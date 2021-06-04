# Simple script for using the AZ-Delivery 1.8" SPI display with the microbit
#
# screen I use has an ST7735S
# (https://www.az-delivery.de/en/products/1-8-zoll-spi-tft-display)
#
# code translated from the Adafruit TFT / ST7735 library

#############################################################################
# I'd love to split this library guff out into a separate file, but mu-editor
# only copies a single file across to the microbit. :/
#############################################################################
from microbit import *

PIN_CS = pin2
PIN_RS = pin0
PIN_RESET = pin1

def initDisplay():
    spi.init(4000000)

    PIN_CS.write_digital(0)
    PIN_RS.write_digital(1)

    resetDisplay()

    # using initG() commands from Arduino code
    # for ST7735S chip
    sendDisplayCommand(0x01) # SWRESET
    sleep(50)
    sendDisplayCommand(0x11) # Sleep Out mode
    sleep(500)
    sendDisplayCommand(0xB1, [0x0b, 0x14])    # set frame rate
    sendDisplayCommand(0xC0, [0x08, 0x00]) # power control command (0x70 = 4.7V ; should be 1Eh=3.25V?)
    sendDisplayCommand(0xC1, [0x05]) # power control 2
    sendDisplayCommand(0xEC, [0x1b]) # pumping color freq
    sendDisplayCommand(0x3A, [0x55]) # colour mode (16 bit)
    sleep(100)
    sendDisplayCommand(0x2A, [0x0, 0x0, 0x0, 0x7f] ) #column address set: 4 1-160
    sendDisplayCommand(0x2b, [0x0, 0x0, 0x0, 0x9f] ) #row address 1-160
    sendDisplayCommand(0x36, [0xC8])    # memory address control (row/col addr, bottom-top refresh)
    sendDisplayCommand(0xB7, [0])  # Set Source Output direction
    sendDisplayCommand(0xF2, [0x0]) # set gamma bit
    sendDisplayCommand(0xE0, [ 0x9, 0x16, 0x9, 0x20,
                        0x21, 0x1B, 0x13, 0x19,
                        0x17, 0x15, 0x1e, 0x2b,
                        0x04, 0x05, 0x02, 0x0e
                    ]
                ) #GMCTRP1
    sleep(50)
    sendDisplayCommand(0xE1, [0x0B, 0x14, 0x08, 0x1E,
                        0x22, 0x1D, 0x18, 0x1E,
                        0x1B, 0x1A, 0x24, 0x2B,
                        0x06, 0x06, 0x02, 0x0F
                    ]
                ) #GMCTRN1
    sleep(50)

    sendDisplayCommand(0x13)
    sleep(10)
    sendDisplayCommand(0x29) # Display on
    sleep(500)

    # set rotation
    sendDisplayCommand(0x36, [0xA8])


def resetDisplay():
    PIN_RESET.write_digital(1)
    sleep(500)
    PIN_RESET.write_digital(0)
    sleep(500)
    PIN_RESET.write_digital(1)
    sleep(500)


def sendDisplayCommand(commandByte, dataBytes=[]):
    sendRawDisplayCommand(commandByte)
    if len(dataBytes) > 0:
        sendDisplayData(dataBytes)


def sendRawDisplayCommand(commandByte):
    PIN_RS.write_digital(0)
    spi.write(bytearray([commandByte]))


def sendDisplayData(dataBytes):
    PIN_RS.write_digital(1)
    spi.write(bytearray(dataBytes))


def fillRect(left, top, right, bottom, colour):
    # clipping
    if left > right:
        left, right = right, left
    if top > bottom:
        top, bottom = bottom, top
    if left < 0:
        width += left
        left = 0
    if top < 0:
        height += top
        top = 0
    if right >= 160:
        right = 159
    if bottom >= 128:
        bottom = 127

    # set column start/end
    LEFT_HI = (left >> 8) & 255
    LEFT_LO = left & 255

    RIGHT_HI = (right >> 8) & 255
    RIGHT_LO = right & 255

    sendDisplayCommand(0x2A, [LEFT_HI, LEFT_LO, RIGHT_HI, RIGHT_LO])

    # set row start/end
    TOP_HI = (top >> 8) & 255
    TOP_LO = top & 255

    BOTTOM_HI = (bottom >> 8) & 255
    BOTTOM_LO = bottom & 255

    sendDisplayCommand(0x2B, [TOP_HI, TOP_LO, BOTTOM_HI, BOTTOM_LO])

    # send pixel data
    # building a list of the pixels first might take too much RAM
    # (only 16kiB in microbit!)
    COLOUR_HI = (colour >> 8) & 255
    COLOUR_LO = colour & 255
    sendRawDisplayCommand(0x2C)
    width = right-left+1
    rowBuffer = bytearray([COLOUR_HI,COLOUR_LO]*width)
    PIN_RS.write_digital(1)
    for _ in range(top,bottom+1):
        spi.write(rowBuffer)




#############################################################################
#
# Actual app code
#
#############################################################################
import random

initDisplay()

fillRect(0, 0, 159, 127, 0x0000)

while True:
    left = random.randint(0, 159)
    right = random.randint(0, 159)
    top = random.randint(0, 127)
    bottom = random.randint(0, 127)

    colour = random.randint(0, 0xffff)

    fillRect(left, top, right, bottom, colour)



