"""A controller for Microphone."""
from machine import Timer

class Microphone(object):

  HZ = 8000
  FRAME_SIZE = 100  # 100 bytes in a data frame

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

    us = int(1000000 / self.HZ)
    self.timer_ = Timer.Alarm(self.hz, us=us, periodic=True)

  def hz(self, alarm):
    if not self.recording_:
      return

    # ADC value is 12-bit.
    self.stream_.append(self.apin_() >> 4)

    if len(self.stream_) >= self.FRAME_SIZE:
      self.flush_frame()

  def flush_frame(self):
    if self.stream_:
      data = bytes([x for x in self.stream_])
      self.callback_(data)
      self.stream_ = []

  def start(self):
    print("Start recording ...")
    self.recording_ = True

  def stop(self):
    print("Stop recording ...")
    self.recording_ = False
    self.flush_frame()
