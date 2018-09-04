# PyAlgoTrade
#
# Copyright 2011-2018 Gabriel Martin Becedillas Ruiz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>
"""

import datetime

from pyalgotrade import bar
from pyalgotrade import barfeed
from pyalgotrade import dataseries
from pyalgotrade.coinbase import common
from pyalgotrade.coinbase import messages


class TradeBar(bar.Bar):
    def __init__(self, matchMsg):
        self.__matchMsg = matchMsg
        self.__dateTime = matchMsg.getTime()
        self.__price = matchMsg.getPrice()
        self.__amount = matchMsg.getSize()

    def getMatchMsg(self):
        return self.__matchMsg

    def setUseAdjustedValue(self, useAdjusted):
        assert not useAdjusted, "Adjusted values not supported"

    def getFrequency(self):
        return bar.Frequency.TRADE

    def getDateTime(self):
        return self.__dateTime

    def getOpen(self, adjusted=False):
        assert not adjusted, "Adjusted values not supported"
        return self.__price

    def getHigh(self, adjusted=False):
        assert not adjusted, "Adjusted values not supported"
        return self.__price

    def getLow(self, adjusted=False):
        assert not adjusted, "Adjusted values not supported"
        return self.__price

    def getClose(self, adjusted=False):
        assert not adjusted, "Adjusted values not supported"
        return self.__price

    def getVolume(self):
        return self.__amount

    def getAdjClose(self):
        return None

    def getTypicalPrice(self):
        return self.__price

    def getPrice(self):
        return self.__price

    def getUseAdjValue(self):
        return False


class LiveTradeFeed(barfeed.BaseBarFeed):

    """A real-time BarFeed that builds bars from live trades.

    :param coinbaseClient: A Coinbase client.
    :type coinbaseClient: pyalgotrade.coinbase.client.Client.
    :param maxLen: The maximum number of values that the :class:`pyalgotrade.dataseries.bards.BarDataSeries`
        will hold.
        Once a bounded length is full, when new items are added, a corresponding number of items are discarded
        from the opposite end.
    :type maxLen: int.

    .. note::
        Note that a Bar will be created for every trade, so open, high, low and close values will all be the same.
    """

    def __init__(self, coinbaseClient, maxLen=dataseries.DEFAULT_MAX_LEN):
        assert isinstance(maxLen, int)

        super(LiveTradeFeed, self).__init__(bar.Frequency.TRADE, maxLen)
        self.__barQueue = []
        self.registerInstrument(common.btc_usd_product_id)
        self.__stopped = False
        self.__coinbaseClient = coinbaseClient
        coinbaseClient.getOrderEvents().subscribe(self.__onOrderEvent)

    def __onOrderEvent(self, orderEvent):
        if isinstance(orderEvent, messages.Match):
            self.__barQueue.append(TradeBar(orderEvent))

    def getCurrentDateTime(self):
        return datetime.datetime.now()

    def barsHaveAdjClose(self):
        return False

    def getNextBars(self):
        ret = None
        if len(self.__barQueue):
            ret = bar.Bars({common.btc_usd_product_id: self.__barQueue.pop(0)})
        return ret

    def peekDateTime(self):
        # Return None since this is a realtime subject.
        return None

    def onDispatcherRegistered(self, dispatcher):
        # Ensure that the client registered.
        dispatcher.addSubject(self.__coinbaseClient)

    def start(self):
        pass

    # This should not raise.
    def stop(self):
        self.__stopped = True

    # This should not raise.
    def join(self):
        pass

    def eof(self):
        return self.__stopped
