"""
This file is used for testing
"""

from datetime import datetime
import logging as log

# logging config
log.basicConfig(filename='E:/startups/AtpPredictionBot/logs.txt', level=log.INFO)
# disable schedule's logs
log.getLogger('schedule').setLevel(log.CRITICAL + 10)
cur_time = str(datetime.now())[0:16]


if 3 % 2 == 0:
    print("null")
else:
    print("not null")