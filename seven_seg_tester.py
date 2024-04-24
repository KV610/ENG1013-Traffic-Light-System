from pymata4 import pymata4
from change_display import display_message

segBoard = pymata4.Pymata4()

try:
    while True:
        text = input("Please enter the message you would like to display: ")
        # time = int(input("Time to stay: "))
        display_message(segBoard, text, 5, False)
except KeyboardInterrupt:
    print("\nQuitting...")
    segBoard.shutdown()
    quit()
