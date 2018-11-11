"""Controller for talk button."""
import pycom
from machine import Pin


class TalkButton(object):

  PIN_STR = 'P8'

  def __init__(self, microphone):
    """Constructor.

    Args:
      microphone: an microphone.Microphone object
    """
    self.pin_ = Pin(self.PIN_STR, mode=Pin.IN, pull=Pin.PULL_DOWN)
    self.pin_.callback(IRQ_RISING, self.pressed)
    self.pin_.callback(Pin.IRQ_FALLING, self.released)

    pycom.heartbeat(False)  # RGB LED

    self.microphone_ = microphone

  def pressed(self):
    pycom.rgbled(0x7f0000)  # red
    self.microphone_.start()

  def released(self):
    pycom.rgbled(0x000000)  # off
    self.microphone_.stop()
