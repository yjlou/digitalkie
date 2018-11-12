"""Controller for talk button."""
import pycom
from machine import Pin
from machine import Timer

class TalkButton(object):

  PIN_STR = 'P8'
  DEBOUNCE_US = 10000  # 10ms

  RELEASED = 0
  PRESSING = 1
  PRESSED = 2
  RELEASING = 3

  def __init__(self, microphone):
    """Constructor.

    Args:
      microphone: an microphone.Microphone object
    """
    self.microphone_ = microphone
    self.pressed_ = False
    self.state_ = self.RELEASED
    self.cnt_ = None  # For debounce

    pycom.heartbeat(False)  # RGB LED
    self.pin_ = Pin(self.PIN_STR, mode=Pin.IN, pull=Pin.PULL_DOWN)
    self.timer_ = Timer.Alarm(self.timer, us=self.DEBOUNCE_US, periodic=True)

  def pressed(self):
    self.pressed_ = True
    pycom.rgbled(0x7f0000)  # red
    self.microphone_.start()
    print("Pressed ...")

  def released(self):
    self.pressed_ = False
    self.microphone_.stop()
    pycom.rgbled(0x000000)  # off
    print("Released ...")

  def timer(self, alarm):
    high = self.pin_()
    if self.state_ is self.RELEASED:
      if high:
        self.cnt_ = 0
        self.state_ = self.PRESSING

    elif self.state_ is self.PRESSING:
      if high:
        self.cnt_ += 1
        if self.cnt_ >= 10:  # 100ms
          self.state_ = self.PRESSED
          self.pressed()
      else:
        self.cnt_ = 0
        self.state_ = self.RELEASED

    elif self.state_ is self.PRESSED:
      if not high:
        self.cnt_ = 0
        self.state_ = self.RELEASING

    elif self.state_ is self.RELEASING:
      if not high:
        self.cnt_ += 1
        if self.cnt_ >= 10:  # 100ms
          self.state_ = self.RELEASED
          self.released()
      else:
        self.cnt_ = 0
        self.state_ = self.PRESSED
