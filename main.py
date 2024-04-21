# File name: main.py 
# Purpose: Contains the polling loop and all subsytems
# Creator: 'James Armit'
# Version: '3.0' - Hardware integrated

#--- IMPORT MODULES ----
import time
from pymata4 import pymata4
import random
import matplotlib.pyplot as plt
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
mainRoadLights = "g"
sideRoadLights = "r"
pedestrianLights = "r"
presetPIN = 2005
failCount = 0
maxAttempts = 4
storageMaxSize = 6
timestamp = 171156

# -- VARIABLE DICTIONARY CONTATINING DEFAULT VALUES -- 
# This dictionary is the one which can be updated in the services subsection
# Only editable variables should be in this dictionary 
systemVariables = {
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

def update_system_variables(updatedVariables):
    global systemVariables, pollCycles, pollInterval, stage1Duration, stage2Duration, stage3Duration, stage4Duration, stage5Duration, stage6Duration, cycleDuration, storageMaxSize
    systemVariables = updatedVariables
    # Update all modifiable variables
    pollCycles = systemVariables['pollCycles']
    pollInterval = systemVariables['pollInterval']
    stage1Duration = systemVariables['stage1Duration']
    stage2Duration = systemVariables['stage2Duration']
    stage3Duration = systemVariables['stage3Duration']
    stage4Duration = systemVariables['stage4Duration']
    stage5Duration = systemVariables['stage5Duration']
    stage6Duration = systemVariables['stage6Duration']
    cycleDuration = systemVariables['cycleDuration']
    storageMaxSize = systemVariables['storageMaxSize']

    # for testing
    print(systemVariables)

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
    
    plt.title("Distance from oncoming traffic vs Time")
    plt.plot(timeData,distanceData, marker="o")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Distance (cm)")


    plt.show() 

    plt.savefig("Ultrasonic_Data.png")

def services():
    """
    Function name: services

    Description: Contains the services subsystem for the MVP and allows the user to change any value in the system 

    Parameters: None

    Returns: updatedParams (dict) a dictionary of any modified values
    """
    global dataStorage 
    while True:
        ledLights = {
                'Main Road Light': "y",
                'Side Road Light': "y",
                'Pedestrian Light': "y"
            }
        update_LED_placeholder(ledLights)
        seven_seg_display_placeholder("srvc")
        print("[1] Normal \n[2] Maintenance \n[3] Data Observation \n[4] Quit Program")

        try:
            mode = int(input("Please select the mode you would like to enter: "))
        except ValueError:
            print("Invalid input")
            continue

        if mode == 1:
            print("Entering normal mode...")
            main()
        elif mode == 2:
            print("Entering maintenance mode...")
            maintenence()
        elif mode == 3:
            print("Entering data observation mode...")
            inputData = []
            for i in range(len(dataStorage[0])):
                #print(dataStorage[i]['data']['ultrasonic'])
                inputData.append(dataStorage[i]['data']['ultrasonic'])
            display_graph(inputData)
            print("Graph displayed")
        elif mode == 4:
            print("Quitting Program...")
            exit()

def maintenence():
    """
    Function name: services

    Description: Contains the services subsystem for the MVP and allows the user to change any value in the system 

    Parameters: None

    Returns: updatedParams (dict) a dictionary of any modified values
    """
    global presetPIN,failCount,maxAttempts,systemVariables,currentData
    paramOptions = [1, 2, 3, 4, 5, 6, 7, 8 ,9 ,10]                # TODO: Validate inputs
    paramVars = []
    paramValues = []
    seven_seg_display_placeholder("adjt")
    for keys in systemVariables:
        paramVars.append(keys)
        paramValues.append(systemVariables[keys])
    try:
        while True:
            try:
                PINAttempt = int(input("Please enter the PIN: "))
                if PINAttempt == presetPIN:
                    while True: 
                        choice = input("Would you like to [1] modify a parameter, [2] view a graph, or [3] exit? ")

                        if choice == '1':

                            for i in range(len(paramVars)):
                                print(f"[{i+1}] {paramVars[i]}: {paramValues[i]}\n")

                            chosenParam = int(input("Please enter the parameter you would like to modify [num]: "))
                            while chosenParam not in paramOptions:
                                chosenParam = int(input("Please enter the parameter you would like to modify [num]: "))

                            chosenValue = int(input(f"Please enter the value you would like to set '{paramVars[chosenParam - 1]}' to: "))
                            paramValues[chosenParam - 1] = chosenValue

                            print(f"Updated [{chosenParam}] {paramVars[chosenParam - 1]} to {chosenValue}\n")

                            updatedVariables = {}
                            for i in range(len(paramVars)):
                                updatedVariables[paramVars[i]] = paramValues[i]

                            update_system_variables(updatedVariables)

                        elif choice == '2':
                            inputData = []
                            for i in dataStorage:
                                inputData.append(i['data']['ultrasonic'])
                            display_graph(inputData)
                            print("Graph displayed")
                            # display_message(segBoard, "data", 5, True)

                        elif choice == '3':
                            print("Exiting maintenence...")
                            break  # break out of this while loop
                    break
                else:
                    failCount += 1

                if failCount >= maxAttempts:
                    seven_seg_display_placeholder("LOCK")
                    print("LOCKED")
                    time.sleep(5) # wait 5 (or however many, feel free to edit) seconds after displaying 'locked' message
                    failCount = 0
                    break
            except ValueError:
                print("Please enter a valid 4 digit pin")
            except EOFError:
                print("Exiting...")
                exit()
    except EOFError:
        print("Exiting Program...")
        exit()

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
        print("Exiting program...")


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

    mainRoadLights = "g"
    sideRoadLights = "r"
    pedestrianLights = "r"

    pedestrians = 0

    stageChangeCycles = stage1Duration

    seven_seg_display_placeholder("stg1")

def stage_2():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 2

    mainRoadLights = "y"
    sideRoadLights = "r"
    pedestrianLights = "r"

    stageChangeCycles = stage2Duration



    seven_seg_display_placeholder("stg2")

def stage_3():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 3

    mainRoadLights = "r"
    sideRoadLights = "r"
    pedestrianLights = "r"

    print(f"Pedestrians: {pedestrians}")

    stageChangeCycles = stage3Duration

    seven_seg_display_placeholder("stg3")

def stage_4():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 4

    mainRoadLights = "r"
    sideRoadLights = "g"
    pedestrianLights = "g"

    stageChangeCycles = stage4Duration

    seven_seg_display_placeholder("stg4")

def stage_5():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 5

    mainRoadLights = "r"
    sideRoadLights = "y"
    pedestrianLights = "gf"

    stageChangeCycles = stage5Duration

    seven_seg_display_placeholder("stg5")

def stage_6():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 6

    mainRoadLights = "r"
    sideRoadLights = "r"
    pedestrianLights = "r"

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
            "g": 13,
            "y": 12,
            "r": 11
        },
        'side': {
            "g": 10,
            "y": 9,
            "r": 8
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
    # Keep the loop running infinatly 
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
            #print(currentData)
            if len(dataStorage[0]) > storageMaxSize:
                dataStorage.remove(dataStorage[0])
            #print(dataStorage[0]['data']['ultrasonic'])

            # check if the mode switch button is pressed
            # if so, call 'maintenence' function and pause loop 
                
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
    
if __name__ == "__main__":
    services()