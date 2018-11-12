"""Controller for talk button."""
import pycom
from machine import Pin
from machine import Timer


class TalkButton(object):

  PIN_STR = 'P8'

  def __init__(self, microphone):
    """Constructor.

    Args:
      microphone: an microphone.Microphone object
    """
    self.pin_ = Pin(self.PIN_STR, mode=Pin.IN, pull=Pin.PULL_DOWN)
    self.pin_.callback(Pin.IRQ_RISING | Pin.IRQ_FALLING, self.toggled)

    pycom.heartbeat(False)  # RGB LED

    self.microphone_ = microphone
    self.pressed_ = False

  def pressed(self):
    if self.pressed_:
      return

    Timer.sleep_us(100000)  # debounce
    if not self.pin_():
      return

    self.pressed_ = True
    pycom.rgbled(0x7f0000)  # red
    self.microphone_.start()
    print("Pressed ...")

  def released(self):
    if not self.pressed_:
      return

    Timer.sleep_us(100000)  # debounce
    if self.pin_():
      return

    self.pressed_ = False
    pycom.rgbled(0x000000)  # off
    self.microphone_.stop()
    print("Released ...")

  def toggled(self, arg):
    if self.pin_():
      self.pressed()
    else:
      self.released()
