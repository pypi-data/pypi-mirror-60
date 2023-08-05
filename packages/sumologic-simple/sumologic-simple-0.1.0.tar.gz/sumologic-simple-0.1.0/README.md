# Simple Search API for the SumoLogic Python SDK

Install requires `pip` >= 19.

Usage:

```py
from sumologic import SumoLogic
from sumo_simple import SumoLogicSimple
from datetime import timedelta

sumo = SumoLogic(MY_ACCESS_ID, MY_ACCESS_KEY)
simple = SumoLogicSimple(sumo)

fields, messages, aggregates = simple.search('''
    _sourceCategory=nginx/prod
''', startTime=timedelta(minutes=-10)
)

print([message for message in messages])
```

TODO: Publish to PyPI
