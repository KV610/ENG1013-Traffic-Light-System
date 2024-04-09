# File name: main.py 
# Purpose: Contains the polling loop and control subsystem 
# Creator: 'James Armit'
# Version: '1.0'

#--- IMPORT MODULES ----
import time
from pymata4 import pymata4

board = pymata4.Pymata4()

#   ----------------------- INITIALISE GLOBAL VARIABLES AND VARIABLE DICTIONARY------------------------------
pedestrians = 0
pollTime = 0
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


dataStorage = []
storageMaxSize = 15
currentData = {}

pedestrian_data = []

ultrasonicData = []
speedData = []

def plot_data(ultrasonic):
    pass

def services():
    """
    Function name: services

    Description: Contains the services subsystem for the MVP and allows the user to change any value in the system 

    Parameters: None

    Returns: updatedParams (dict) a dictionary of any modified values
    """
    global presetPIN,failCount,maxAttempts  # This should continue to include all global variables
    paramOptions = [1, 2, 3]                # TODO: Update this section such that all global variables are permanently updated
    paramVars = ["delay", "frequency", "distance"]
    paramValues = [300, 60, 90]
    while True:
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

                    continue

                elif choice == '2':
                    #display_graph()
                    print("Graph displayed")
                    # display_message(segBoard, "data", 5, True)

                elif choice == '3':
                    print("Exiting maintenence...")
                    exit()
                    break  # break out of this while loop
        else:
            failCount += 1

        if failCount >= maxAttempts:
            # display_message(segBoard, "Locd", 5, False)
            print("LOCKED")
            time.sleep(5) # wait 5 (or however many, feel free to edit) seconds after displaying 'locked' message
            failCount = 0
            continue

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
            if i >= 1:  
                if ultrasonicData[-1][0] == 60 and result[0] < 60:
                    print("Object detected in range")
                if ultrasonicData[-1][0] < 60 and result[0] == 60:
                    print("Object has left range")
            ultrasonicData.append(result)
            #print(f"The nearest object is {result[0]} cm away at {result[1]}")
            # Find the change in distance and time over one inteval
            # Note that ultrasonicData[-1] = ultrasonicData[-2] for some reason
            if i >= 3:
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

def stage_1():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 1

    mainRoadLights = "g"
    sideRoadLights = "r"
    pedestrianLights = "r"

    pedestrians = 0

    stageChangeCycles = stage1Duration

def stage_2():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 2

    mainRoadLights = "y"
    sideRoadLights = "r"
    pedestrianLights = "r"

    stageChangeCycles = stage2Duration

def stage_3():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 3

    mainRoadLights = "r"
    sideRoadLights = "r"
    pedestrianLights = "r"

    print(f"Pedestrians: {pedestrians}")

    stageChangeCycles = stage3Duration

def stage_4():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 4

    mainRoadLights = "r"
    sideRoadLights = "g"
    pedestrianLights = "g"

    stageChangeCycles = stage4Duration

def stage_5():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 5

    mainRoadLights = "r"
    sideRoadLights = "y"
    pedestrianLights = "gf"

    stageChangeCycles = stage5Duration

def stage_6():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 6

    mainRoadLights = "r"
    sideRoadLights = "r"
    pedestrianLights = "r"

    stageChangeCycles = stage6Duration

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

def main():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles,pollTime
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
            currentData['data'] = input_data(12,0.05)
            dataStorage.append(currentData)
            #print(currentData)
            if len(dataStorage) > storageMaxSize:
                dataStorage.remove(dataStorage[0])

            # check if the mode switch button is pressed
            # if so, call 'maintenence' function and pause loop 
                
            if stageChangeCycles == 0:
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
            print(mainRoadLights)
            print(sideRoadLights)
            print(pedestrianLights)

            delayTime = cycleDuration - pollTime
            time.sleep(delayTime)
            stageChangeCycles -= 1 
    except KeyboardInterrupt:
        services()
    

if __name__ == "__main__":
    main()