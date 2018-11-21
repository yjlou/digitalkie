"""A controller for speaker."""
from machine import Timer

class Speaker(object):

  # For interrupt mode.
  HZ = 2000

  def __init__(self, dac, int_mode=True, debug=False):
    """Constructor.

    Args:
      dac: a DAC object.
      int_mode: True for interrupt mode.
      debug: True for debug mode.
    """
    self.dac_ = dac
    self.debug_ = debug

    self.buf_size_ = self.HZ * 2
    self.buf_ = [0.0] * self.buf_size_
    self.head_ = 0  # Next to pop
    self.tail_ = 0  # Next to push

    self.us_ = int(1000000 / self.HZ)
    if int_mode:
      self.timer_ = Timer.Alarm(self.hz, us=self.us_, periodic=True)

  def enque(self, data):
    """Push data stream to the queue.

    Args:
      data: list of byte.
    """
    if self.debug_:
      delta = max(data) - min(data)
      cols = 40
      volume = int(delta / 255 * cols)
      print('+' * volume + ' ' * (cols - volume) + '\r', end='')
    floats = [x / 255.0 for x in data]

    num = len(data)
    self.buf_[self.tail_:self.tail_+num] = floats
    self.tail_ = (self.tail_ + num) % self.buf_size_

  def hz(self, alarm):
    if self.head_ == self.tail_:
      return
    data = self.buf_[self.head_]
    self.head_ = (self.head_ + 1) % self.buf_size_

    self.dac_.write(data)

  def loop(self):
    self.hz(None)
