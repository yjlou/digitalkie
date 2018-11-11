"""A controller for speaker."""
from machine import Timer

class Speaker(object):

  HZ = 8000

  def __init__(self, dac):
    """Constructor.

    Args:
      dac: a DAC object.
    """
    self.dac_ = dac
    self.stream_ = []

    us = 1000000 / self.HZ
    self.timer_ = Timer.Alarm(self.hz, us=us, periodic=True)

  def enque(self, data):
    """Push data stream to the queue.

    Args:
      data: list of byte.
    """
    print('+')
    floats = [x / 255.0 for x in data]
    self.stream_.extend(floats)

  def hz(self):
    if self.stream_:
      data = self.stream_.pop(0)
      self.dac_.write(data)
