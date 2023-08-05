import selectors
import sys
import threading


class Ticker:
    """
    Simple ticker for Linux.
    The max resolution it supports is 1 milliseconds.
    """
    def __init__(self, interval: float):
        """
        Initialise a ticker. The minimum interval is 1 millisecond.
        :param interval: time to sleep in second
        """
        if sys.platform != 'linux':
            raise NotImplementedError(
                "only linux is currently supported")
        self.selector = selectors.DefaultSelector()
        self.interval = interval

    def __selector_timeout(self) -> list:
        return self.selector.select(timeout=self.interval)

    def tick(self) -> bool:
        """
        Run the ticker using the internal selector with timeout.
        :return: True if the ticker has timed-out
        """
        if len(self.__selector_timeout()) == 0:
            return True
        return False

    def stop(self):
        """
        Close the ticker using the internal selector.
        :return: None
        """
        self.selector.close()

    def __repr__(self) -> str:
        return str(self.interval)


class RepeatedTicker:
    """
    RepeatedTicker provides a simple repeated ticker on Linux.
    It provides a `tickback` method to run a method every tick.
    The max resolution it supports is 1 milliseconds.
    """
    def __init__(self, interval: float, count: int):
        """
        Initialise a new `RepeatTicker`.
        No timer is created until `tickback` method is invoked.
        :param interval: time to sleep in second
        :param count: the number of times to repeat a `tickback`
        """
        self.tickers = []
        self.interval = interval
        self.count = count
        self.__repeated_ticker = self

    def __init_tickers(self):
        """
        Initialise the underlying tickers as threads.
        :return: None
        """
        for _ in range(self.count):
            t = Ticker(interval=self.interval)
            self.tickers.append(threading.Thread(target=t.tick, daemon=True))

    def tickback(self, f, args):
        """
        Callback method for tickers.
        Repeat a ticker every `self.interval` seconds for `self.count`
        many times.
        :param f: the callback function
        :param args: the callback function's arguments (tuple)
        :return: None
        """
        if self.__repeated_ticker:
            self.__init_tickers()
        for ticker_thread in self.tickers:
            ticker_thread.start()
        for ticker_thread in self.tickers:
            ticker_thread.join()
            if f and len(args) > 0:
                f(args)
        self.tickers = []


def main():
    def hello(interval):
        print(f'hello() woke after {interval[0]}s')

    # Repeat the ticker every 0.002 seconds for 2 times
    repeated_ticker = RepeatedTicker(interval=0.002, count=2)
    repeated_ticker.tickback(hello, args=(repeated_ticker.interval,))
    # Execute lambda
    repeated_ticker.tickback(lambda x: print(f'lambda woke after {x[0]}s'),
                             args=(repeated_ticker.interval,))
    # No tickback; only ticks
    repeated_ticker.tickback(None, args=())
    # Repeat the ticker every 0.01 second
    simple_ticker = Ticker(interval=0.01)
    try:
        while simple_ticker.tick():
            print(f'simple ticker woke after {simple_ticker}s')
    finally:
        simple_ticker.stop()


if __name__ == "__main__":
    sys.exit(main())
