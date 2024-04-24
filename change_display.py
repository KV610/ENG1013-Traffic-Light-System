# ADD FILE HEADER

# import pymata4, time
from pymata4 import pymata4
import time

# Define lookup dictionary for all numbers (i.e. what segments to turn on)
lookupDict = {
    '0': "11111100",
    '1': "01100000",
    '2': "11011010",
    '3': "11110010",
    '4': "01100110",
    '5': "10110110",
    '6': "10111110",
    '7': "11100000",
    '8': "11111110",
    '9': "11100110",
    'A': "11101110",
    'B': "00111110",
    'C': "10011100",
    'D': "01111010",
    'E': "10011110",
    'F': "10001110",
    'G': "10111100",
    'H': "01101110",
    'I': "00001100",
    'J': "01111000",
    'K': "10101110",
    'L': "00011100",
    'M': "10101000",
    'N': "11101100",
    'O': "11111100",
    'P': "11001110",
    'Q': "11010110",
    'R': "11001100",
    'S': "10110110",
    'T': "00011110",
    'U': "01111100",
    'V': "01111100",
    'W': "01010100",
    'X': "01101110",
    'Y': "01110110",
    'Z': "11011010",

    'a': "11111010",
    'b': "00111110",
    'c': "00011010",
    'd': "01111010",
    'e': "11011110",
    'f': "10001110",
    'g': "11110110",
    'h': "00101110",
    'i': "00001000",
    'j': "10110000",
    'k': "10101110",
    'l': "00001100",
    'm': "00101000",
    'n': "00101010",
    'o': "00111010",
    'p': "11001110",
    'q': "11100110",
    'r': "00001010",
    's': "10110110",
    't': "00011110",
    'u': "00111000",
    'v': "00111000",
    'w': "00101000",
    'x': "01101110",
    'y': "01110110",
    'z': "11011010",

    ' ': "00000000",
    '!': "01100001",
    '"': "01000100",
    '#': "01111110",
    '$': "10110110",
    '%': "01001011",
    '&': "01100010",
    "'": "00000100",
    '(': "10010100",
    ')': "11010000",
    '*': "10000100",
    '+': "00001110",
    "'": "00001000",
    '-': "00000010",
    '.': "00000001",
    '/': "01001010",

    ':': "10010000",
    ';': "10110000",
    '<': "10000110",
    '=': "00010010",
    '>': "11000010",
    '?': "11001011",
    '@': "11111010",
    '[': "10011100",
    '\\': "00100110",
    ']': "11110000",
    '^': "11000100",
    '_': "00010000",
    '`': "01000000",
    '{': "01100010",
    '|': "00001100",
    '}': "00001110",
    '~': "10000000"
}

# fix: [.-'+],

# allows for up to 4 length alphanumeric messages
def format_message(charString):

    # separate message into a list by characters
    charList = list(charString)

    # replace non-allowable characters (except "."") with empty character
    for i in range(len(charList)):
        if charList[i] != "." and charList[i] not in lookupDict:
                charList[i] = " "

    # merge any "." with previous character if it exists
    i = 0
    while i < len(charList):
        if charList[i] == "." and i > 0 and charList[i-1] != ".":
            charList[i-1] += "." # add "." to the previous character
            charList.pop(i) # remove the lone "." from the list of characters
        elif charList[i] == ".":
            charList[i] = " ."
            i += 1
        else:
            i += 1
    
    # truncate or extend the message to length 4
    while len(charList) != 4:
        if len(charList) < 4:
            charList.append(" ")
        else:
            charList = charList[:4]
    
    return charList

# function to light a digit
def light_segments(board, segPins, char):
    
    # in the case of "." in a digit, adjust the segment ON/OFF value from the dictionary to include it
    if "." in char:
        segValues = lookupDict[str(char[:-1])]
        segValues = segValues[:-1] + "1"
    else:
        segValues = lookupDict[str(char)]

    # light the segments according to the lookup dictionary values
    for i in range(len(segValues)):
        board.digital_pin_write(segPins[i], int(segValues[i]))

# function to multiplex
def set_pins(message, board, segPins, powerPins, duration, refreshRate):
    """
    Function name: set_pins

    Description: 
                Contains the logic for multiplexing, to achieve the illusion of multiple digits being on at once.

    Parameters: 
                board: the Arduino as initialised using pymata
                message: the 4-digit message which will be displayed
                timeOn: the amount of time the message should stay (if static i.e blink = False) or blink for (if blink = True)
                blink: whether or not to blink the message

    Returns: None
    """
    powerPins = [12,7,8,13]

    j = 0
    currentTime = time.time()

    while time.time() < currentTime + duration:

        for ch in message:
            if j >= 4:
                j = 0

            # turn off all pins
            for pin in powerPins:
                board.digital_pin_write(pin, 1)

            # turn on the appropriate D pins that will turn segments on/off
            light_segments(board, segPins, ch)

            # turn on the power pin depending on which letter in the message
            for i in range(len(message)):
                if j == i:
                    board.digital_pin_write(powerPins[i], 0) #

            # adjust the refresh rate (1/time between switching of digits in multiplexing)
            try:
                time.sleep(1/refreshRate)
            except ZeroDivisionError:
                time.sleep(0)

            j += 1

# Main function
def display_message(board: object, message: str, timeOn: int, blink: bool):
    """
    Function name: display_message

    Description: 
                Base function that is called from main file for displaying messages on the seven-segment display.
                Consists of calls to other functions in this file.

    Parameters: 
                board: the board as initialised using pymata
                message: the 4-digit message which will be displayed
                timeOn: the amount of time the message should stay (if static i.e blink = False) or blink for (if blink = True)
                blink: whether or not to blink the message

    Returns: None
    """

    # define pins used by segments
    allPins = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    segPins = [3, 4, 5, 6, 10, 11, 9, 2] # pins 7 and 8 have been swapped with 10 and 11 for now, since PWM doesnt seem to work with supplying voltage as high or low
    powerPins = [7, 8, 12, 13]

    # set up pins for digital output
    for pin in allPins:
        board.set_pin_mode_digital_output(pin)

    msg = format_message(message)

    refreshRate = 240 # refresh rate (Hz)

    if blink:
        currentTime = time.time()
        while time.time() < currentTime + timeOn:
            set_pins(msg, board, segPins, powerPins, 1, refreshRate) # show for 1 second
            set_pins(" ", board, segPins, powerPins, 1, refreshRate) # clear for 1 second
    else:
        set_pins(msg, board, segPins, powerPins, timeOn, refreshRate) # show message for timeOn seconds
        set_pins(" ", board, segPins, powerPins, 1, refreshRate) # clear the message/turn off digits

    