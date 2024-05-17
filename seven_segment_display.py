# File name: seven_segment_display.py 
# Created By: Binuda Kalugalage
# Created Date: 01/04/2024
# Purpose: Contains the code for configuring the seven segment display and showing 4-digit alphanumeric messages on it 
# version = '9.0'

# Import modules
from pymata4 import pymata4
import time

# Define pins
digitPins = [2, 3, 6, 7]
SER = 8
RCLK = 9
SRCLK = 10
SRCLR = 2

allPins = [2, 3, 6, 7, 8, 9, 10]

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

    ' ': "00000000",
    '!': "01000001",
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

def click_srclk(board):
    board.digital_write(SRCLK, 1)
    board.digital_write(SRCLK, 0)

def click_rclk(board):
    board.digital_write(RCLK, 1)
    board.digital_write(RCLK, 0)


def format_message(charString, scrolling):
    """
    Function name: format_message

    Description: 
                Validates the message to be displayed to be a 4-letter alphanumeric string, and additionally formats decimal points if present.

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
                if "." not in charList[charIndex - 1]:  # if it is also not preceded by a decimal point
                    charList[charIndex-1] += "." # add "." to the previous character
                    charList.pop(charIndex) # remove the current lone "." from the list of characters
                else:
                    charList[charIndex] = " ." # if it is preceded by a decimal point, make that decimal point be alone in its own digit
                    charIndex += 1
            else: 
                charList[charIndex] = " ." # if it is the first character, make that decimal point be alone in its own digit
                charIndex += 1
        else:
            charIndex += 1 # go to the next character, with nothing happening to the current character
    
    # truncate or extend the message to length 4 if static
    if not scrolling:
        while len(charList) != 4:
            if len(charList) < 4:
                charList.append(" ") # extend message to length 4
            else:
                charList = charList[:4] # truncate message to length 4
    
    return charList

def scroll_format(wholeString):
    """
    Function name: scroll_format

    Description: 
                Creates a series of 

    Parameters: 
                charString (string): the 4-digit message as a string which will be displayed

    Returns: a list containing the characters of the validated and formatted input message, in order
    """


    def padded(lst, length, pad_value, direction):
        if direction == 'L':
            return ([pad_value] * (length - len(lst))) + lst
        elif direction == 'R':
            return lst + ([pad_value] * (length - len(lst)))

    scrollSections = []
    midIndex = len(wholeString) // 2  # calculate the middle index
    
    if len(wholeString) > 1:
        for i in range(len(wholeString)+5):

            if i <= 3:
                subString = wholeString[0:i]
            if i > 3:
                subString = wholeString[-4+i:0+i] # (= wholeString[i-4:i])

            if 0 < len(subString) <= 4:
                # if in_first_half(wholeString, list(subString)):
                if i - len(subString) > midIndex: # first half -> pad right
                    scrollSections.append(padded(subString, 4, ' ' , 'R'))
                elif i - len(subString) == midIndex: # exactly half -> pad to middle
                    scrollSections.append(padded(padded(subString, 3, ' ' , 'L'), 4, ' ', 'R'))
                else: # second half -> pad left
                    scrollSections.append(padded(subString, 4, ' ' , 'L'))
            elif len(subString) == 0:
                scrollSections.append([' ', ' ', ' ', ' '])
            elif len(subString) > 4:
                scrollSections.append(subString)
    elif len(wholeString) == 1:

        subString = wholeString

        scrollSections.append([' ', ' ', ' ', ' '])

        for i in range(4):
            scrollSections.append(padded(padded(subString, 4-i, ' ' , 'L'), 0 if i==0 else 4, ' ', 'R'))

        scrollSections.append([' ', ' ', ' ', ' '])

    
    return scrollSections 

def enable_segments(board, trafficBits, charA, charB):
    """
    Function name: enable_segments

    Description: 
                Controls which segment pins (of all digits) of the display are powered, depending on the current character 'currentChar'

    Parameters: 
                board (object): the Arduino board initialised using pymata
                charA (string): a character of the message on display 1
                charB (string): a character of the message on display 2

    Returns: None
    """
    
    # in the case of "." in a digit in charA
    if "." not in charA:
        segStates1 = lookupDict[str(charA)] # only set segStates to the value of the key charA, charB (with DP segment off by default)
    else:
        # find the dictionary value for key charA which describes the on/off states for the segments of the digits
        segStates1 = lookupDict[str(charA[:-1])] 
        
        # change the last character of that value (which describes the DP segment) to 1
        segStates1 = segStates1[:-1] + "1" 

    # in the case of "." in a digit in charB
    if "." not in charB:
        segStates2 = lookupDict[str(charB)] # only set segStates to the value of the key charA, charB (with DP segment off by default)
    else:
        # find the dictionary value for key charB which describes the on/off states for the segments of the digits
        segStates2 = lookupDict[str(charB[:-1])] 
        
        # change the last character of that value (which describes the DP segment) to 1
        segStates2 = segStates2[:-1] + "1" 


    # enable the segments according to the lookup dictionary values
    # pushedBits = []
    for bit in trafficBits[::-1]+segStates2[::-1]+segStates1[::-1]:
        board.digital_write(SER, int(bit)) # SER (1 or 0)
        # pushedBits += bit        
        click_srclk(board)
        
    # print(pushedBits)

def cycle_digits(message1, message2, trafficBits, board, refreshRate):
    """
    Function name: cycle_digits

    Description: 
                Contains the logic to achieve the effect of multiple digits 'being on at once'.
                Cycles through each digit of the display and turns it on if appropriate.
                Contains calls to function 'enable_segments'.

    Parameters: 
                message (list): the validated 4-digit message as a list
                board (object): the Arduino board initialised using pymata
                duration (float): the amount of time the message should stay on for
                refreshRate (float): the frequency (in Hz), at which the display's 4 digits will be updated. Defaults to 60Hz.

    Returns: None
    """ 

    digitNum = 1 # counter for the current digit (1, 2, 3 or 4, from left to right)

    # for each character in the list 'message' 
    for chA, chB, traffic in zip(message1[::-1], message2[::-1], trafficBits[::-1]):
        # reset the counter digitNum to 1 after all four digits has been cycled through once
        if digitNum >= 5:
            digitNum = 1

        # disable all segments
        enable_segments(board, trafficBits, " ", " ")

        # turn off all digits
        # UNCOMMENT IF SRCLR IS ADDED
        # board.digital_write(SRCLR, 0)
        # click_rclk(board)
        # board.digital_write(SRCLR, 1)
        for pin in digitPins:
            board.digital_write(pin, 1)

        # turn on the appropriate segment pins for the given character ch on all digits
        enable_segments(board, trafficBits, chA, chB)

        click_rclk(board)

        # turn on only the current digit
        board.digital_write(digitPins[digitNum - 1], 0) # subtract digitPins by 1 to match Python's list indexing syntax

        # all four digits are updated every 1/refreshRate seconds, 
        # therefore each of the FOUR (4) digits are updated every (1/refreshRate)/4 seconds
        try:
            time.sleep((1/refreshRate)/4)
        except ZeroDivisionError:
            time.sleep((1/60)/4) # if the refresh rate is 0, the default will be 60hz

        digitNum += 1 # go to the next digit on the display
   
def display_message(scrollText, staticText, trafficBits, board, timeOn, scrolling, refreshRate = 60):
    """
    Function name: display_message

    Description: 
                Base function that is called from main file for displaying messages on the seven-segment display.
                Contains calls to format_message and cycle_digits.

    Parameters: 
                message (string): the 4-digit message as a string which will be displayed
                board (object): the Arduino board initialised using pymata
                timeOn (float): the amount of time the message should display for
                scrolling (bool): whether or not to scroll the message
                refreshRate (float): the frequency (in Hz) at which the display's 4 digits will be updated. Defaults to 60Hz

    Returns: None
    """

    formattedScrollText = format_message(scrollText, True)
    formattedStaticText = format_message(staticText, False)

    if scrolling:
        scrollSections = scroll_format(formattedScrollText)
        for section in scrollSections:
            currentTime = time.time()  # the current time before displaying the current section on scrolling display
            while time.time() < currentTime + timeOn/len(scrollSections):
                cycle_digits(section, formattedStaticText, trafficBits, board, refreshRate)     
    else:
        currentTime = time.time()  # the current time before displaying the current section on scrolling display
        while time.time() < currentTime + timeOn:
            cycle_digits("    ", formattedStaticText, board, refreshRate)     
    
    cycle_digits("    ", "    ", trafficBits, board, refreshRate) # clear the message by turning off all digits on both displays




# ------------------------------------- BELOW CODE IS FOR DEBUGGING ONLY ------------------------------------- 
# board = pymata4.Pymata4() # define the Arduino board
# # configure pins for digital output
# for pin in allPins:
#     board.set_pin_mode_digital_output(pin)

# while True:
#     try:
#         scrollMessage = input("Please enter the scrolling message you would like to display: ") # the message to be displayed
#         staticMessage = input("Please enter the static message you would like to display: ") # the message to be displayed
#         onTime = float(input("Time to stay on: ")) # time for the message to be displayed

#         display_message(scrollMessage, staticMessage, board, onTime, True, 120) # call the seven segment display function
#     except ValueError:
#         print("\nPlease ensure that the time to stay on is a float.\n")
#     except KeyboardInterrupt: # shutdown the board and quit the program on a keyboard interrupt (Control-C)
#         print("\nQuitting...")
#         board.shutdown()
#         quit()


