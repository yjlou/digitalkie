from machine import ADC
from machine import DAC
from machine import Timer

import lora
import microphone
import speaker
import talk_button

def frame_received(data):
  print('.')
  lora_ctl.send(data)

lora_ctl = lora.LoRaController()
spk = speaker.Speaker(DAC('P22'))
adc = machine.ADC() 
apin = adc.channel(pin='P13')
uphone = microphone.Microphone(apin, frame_received)
tlk_btn = talk_button.TalkButton(uphone)

while True:
  Timer.sleep_us(10000)
  data = lora_ctl.recv()
  if data:
    spk.enque(data)
