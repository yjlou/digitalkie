"""A controller for Microphone."""
from machine import Timer

class Microphone(object):

  HZ = 2000
  FRAME_SIZE = 200  # 200 bytes in a data frame

  def __init__(self, apin, callback):
    """Constructor.

    Args:
      apin: an ADC pin object.
      callback: callback functino when a frame is colelct.
                callback(data) where data is a list of byte.
    """
    self.apin_ = apin
    self.callback_ = callback
    self.stream_ = []
    self.recording_ = False
    self.sampled_ = 0  # For statistic

    us = int(1000000 / self.HZ)
    self.timer_ = Timer.Alarm(self.hz, us=us, periodic=True)
    self.second_ = Timer.Alarm(self.second, s=1, periodic=True)

  def hz(self, alarm):
    if not self.recording_:
      return

    # ADC value is 12-bit.
    self.stream_.append(self.apin_() >> 4)
    self.sampled_ += 1

    if len(self.stream_) >= self.FRAME_SIZE:
      self.flush_frame()

  def second(self, alarm):
    if not self.recording_:
      return
    print('Sampled: {} data.'.format(self.sampled_))
    self.sampled_ = 0

  def flush_frame(self):
    if self.stream_:
      data = bytes([x for x in self.stream_])
      self.stream_ = []
      self.callback_(data)

  def start(self):
    print("Start recording ...")
    self.recording_ = True

  def stop(self):
    print("Stop recording ...")
    self.recording_ = False
    self.sampled_ = 0
    self.flush_frame()
