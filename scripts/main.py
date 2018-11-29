from machine import ADC
from machine import Timer
from machine import DAC
import math
import pycom
import uos

import lora
import microphone
import speaker
import talk_button

def randint(a, b):
  """Returns a random integer bet a and b (not included).

  Args:
    a: starting integer
    b: ending integer (not included)

  Returns:
    int
  """
  assert(b > a)
  r = (b - a)  # range
  bits = math.ceil(math.log(r) / math.log(2)) + 7 + 8  # 8 more bits to make posibility more even.
  num_bytes = int(bits / 8)
  random_bytes = uos.urandom(num_bytes)
  s = 0  # sum
  for b in random_bytes:
    s = s * 256 + b
  result = (s % r) + a
  return result

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

  RECV_WINDOW = 20   # Used to count how many packets were received in the past.
  WAIT_RSP_MS = 200  # Timeout before receive the response
  NEXT_TRY_MIN = 1000  # Min timeout for next try
  NEXT_TRY_MAX = 2000  # Min timeout for next try

  statistics = [0] * RECV_WINDOW

  cnt = 0
  while True:
    print('=============================================')
    # Send 10 packets
    # flash(0x000010)  # dark blue

    data = 'ECHO_REQ{}'.format(cnt)
    lora_ctl.send(data)

    # Collect response in 200ms
    received = 0
    timer = Timer.Chrono()
    timer.start()
    while timer.read_ms() < WAIT_RSP_MS:
      recv = lora_ctl.recv()
      if recv and recv.startswith('ECHO_RSP'):
        print('[{}] Recv RSP in {} ms'.format(cnt, timer.read_ms()))
        received = 1
        break
    cnt += 1

    statistics = statistics[1:] + [received]

    total_recv = sum(statistics)
    percent = total_recv / RECV_WINDOW
    print('Recv: {}  Percent: {:3d}%'.format(total_recv, int(percent * 100)))
    print('---------------------------------------------')
    if percent >= 0.8:
      flash(0x007f00)  # green
    elif percent >= 0.4:
      flash(0x3f1f00)  # yellow
    else:
      flash(0x7f0000)  # red

    # Now become a responder until timeout.
    timeout = randint(NEXT_TRY_MIN, NEXT_TRY_MAX)
    print('In response mode until next timeout: {} ms'.format(timeout))
    while timer.read_ms() < timeout:
      recv = lora_ctl.recv()
      if recv and recv.startswith('ECHO_REQ'):
        print('Got echo request: {}'.format(recv))
        send_back = bytes('ECHO_RSP', 'utf-8') + recv[8:]
        lora_ctl.send(send_back)

def audio_loopback():
  def handle_audio(data):
    spk.enque(data)

  int_mode = False
  spk = speaker.Speaker(DAC('P22'), int_mode=int_mode, debug=False)
  adc = ADC()
  apin = adc.channel(pin='P13', attn=ADC.ATTN_11DB)
  uphone = microphone.Microphone(apin, handle_audio, int_mode=int_mode)
  tlk_btn = talk_button.TalkButton(uphone)

  print('Audio playpack ...')
  flash(0x000010)  # Dark blue

  while True:
    if int_mode:
      Timer.sleep_us(1000000)
    else:
      uphone.loop()
      spk.loop()

def main():
  pkt_tx_queue = []

  def audio_frame_ready(data):
      pkt_tx_queue.append(data)

  lora_ctl = lora.LoRaController()
  spk = speaker.Speaker(DAC('P22'))
  adc = ADC()
  apin = adc.channel(pin='P13', attn=ADC.ATTN_11DB)
  uphone = microphone.Microphone(apin, audio_frame_ready)
  tlk_btn = talk_button.TalkButton(uphone)

  print('Started ...')
  flash(0x007f00)  # green

  while True:
    Timer.sleep_us(1000)

    # Handle the RX packets
    # TODO: refactor to use callback mechanism.
    while True:
      data = lora_ctl.recv()
      if data:
        spk.enque(data)
      else:
        break

    # Handle the TX queue
    # TODO: refactor to use Python synchronized Queue.
    while pkt_tx_queue:
      data = pkt_tx_queue.pop(0)
      print('.')
      lora_ctl.send(data)

lora_echo()
# audio_loopback()
# main()
