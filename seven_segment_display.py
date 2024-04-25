# File name: seven_segment_display.py 
# Created By: Binuda Kalugalage
# Created Date: 01/04/2024
# Purpose: Contains the code for configuring the seven segment display and showing 4-digit alphanumeric messages on it 
# version = '5.0'

# Import modules
from pymata4 import pymata4
import time

# Define pins
segPins = [3, 4, 5, 6, 10, 11, 9, 2] # define pins powering the segments of the digits, ordered such that they map to segments a, b, c, d, e, f, g and DP
digitPins = [12, 7, 8, 13] # define pins powering the digits themselves, ordered such that they map to pins 1, 2, 3 and 4

# Define lookup dictionary for all alphanumeric characters (for which segments to turn on)
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

    ' ': "00000000"
}

def format_message(charString):
    """
    Function name: cycle_digits

    Description: 
                Validates the message to be displayed to be a 4-letter alphanumeric string, and additionally formats decimal points if present

    Parameters: 
                charString (string): the 4-digit message as a string which will be displayed

    Returns: a list containing the characters of the validated and formatted input message, in order
    """

    # separate input string into a list by characters
    charList = list(charString)

    # replace non-allowable characters in that list (except "."") with a space (" ")
    for character in charList:
        if character != "." and character not in lookupDict:
                charList[charList.index(character)] = " "
    
    # handle decimal points in the list - merge any "." with the preceding character
    charIndex = 0
    while charIndex < len(charList):
        if charList[charIndex] == ".": # if the current character is a decimal point
            if charIndex != 0: # if it is not the first character
                if "." not in charList[charIndex-1]:  # if it is also not preceded by a decimal
                    charList[charIndex-1] += "." # add "." to the previous character
                    charList.pop(charIndex) # remove the current lone "." from the list of characters
                else:
                    charList[charIndex] = " ."
                    charIndex += 1
            else: # if it is the first character
                charList[charIndex] = " ."
                charIndex += 1
        else:
            charIndex += 1 # go to the next character, nothing happens to current character
    
    # truncate or extend the message to length 4
    while len(charList) != 4:
        if len(charList) < 4:
            charList.append(" ")
        else:
            charList = charList[:4]
    
    return charList

def enable_segments(board, currentChar):
    """
    Function name: enable_segments

    Description: 
                Controls which segment pins (of all digits) of the display are powered, depending on the current character 'currentChar'

    Parameters: 
                board (object): the Arduino board initialised using pymata
                currentChar (string): a character of the message, which is being cycled through in cycle_digits

    Returns: None
    """
    
    # in the case of "." in a digit, adjust the segment ON/OFF value from the dictionary to include it
    if "." in currentChar:
        segValues = lookupDict[str(currentChar[:-1])]
        segValues = segValues[:-1] + "1"
    else:
        segValues = lookupDict[str(currentChar)]

    # light the segments according to the lookup dictionary values
    for i in range(len(segValues)):
        board.digital_pin_write(segPins[i], int(segValues[i]))

def cycle_digits(message, board, duration, refreshRate):
    """
    Function name: cycle_digits

    Description: 
                Contains the logic to achieve the effect of multiple digits 'being on at once'.
                Cycles through each digit of the display and turns on/off
                Contains calls to function 'enable_segments'.

    Parameters: 
                message (list): the validated 4-digit message as a list
                board (object): the Arduino board initialised using pymata
                duration (float): the amount of time the message should stay on for
                refreshRate (float): the frequency (in Hz), at which the display's 4 digits will be updated. Defaults to 60Hz.

    Returns: None
    """ 

    digitNum = 1 # counter for the current digit (1, 2, 3 or 4, from left to right)
    currentTime = time.time() # the current time before displaying the message

    # for the specified duration, execute the code below
    while time.time() < currentTime + duration:

        # for each character in the list 'message' 
        for ch in message:
            # reset the counter digitNum to 1 after all four digits has been cycled through once
            if digitNum >= 5:
                digitNum = 1

            # turn off all digits
            for pin in digitPins:
                board.digital_pin_write(pin, 1)

            # turn on the appropriate segment pins for the given character ch on all digits
            enable_segments(board, ch)

            # turn on only the current digit on the display
            board.digital_pin_write(digitPins[digitNum - 1], 0) # subtract digitPins by 1 to match Python's list indexing syntax


            # all four digits are updated every 1/refreshRate seconds, 
            # therefore each of the FOUR (4) digits are updated every (1/refreshRate)/4 seconds
            try:
                time.sleep((1/refreshRate)/4)
            except ZeroDivisionError:
                time.sleep((1/60)/4) # if the refresh rate is 0, the default will be 60hz

            digitNum += 1 # go to the next digit on the display
   
def display_message(message, board, timeOn, refreshRate = 60):
    """
    Function name: display_message

    Description: 
                Base function that is called from main file for displaying messages on the seven-segment display.
                Contains calls to format_message and cycle_digits.

    Parameters: 
                message (string): the 4-digit message as a string which will be displayed
                board (object): the Arduino board initialised using pymata
                timeOn (float): the amount of time the message should display for
                refreshRate (float): the frequency (in Hz) at which the display's 4 digits will be updated. Defaults to 60Hz

    Returns: None
    """

    allPins = segPins + digitPins

    # set up pins for digital output
    for pin in allPins:
        board.set_pin_mode_digital_output(pin)


    cycle_digits(format_message(message), board, timeOn, refreshRate) # show message for timeOn seconds
    cycle_digits("    ", board, 1, refreshRate) # clear the message by turning off all digits




# ------------------ BELOW CODE IS FOR MILESTONE 2 DEMONSTRATION ONLY ------------------ 
segBoard = pymata4.Pymata4() # define the Arduino board
while True:
    try:
        displayText = input("Please enter the message you would like to display: ") # the message to be displayed
        onTime = float(input("Time to stay on: ")) # time for the message to be displayed
        display_message(displayText, segBoard, onTime, 60) # call the seven segment display function
    except ValueError:
        print("\nPlease ensure that the time to stay on is a float.\n")
        continue
    except KeyboardInterrupt: # shutdown the board and quit the program on a keyboard interrupt (Control-C)
        print("\nQuitting...")
        segBoard.shutdown()
        quit()