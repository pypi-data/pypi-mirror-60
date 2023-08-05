
Simple ticker for use on linux platform. Maximum tick resolution is
1 millisecond.

Install using pip:

.. code:: bash

   pip install linux-ticker

Simple use shown below:

.. code:: python

   from linux_ticker import Ticker, RepeatedTicker

   def hello(interval):
       print(f'hello() woke after {interval[0]}s')

Repeat the ticker every 0.002 seconds for 2 times:

.. code:: python

   repeated_ticker = RepeatedTicker(interval=0.002, count=2)
   repeated_ticker.tickback(hello, args=(repeated_ticker.interval,))

Execute lambda:

.. code:: python

   repeated_ticker.tickback(lambda x: print(f'lambda woke after {x[0]}s'), args=(repeated_ticker.interval,))

No tickback - only ticks:

.. code:: python

   repeated_ticker.tickback(None, args=())

Repeat the ticker every 0.01 second

.. code:: python

   simple_ticker = Ticker(interval=0.01)
   try:
       while simple_ticker.tick():
           print(f'simple ticker woke after {simple_ticker}s')
   finally:
       simple_ticker.stop()
