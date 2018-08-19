import sys
sys.path.append("/home/pi/Desktop/NAVI/SPIRIT/GROVE/LOGIKA")
from grove_rgb_lcd import *

import random

try:
    setRGB(0,255,0)

    setText("Hello World")
    time.sleep(2)

    # ascii char 255 is the cursor character
    setRGB(255,255,255)
    setText(chr(255)*32)
    time.sleep(2)



    setRGB(0,255,255)
    setText("ASCII printable and extended")
    time.sleep(2)

    chars = ""
    for a in range(32,256):
        chars += chr(a)
        if len(chars) == 32:
            setText(chars)
            chars = ""
            time.sleep(2)

    setRGB(0,255,0)
    setText("Solid colors")
    time.sleep(2)

    setText("Red")
    setRGB(255,0,0)
    time.sleep(.5)

    setText("Green")
    setRGB(0,255,0)
    time.sleep(.5)

    setText("Blue")
    setRGB(0,0,255)
    time.sleep(.5)

    setText("Yellow")
    setRGB(255,255,0)
    time.sleep(.5)

    setText("Magenta")
    setRGB(255,0,255)
    time.sleep(.5)

    setText("Cyan")
    setRGB(0,255,255)
    time.sleep(.5)

    setText("White")
    setRGB(255,255,255)
    time.sleep(.5)


    setText("Grey")
    setRGB(127,127,127)
    time.sleep(.5)

    setText("Shades of cyan")
    for c in range(0,255):
        setRGB(255-c,255,255)
        time.sleep(.01)


except KeyboardInterrupt:
    setText("KeyboardInterrupt")
    setRGB(255,0,0)
except IOError:
    setText("IOError")
    setRGB(255,0,0)

time.sleep(1)
setText("All done")
setRGB(0,255,0)
