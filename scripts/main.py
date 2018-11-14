import pycom
from machine import ADC
from machine import DAC
from machine import Timer

import lora
import microphone
import speaker
import talk_button

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
  pycom.rgbled(0x007f00)  # green
  Timer.sleep_us(100000)
  pycom.rgbled(0x000000)  # off

  while True:
    Timer.sleep_us(1000)
    while True:
      data = lora_ctl.recv()
      if data:
        spk.enque(data)
    else:
        break

main()
