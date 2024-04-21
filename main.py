# File name: main.py 
# Purpose: Contains the traffic light system logic 
# Version '0.0' - Edited By: 'James Armit' (09/04/24) - file created with polling loop and control subsystem
# Version '1.0' - Edited By: 'Karthik Vaideeswaran' (09/04/24) - created function led_status for m2p1
# Version '2.0' - Edited By: 'Binuda Kalugalage' (10/04/2024) - added maintenance_mode, fixed display_graph, added dummy button (ped) + ultrasonic data for m2p1
# Version '3.0' - Edited By: 'James Armit' (21/04/24) - hardware integration
# Version '4.0' - Edited By: 'Binuda Kalugalage' (21/04/2024) - improved maintenance and services functions' logic; improved system parameter handling and console readability

#--- IMPORT MODULES ----
import time
from pymata4 import pymata4
import random
import matplotlib.pyplot as plt

from change_display import display_message

board = pymata4.Pymata4()

#   ----------------------- INITIALISE GLOBAL VARIABLES AND VARIABLE DICTIONARY------------------------------
pedestrians = 0
pollTime = 0
pollCycles = 12
pollInterval = 0.05
currentStage = 1 
stageChangeCycles = 10
stage1Duration = 10
stage2Duration = 1
stage3Duration = 1
stage4Duration = 10
stage5Duration = 1
stage6Duration = 1
cycleDuration = 3.00
mainRoadLights = "Green"
sideRoadLights = "Red"
pedestrianLights = "Red"
storageMaxSize = 6
timestamp = 171156

# maintenance mode variables
failCount = 0
systemVariables = {"presetPIN": 2005,
          "maxPinAttempts.": 3, 
          "lockedTime": 5}


# -- VARIABLE DICTIONARY CONTATINING DEFAULT VALUES -- 
# This dictionary is the one which can be updated in the services subsection
# Only editable variables should be in this dictionary 
systemVariables = {
    'presetPIN': 2005,
    'maxPinAttempts': 3, 
    'lockedTime': 5,
    'pollCycles' : 12,
    'pollInterval' : 0.05,
    'stage1Duration': 10,
    'stage2Duration': 1,
    'stage3Duration': 1,
    'stage4Duration': 10,
    'stage5Duration': 1,
    'stage6Duration': 1,
    'cycleDuration': 3.00,
    'storageMaxSize': 15
}

dataStorage = []
currentData = {}

pedestrian_data = []

ultrasonicData = []
ultrasonicPlaceholder = []
speedData = []

def seven_seg_display_placeholder(message):
    print("\n--- 7 SEG DISPLAY OUTPUT ---")
    if type(message) == str:
        if len(message) != 4:
            message = message[:,4]
        print(f"Message displayed: '{message}'")
    else:
        print("Message must be a string")

def display_graph(ultrasonic):

    distanceData = []
    timeData = []

    firstTime = ultrasonic[0][0][1]
    print(f"First time is {firstTime}")

    for j in range(len(ultrasonic)):
        for i in ultrasonic[j]:
            distanceData.append(i[0])
            timeData.append((i[1]-firstTime))

   # if len(timeData) < 20:
   #    print("\nInsufficient data. Please wait 20 seconds in the polling loop before trying again.\n")
   #    time.sleep(2)
   #    return
    
    plt.title("Distance from oncoming traffic vs Time")
    plt.plot(timeData,distanceData, marker="o")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Distance (cm)")

    plt.show() 

    return plt

def services():
    """
    Function name: services

    Description: Contains the services subsystem for the MVP. 
                 Displays the mode system menu displaying the different operations of the program.
                 Calls the according function depending on user input.

    Parameters: None

    Returns: None
    """

    global dataStorage 
    while True:
        ledLights = {
                'Main Road Light': "Yellow",
                'Side Road Light': "Yellow",
                'Pedestrian Light': "Yellow"
            }
        update_LED_placeholder(ledLights)

        seven_seg_display_placeholder("srvc")

        print("\n---------------------------")
        print("SYSTEM MENU                ")
        print("---------------------------")   
        print("[1] Normal \n[2] Maintenance \n[3] Data Observation \n*Type 'end' to end program")
        print("---------------------------\n")

        try:
            mode = input("Please select the mode you would like to enter: ")


            if mode == 'end':
                print("Shutting down...")
                board.shutdown()
                exit(0)
            else:
                try:
                    mode = int(mode)
                except ValueError:
                    print("\nPlease select one of the shown modes.\n")
                    time.sleep(1)
                    continue
                except KeyboardInterrupt:
                    continue
                if mode == 1:
                    print("\nEntering normal mode...\n")
                    main()
                elif mode == 2:
                    print("\nEntering maintenance mode...")
                    maintenance()
                elif mode == 3:
                    print("\nEntering data observation mode...\n")
                    inputData = []
                    for i in range(len(dataStorage[0])):
                        inputData.append(dataStorage[i]['data']['ultrasonic'])
                    display_graph(inputData).savefig("Ultrasonic_Data.png")
                    print("Graph displayed")
                else:
                    print("\nPlease select one of the shown modes.\n")
                    time.sleep(1)
                    continue
        except KeyboardInterrupt:
            continue


def maintenance():
    """
    Function name: maintenance_mode
    
    Description: This function contains the logic for the maintenance mode.
                 System parameters can be modified through this function.
    
    Parameters: None

    Returns: None
    """

    seven_seg_display_placeholder("adjt")

    global failCount, systemVariables, currentData

    stage_6() # call stage 6

    while True:
        try:
            PINAttempt = input("\nPlease enter the PIN to enter maintenance mode.\n*Type 'back' to return to the system menu.\nPIN: ")

            if PINAttempt == 'back':
                services() # return to system menu
                return
            else:
                try:
                    PINAttempt = int(PINAttempt)
                except ValueError:
                    print("\nPlease enter a PIN attempt.")
                    time.sleep(1)
                    continue

                if PINAttempt == systemVariables['presetPIN']:
                    failCount = 0 # forget any previous failed attempts

                    while True:
                        print("\n---------------------------")
                        print("SYSTEM PARAMETERS          ")
                        print("---------------------------")
                        for variable in enumerate(systemVariables):
                            print(f"[{variable[0]+1}] {variable[1]}: {systemVariables[variable[1]]}")
                        print("---------------------------\n")

                        chosenParam = input("Please select the parameter you would like to modify.\n*Type 'back' to return to the system menu.\n")

                        if chosenParam == 'back':
                            services()
                            return
                        else:
                            try:
                                chosenParam = int(chosenParam)
                            except ValueError:
                                print("\nPlease select one of the shown parameters.\n")
                                time.sleep(1)
                                continue

                            if chosenParam in range(1, len(systemVariables) + 1):
                                chosenKey = list(systemVariables.keys())[chosenParam - 1]
                                chosenValue = int(input(f"Please enter the value you would like to set '{chosenKey}' to: "))
                                systemVariables[chosenKey] = chosenValue

                                print(f"\nUpdated parameter [{chosenParam}] {chosenKey} to {chosenValue}")
                                time.sleep(1)
                            else:
                                print("\nPlease select one of the shown parameters.\n")
                                time.sleep(1)
                                continue

                else:
                    failCount += 1
                    if failCount >= systemVariables['maxPinAttempts']:
                        print(f"\nToo many incorrect attempts. Try again in {systemVariables['lockedTime']} seconds.")
                        seven_seg_display_placeholder("Locd")
                        # display_message(board, 'Locd', systemVariables['lockedTime'], False)
                        time.sleep(systemVariables['lockedTime'])
                        failCount = 0
                    else:
                        print("\nIncorrect PIN. Please try again.")
                        time.sleep(1)
                    continue
        except KeyboardInterrupt:
            print()
            continue

# ACTUAL HARDWARE INTEGRATED FUNCTION
def input_data(cycles,intervalLength):
    """
    Function name: input_data
    
    Description: This function runs each cycle and takes inputs from the sensors in the system.
    
    Parameters:
        cycles (int): the number of measurements to take
        intervalLength (float): the time delay between each measurement in seconds
    Returns: 
        ouput (dictionary): contains the arrays output by each sensor to be interpreted in the polling loop
    
    """
    try:
        global pedestrians
        global pollTime
        triggerPin = 3
        echoPin = 5
        pedestrians = 0
        for i in range(cycles*4):
            # -------- PEDESTRIANS -------
            board.set_pin_mode_digital_input(6)
            pedButton = 6
            button = board.digital_read(pedButton)
            pedestrian_data.append(button[0])
            #print(pedestrian_data)
            if len(pedestrian_data) >= 2:
                if button[0] > pedestrian_data[-1]:
                    print("Button pressed!")
                elif button[0] < pedestrian_data[1]:
                    print("Button released!")
            # --------  ULTRASONIC  -------------
            sumSpeed = 0
            board.set_pin_mode_sonar(triggerPin,echoPin,timeout=200000)
            result = board.sonar_read(triggerPin)     
            if i >= 3:  
                if ultrasonicData[-1][0] == 60 and result[0] < 60:
                    print("Object detected in range")
                if ultrasonicData[-1][0] < 60 and result[0] == 60:
                    print("Object has left range")
            if result[1] != 0:
                ultrasonicData.append(result)
            
            #print(f"The nearest object is {result[0]} cm away at {result[1]}")
            # Find the change in distance and time over one inteval
            # Note that ultrasonicData[-1] = ultrasonicData[-2] for some reason
            if i >= 4:
                try:
                    deltaD = result[0] - ultrasonicData[-3][0]
                    deltaT = result[1] - ultrasonicData[-3][1]
                    speed = deltaD / deltaT
                    if speed > 0.1:
                        #print(f"The current speed is {speed:.3f} cm/s")
                        speedData.append(speed)
                    else:
                        #print(f"No movement detected")
                        pass
                except ZeroDivisionError:
                    pass
            time.sleep(intervalLength)
            pollTime += intervalLength
        for i in speedData:
            sumSpeed += i
        averageSpeed = sumSpeed / cycles * 4
        print(f"The average speed during the intervals was {averageSpeed:.3f} cm/s")
        for i in range(len(pedestrian_data)):
            if pedestrian_data[i] == 1:
                if pedestrian_data[i] > pedestrian_data[i-1]:
                    pedestrians += 1
        print(f"{pedestrians} have pushed the button during the stage")
        output = {
            'pedestrian': pedestrian_data,
            'ultrasonic': ultrasonicData
        }
        return output
    except KeyboardInterrupt:
        services()
        return


# TEST INPUTS / PLACEHOLDER FUNCTION
#def input_data_placeholder(cycles,intervalLength):
    """
    Function name: input_data_placeholder

    Description: Provides randomised input data from the pedestrian button and ultrasonic sensor
    This data is random but has limits such that it will return a result that is within the boundries 
    of the actual hardware integrated function 

    Parameters: 
        Cycles (int): the number of checks the system should do (number of datapoints)
        intervalLength (float): the delay time between each interval
    Returns:
        output (dict): a dictionary containing the resulting lists 
    """
   # global pedestrians,timestamp, pollTime
   # ultrasonicPlaceholder = []
   # pedestrianPlaceholder = []
   # firstValues = [0,timestamp]
   # nextValues = firstValues
   # for i in range(10):
   #     nextValues = [random.randint(0,60), nextValues[1] + i/12]
   #     ultrasonicPlaceholder.append(nextValues)
   # for i in range(10):
   #     pedestrianPlaceholder.append(random.randint(0,1))
   # for i in range(len(pedestrianPlaceholder)):
   #         if pedestrianPlaceholder[i] == 1:
   #             if pedestrianPlaceholder[i] > pedestrianPlaceholder[i-1]:
   #                 pedestrians += 1
   # print(f"\n{pedestrians} have pushed the pedestrian button since stage 1")
   # output = {
   #     'ultrasonic' : ultrasonicPlaceholder,
   #     'pedestrian' : pedestrianPlaceholder
   # }
   # time.sleep((cycles*4)*intervalLength)
   # pollTime = 0
   # timestamp = ultrasonicPlaceholder[-1][1]
   # return output
    
def stage_1():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 1

    mainRoadLights = "Green"
    sideRoadLights = "Red"
    pedestrianLights = "Red"

    pedestrians = 0

    stageChangeCycles = stage1Duration

    seven_seg_display_placeholder("stg1")

def stage_2():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 2

    mainRoadLights = "Yellow"
    sideRoadLights = "Red"
    pedestrianLights = "Red"

    stageChangeCycles = stage2Duration

    seven_seg_display_placeholder("stg2")

def stage_3():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 3

    mainRoadLights = "Red"
    sideRoadLights = "Red"
    pedestrianLights = "Red"

    print(f"Pedestrians: {pedestrians}")

    stageChangeCycles = stage3Duration

    seven_seg_display_placeholder("stg3")

def stage_4():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 4

    mainRoadLights = "Red"
    sideRoadLights = "Green"
    pedestrianLights = "Green"

    stageChangeCycles = stage4Duration

    seven_seg_display_placeholder("stg4")

def stage_5():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 5

    mainRoadLights = "Red"
    sideRoadLights = "Yellow"
    pedestrianLights = "gf"

    stageChangeCycles = stage5Duration

    seven_seg_display_placeholder("stg5")

def stage_6():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 6

    mainRoadLights = "Red"
    sideRoadLights = "Red"
    pedestrianLights = "Red"

    stageChangeCycles = stage6Duration

    seven_seg_display_placeholder("stg6")

def set_stage(current):
    """
    Function: set_stage

    Description: contains the logic for transitioning between stages 

    Parameters: current (int), the current stage 
    
    Returns: No returns
    """
    if current == 1:
        stage_2()
    elif current == 2:
        stage_3()
    elif current == 3:
        stage_4()
    elif current == 4:
        stage_5()
    elif current == 5:
        stage_6()
    elif current == 6:
        stage_1()

def update_LED_placeholder(ledDict):
    print("---- LED LIGHT OUTPUT --- ")
    ledMapping = {
        'main': {
            "Green": 13,
            "Yellow": 12,
            "Red": 11
        },
        'side': {
            "Green": 10,
            "Yellow": 9,
            "Red": 8
        }
    }
    for keys in ledDict:
        print(f"{keys} is set to {ledDict[keys]} LED active")
    for i in range(8,14):
        board.set_pin_mode_digital_output(i)
        board.digital_write(i,0)
    board.digital_write(ledMapping['main'][mainRoadLights],1)
    board.digital_write(ledMapping["side"][sideRoadLights],1)
    


def main():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles,pollTime,dataStorage
    """
    Function name: main 

    Description: This function will contain the main polling loop which operates
    when the system is in Normal Operations. It will be constantly running unless 
    otherwise stopped so long as the file is not imported as a module

    Parameters: None 
    Returns: None 
    """
    # Keep the loop running infinitely 
    # If a Keyboard inturrupt is used, exit the program. Otherwise, keep running
    try:
        while True:
            # reset the value of 'currentData' to a blank dictionary
            currentData = {}
            # reset PollTime to 0
            pollTime = 0
            # call all input functions
            #   currentData['data'] = input_data(12,0.05)  THIS IS THE ACTUAL HARDWARE INTEGRATED FUNCTION
            currentData['data'] = input_data(pollCycles,pollInterval)
            dataStorage.append(currentData)
            if len(dataStorage[0]) > storageMaxSize:
                dataStorage.remove(dataStorage[0])
                                      
            if stageChangeCycles <= 0: # Check in case the duration is edited such that the value is now negative
                set_stage(currentStage)

            if pedestrians > 1:
                if currentStage == 1:
                    if currentData['data']['ultrasonic'][-1][0] == 60 :
                        if stageChangeCycles > 2:
                            stageChangeCycles = 2
                else:
                    pass
            else:
                pass
            print(f"Cycles to stage change: {stageChangeCycles}")
            print(f"Current stage: {currentStage}")
            ledLights = {
                'Main Road Light': mainRoadLights,
                'Side Road Light': sideRoadLights,
                'Pedestrian Light': pedestrianLights
            }

            update_LED_placeholder(ledLights)

            delayTime = cycleDuration - pollTime
            time.sleep(delayTime)
            stageChangeCycles -= 1 
    except KeyboardInterrupt:
        services()
        return
    
if __name__ == "__main__":
    services()
