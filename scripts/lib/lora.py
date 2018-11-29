from machine import Timer
from network import LoRa
import socket
import machine
import time

class LoRaController(object):

  MRU = 255  # MTU is 255 bytes.

  def __init__(self, debug=False):
    """Constructor."""
    self.debug_ = debug

    self.lora_ = LoRa(mode=LoRa.LORA,
                      region=LoRa.US915,
                      power_mode=LoRa.ALWAYS_ON,
                      tx_power=20,  # 5~20
                      bandwidth=LoRa.BW_500KHZ)

    # create a raw LoRa socket
    self.sock_ = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

    self.sent_in_second_ = 0  # number of packet sent in this second
    self.second_ = Timer.Alarm(self.second, s=1, periodic=True)

    # To count how long will we take to send out a packet.
    self.chrono_ = Timer.Chrono()

  def second(self, alarm):
    if not self.sent_in_second_:
      return
    if self.debug_:
      print('#packet sent: {}.'.format(self.sent_in_second_))
    self.sent_in_second_ = 0

  def send(self, data):
    """Send out data.

    Args:
      data: bytes.
    """
    self.sock_.setblocking(True)
    self.chrono_.reset()
    self.chrono_.start()
    self.sock_.send(data)
    if self.debug_:
      print('Sent took {} ms'.format(self.chrono_.read_ms()))
    self.sent_in_second_ += 1

  def recv(self):
    """Receive data.

    This is non-blocking call.

    Returns:
    bytes if a data is received.
    0 byte of data will be returned if no data is received.
    """
    self.sock_.setblocking(False)
    return self.sock_.recv(self.MRU)
