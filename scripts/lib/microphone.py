"""A controller for Microphone."""
from machine import Timer

class Microphone(object):

  # Used in interrupt mode
  HZ = 2000

  FRAME_SIZE = 200  # MTU is 255 bytes.

  def __init__(self, apin, callback, int_mode=True):
    """Constructor.

    Args:
      apin: an ADC pin object.
      callback: callback functino when a frame is colelct.
                callback(data) where data is a list of byte.
      int_mode: True for interrupt mode.
    """
    self.apin_ = apin
    self.callback_ = callback
    self.stream_ = [0] * self.FRAME_SIZE
    self.num_samples_ = 0  # Number of data in stream_[]
    self.recording_ = False
    self.samples_in_sec_ = 0  # For statistic

    us = int(1000000 / self.HZ)
    if int_mode:
      self.timer_ = Timer.Alarm(self.hz, us=us, periodic=True)
    self.second_ = Timer.Alarm(self.second, s=1, periodic=True)

  def hz(self, alarm):
    if not self.recording_:
      return

    # ADC value is 12-bit.
    self.stream_[self.num_samples_] = self.apin_() >> 4
    self.num_samples_ += 1
    self.samples_in_sec_ += 1

    if self.num_samples_ >= self.FRAME_SIZE:
      self.flush_frame()

  def second(self, alarm):
    if not self.recording_:
      return
    print('Sampled: {} data.'.format(self.samples_in_sec_))
    self.samples_in_sec_ = 0

  def flush_frame(self):
    if self.num_samples_:
      data = bytes([x for x in self.stream_])  # Convert to bytes array for sending
      self.num_samples_ = 0
      self.callback_(data)

  def start(self):
    print("Start recording ...")
    self.recording_ = True

  def stop(self):
    print("Stop recording ...")
    self.recording_ = False
    self.samples_in_sec_ = 0
    self.flush_frame()

  def loop(self):
    self.hz(None)
