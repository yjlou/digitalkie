import pycom
from machine import ADC
from machine import DAC
from machine import Timer

import lora
import microphone
import speaker
import talk_button

def flash(color, delay_us=100000):
  """Generate a 100ms of flash on RGB LED.

  Args:
    color: int
  """
  pycom.heartbeat(False)
  pycom.rgbled(color)
  Timer.sleep_us(delay_us)
  pycom.rgbled(0x000000)  # off

def lora_echo():
  lora_ctl = lora.LoRaController()

  print('LoRa Echo ...')
  flash(0x7f007f)  # Purple

  while True:
    # Send 10 packets
    flash(0x000010)  # dark blue
    TOTAL_SEND = 10
    for i in range(TOTAL_SEND):
      data = 'ECHO_REQ{}'.format(i)
      lora_ctl.send(data)

    # Collect response in one second.
    timer = Timer.Chrono()
    timer.start()
    collected = []
    while timer.read_ms() < 1000:
      recv = lora_ctl.recv()
      if recv and recv.startswith('ECHO_RSP'):
        collected.append(recv)

    percent = len(collected) / TOTAL_SEND
    print('Send: {}  Recv: {}  Percent: {:3d}%'.format(
          TOTAL_SEND, len(collected), int(percent * 100)))
    if percent >= 0.7:
      flash(0x007f00)  # green
    elif percent >= 0.4:
      flash(0x7f7f00)  # yellow
    else:
      flash(0x7f0000)  # red

    # Now become a responder (until fifth second)
    while timer.read_ms() < 5000:
      recv = lora_ctl.recv()
      if recv and recv.startswith('ECHO_REQ'):
        send_back = bytes('ECHO_RSP', 'utf-8') + recv[8:]
        lora_ctl.send(send_back)

def audio_loopback():
  def audio_buffer(data):
      spk.enque(data)

  spk = speaker.Speaker(DAC('P22'))
  adc = ADC()
  apin = adc.channel(pin='P13')
  uphone = microphone.Microphone(apin, audio_buffer)
  tlk_btn = talk_button.TalkButton(uphone)

  print('Audio playpack ...')
  flash(0x000010)  # Dark blue

  while True:
    Timer.sleep_us(1000000)


def main():
  def audio_buffer(data):
      print('.')
      lora_ctl.send(data)

  lora_ctl = lora.LoRaController()
  spk = speaker.Speaker(DAC('P22'))
  adc = ADC()
  apin = adc.channel(pin='P13')
  uphone = microphone.Microphone(apin, audio_buffer)
  tlk_btn = talk_button.TalkButton(uphone)

  print('Started ...')
  flash(0x007f00)  # green

  while True:
    Timer.sleep_us(1000)
    while True:
      data = lora_ctl.recv()
      if data:
        spk.enque(data)
    else:
        break

# lora_echo()
# audio_loopback()
main()
