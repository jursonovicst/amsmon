import time

import framebuf
from machine import Pin, I2C, ADC, lightsleep

from picodht22 import PicoDHT22
from sh1106 import sh1106

# 32x32 icon pixel array
humid = bytearray([
    0x00, 0x00, 0x00, 0x00, 0x07, 0xC0, 0x00, 0x00, 0x07, 0xE0, 0x00, 0x18, 0x04, 0x20, 0x00, 0x18,
    0x04, 0x38, 0x00, 0x3C, 0x04, 0x20, 0x00, 0x24, 0x04, 0x30, 0x00, 0x66, 0x04, 0x30, 0x00, 0x24,
    0x04, 0x20, 0x00, 0x3C, 0x05, 0xB8, 0x00, 0x00, 0x05, 0xA0, 0x06, 0x00, 0x05, 0xA0, 0x0E, 0x00,
    0x05, 0xB0, 0x0B, 0x00, 0x05, 0xA0, 0x19, 0x00, 0x05, 0xB8, 0x11, 0x80, 0x05, 0xA0, 0x11, 0x80,
    0x05, 0xA0, 0x1B, 0x00, 0x0D, 0xA0, 0x0E, 0x00, 0x19, 0xB8, 0x00, 0x18, 0x31, 0x8C, 0x00, 0x18,
    0x21, 0x84, 0x00, 0x24, 0x67, 0xC6, 0x00, 0x66, 0x47, 0xE2, 0x00, 0x42, 0x47, 0xE2, 0x00, 0x42,
    0x47, 0xE2, 0x00, 0x42, 0x47, 0xC6, 0x00, 0x7E, 0x61, 0x84, 0x00, 0x18, 0x30, 0x0C, 0x00, 0x00,
    0x18, 0x18, 0x00, 0x00, 0x0F, 0xF0, 0x00, 0x00, 0x01, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
])

cpu = bytearray([
    0b00000000,0b00000000,
    0b00010010,0b01001000,
    0b00111111,0b11111100,
    0b01100000,0b00000110,
    0b00100000,0b00000100,
    0b00100000,0b00000100,
    0b01100000,0b00000110,
    0b00100000,0b00000100,
    0b00100000,0b00000100,
    0b01100000,0b00000110,
    0b00100000,0b00000100,
    0b00100000,0b00000100,
    0b01100000,0b00000110,
    0b00111111,0b11111100,
    0b00010010,0b01001000,
    0b00000000,0b00000000
])

assert len(humid) == 32*32/8, f"{len(humid)}"

def draw_ams(dht22: PicoDHT22, disp: sh1106.SH1106, led: Pin):
    # flash led during IO
    led.on()
    t, h = dht22.read()
    led.off()

    # print
    disp.fill_rect(40, 0, 128 - 40, 40, 0)
    disp.text(f"{t:4.1f}C" if t is not None else "--", 40, 10)
    disp.text(f"{int(h):2d}%" if h is not None else "--%", 40, 20)


def draw_rpi(adc: ADC, disp: sh1106.SH1106):
    volt = (3.3 / 65535) * adc.read_u16()
    temperature = 27 - (volt - 0.706) / 0.001721

    # print
    disp.fill_rect(22, 43, 128-20, 13, 0)
    disp.text(f"{temperature:2.0f}C", 22, 48)



# DHT22 sensor
dht22 = PicoDHT22.PicoDHT22(Pin(22, Pin.IN, Pin.PULL_UP))

# IIC OLED CH1116G display
i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=400000)
print(f"I2C scan: {i2c.scan()}")
display = sh1106.SH1106_I2C(128, 64, i2c, None, 0x3c)
display.sleep(False)
display.fill(0)

# print icon
fb = framebuf.FrameBuffer(humid, 32, 32, framebuf.MONO_HLSB)
display.blit(fb, 4, 4)

# RPi pico temp sensor
sensor = ADC(4)

# print icon
fb = framebuf.FrameBuffer(cpu, 16, 16, framebuf.MONO_HLSB)
display.blit(fb, 2, 43)


# led
led = Pin("LED", Pin.OUT)

i = 1
d = 1
while True:
    # scrolling led
    display.pixel(i, 60, 0)

    if i % 5 == 0:
        draw_ams(dht22, display, led)
        draw_rpi(sensor, display)

    if i == 0 or i == 127:
        d *= -1
    i += d
    display.pixel(i, 60, 1)

    display.show()
    time.sleep_ms(200)
