from datetime import datetime, timezone, timedelta
from dateutil import tz
from enum import Enum
from time import sleep
from abc import ABC, abstractmethod
from typing import *
import logging
import atexit
import math
if TYPE_CHECKING:
    from .sumologic import SumoLogic

__all__ = [
    'SumoLogicSimple'
]

def _sumoTime(date = None):
    date = date or datetime.now(timezone.utc)
    return int(date.timestamp()*1000)

class State(Enum):
    DONE = 'DONE GATHERING RESULTS'
    GATHERING = 'GATHERING RESULTS'

states = { i.value for i in State }


class _ResultGenerator:

    MAX_PER_REQ = 100000
    MIN_PER_REQ = 10
    delay = 1

    def __init__(self, sumoSimple, searchJob: dict, startTime: datetime, endTime: datetime):
        """
        :type sumoSimple: SumoLogicSimple
        """
        self.client = sumoSimple.client
        self.yielded = 0
        self.searchJob = searchJob
        self.startTime = startTime
        self.endTime = endTime
        self.lastCountLogged = 0
        self.logger = sumoSimple.logger.getChild(self.__class__.__name__)
        self.buckets: Dict[str, dict] = {}

    @abstractmethod
    def getListOfRecords(self) -> list:
        pass

    @abstractmethod
    def getCountFromStatus(self, status: dict) -> int:
        pass

    def _yield_next_n(self, n: int, yieldUntil: int):
        while self.yielded < yieldUntil:
            records = self.getListOfRecords()
            numMessages = len(records)
            self.yielded += numMessages
            yield from (m['map'] for m in records)

    def _yield_from_status(self, status: dict):
        count = self.getCountFromStatus(status)
        state = State(status['state'])
        n_waiting = count - self.yielded

        if (state == State.DONE or (state == State.GATHERING and n_waiting > self.MIN_PER_REQ)):
            yield from self._yield_next_n(self.MAX_PER_REQ, count)

        more_waiting = (n_waiting > self.MAX_PER_REQ)
        self.logger.debug(f"{n_waiting} waiting and <={self.MAX_PER_REQ} returned, so more_waiting = {more_waiting}")
        return more_waiting

    def _render_buckets(self, buckets: List[dict]):
        if len(buckets) < 1:
            return
        bucketLength = buckets[-1]['length']
        mySpan: timedelta = self.endTime - self.startTime
        while buckets[0]['startTimestamp'] > self.startTime.timestamp()*1000:
            buckets.insert(0, {
                'count': 0,
                'length': bucketLength,
                'startTimestamp': buckets[0]['startTimestamp'] - bucketLength
            })
        maxBucketCount = max(b['count'] for b in buckets)
        blocks = '_▁▂▃▄▅▆▇█'
        bucketBlocks = [
            blocks[math.floor(b['count']/maxBucketCount * (len(blocks)-1))]
            for b in buckets
        ]
        return f'[{"".join(bucketBlocks)}]'

    def _log_progress(self, status: dict):

        self.buckets.update({b['startTimestamp']: b for b in status['histogramBuckets']})
        buckets = sorted(self.buckets.values(), key=lambda b: b['startTimestamp'])
        if len(buckets) < 1:
            return

        averageCountPerMs = sum(b['count'] for b in buckets)/sum(b['length'] for b in buckets)
        earliestKindaFullBucket = next(b for b in buckets if b['count']/b['length'] >= averageCountPerMs/2)
        earliestRetrieved = datetime.fromtimestamp(earliestKindaFullBucket['startTimestamp']/1000, tz=timezone.utc)
        retrievedSpan = self.endTime - earliestRetrieved
        mySpan = self.endTime - self.startTime
        proportionSearched = round(retrievedSpan/mySpan, 2)
        countLogged = sum(b['count'] for b in buckets)

        if self.lastCountLogged < countLogged:
            percentageSearched = proportionSearched * 100
            self.logger.info(f"{self._render_buckets(buckets)} - {percentageSearched:.1f}% of search timespan searched, {status['messageCount']} messages and {status['recordCount']} aggregate records found.")
        self.lastCountLogged = countLogged

    def _log_errors(self, status: dict):
        for error in status['pendingErrors']:
            self.logger.error(f'Received error from Sumo: {error}')
        for warning in status['pendingWarnings']:
            self.logger.warning(f'Received warning from Sumo: {warning}')

    def yield_all(self):
        while True:
            status = self.client.search_job_status(self.searchJob)
            # broken, API returns crap
            self._log_progress(status)
            self._log_errors(status)
            self.logger.debug(f"{self.getCountFromStatus(status)} collected by Sumo")
            more_waiting = yield from self._yield_from_status(status)

            state = State(status['state'])
            if state == State.DONE:
                assert self.yielded == self.getCountFromStatus(status)
                break
            if not more_waiting:
                self.logger.debug("No more records waiting, sleeping...")
                sleep(self.delay)

class _MessagesGenerator(_ResultGenerator):
    def getListOfRecords(self):
        self.logger.debug(f'Asking Sumo for <= {self.MAX_PER_REQ} messages...')
        messages = self.client.search_job_messages(self.searchJob, limit=self.MAX_PER_REQ, offset=self.yielded)['messages']
        self.logger.debug(f'...retrieved {len(messages)}.')
        return messages
    def getCountFromStatus(self, status):
        return status['messageCount']

class _RecordsGenerator(_ResultGenerator):
    def getListOfRecords(self):
        return self.client.search_job_records(self.searchJob, limit=self.MAX_PER_REQ, offset=self.yielded)['records']
    def getCountFromStatus(self, status):
        return status['recordCount']

class SumoLogicSimple:

    searches: List[Tuple['SumoLogic', dict]] = []

    def __init__(self, sumo: 'SumoLogic'):
        """
        Initialize the Simple SumoLogic API.
        """
        self.client = sumo
        self.logger: logging.Logger = logging.getLogger(SumoLogicSimple.__name__)

    @staticmethod
    def _getTime(t: Union[datetime, timedelta, None]) -> datetime:
        if isinstance(t, datetime):
            return t.astimezone(timezone.utc)
        elif t is None:
            return datetime.now(timezone.utc)
        elif isinstance(t, timedelta):
            return datetime.now(timezone.utc) + t

    def search(self, query, startTime: Union[datetime, timedelta, None], endTime: Union[datetime, timedelta, None] = None, timeZone='UTC') -> Tuple[dict, Iterable[dict], Iterable[dict]]:
        """
        Search Sumo with a given query, and return a streaming iterable of results.

        :type query: str
        :type startTime: Union[datetime, timedelta]
        :type endTime: Union[datetime, timedelta]

        :return Tuple of (fields, messages, records).
        :rtype: Tuple[dict, Iterable[dict], Iterable[dict]]
        """
        MAX_PER_REQ = 100000
        MIN_PER_REQ = 10

        messages_yielded = 0
        records_yielded = 0

        startTime = self._getTime(startTime)
        endTime = self._getTime(endTime)

        sj = self.client.search_job(query, _sumoTime(startTime), _sumoTime(endTime), timeZone=timeZone, byReceiptTime=False)
        self.searches.append((self.client, sj))
        from pprint import pprint
        pprint(sj)
        firstResponse = self.client.search_job_messages(sj, limit=1)
        fields = firstResponse['fields']

        messagesGenerator = _MessagesGenerator(self, sj, startTime, endTime)
        recordsGenerator = _RecordsGenerator(self, sj, startTime, endTime)

        sleep(0.1)

        return (fields, messagesGenerator.yield_all(), recordsGenerator.yield_all())

    @classmethod
    def _cleanup(Class):
        print('cleaning up')
        for client, sj in Class.searches:
            client.delete_search_job(sj)

atexit.register(SumoLogicSimple._cleanup)
