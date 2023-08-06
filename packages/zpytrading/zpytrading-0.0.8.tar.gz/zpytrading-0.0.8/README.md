# zpytrading

Python - Zinnion SDK

https://pypi.org/project/zpytrading/

`pip3 install --upgrade --force-reinstall --no-cache-dir zpytrading`

### Requirements

You need to download and export the path to `libztrading.so` https://github.com/Zinnion/zpytrading/wiki

### Example

```Python

import zpytrading
import json
import pandas
import time


def handle_data(self, data):
    print(data)


def init():
    pandas.set_option('display.max_colwidth', -1)
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MTA5MzM5MTMsImlhdCI6MTU3OTM5NzkxMywiaXNzIjoic3F1aXJyZWwiLCJ1c2VyX2lkIjoiYjU2NjdlY2UtNTc4Zi00YjQxLTgzNjAtNTk2MTk1MDEwNmNkIn0.tU3-57y14fg3KPBB-w6Iz8cw92o74HFBhvYcXKJ_p44"
    account = "fa237b32-d580-42db-aeb9-b09a1d90067e"
    zTrading = zpytrading.ZinnionAPI(token, account)
    streamingr_config = '{"subscriptions": [ "COINBASEPRO:BTC-USD"], "channels": [1] }'
    zTrading.add_streaming(streamingr_config)

    indicator_config = '{"indicator": "sma", "options": [3], "data_in": ["close"], "candle_type": "ha", "timeframe": 1, "max_candles": 60}'
    zTrading.add_indicator(indicator_config)

    # indicator_config = '{"indicator": "rsi", "options": [5], "data_in": ["close"], "candle_type": "ha", "timeframe": 1, "max_candles": 60}'
    # zTrading.add_indicator(indicator_config)

    # indicator_config = '{"indicator": "mass", "options": [5], "data_in": ["high","low"], "candle_type": "ha", "timeframe": 1, "max_candles": 60}'
    # zTrading.add_indicator(indicator_config)

    zTrading.start_streaming(handle_data)


if __name__ == "__main__":
    init()


```
