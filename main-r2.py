# File name: main.py 
# Purpose: Contains the polling loop and control subsystem 
# Creator: 'James Armit'
# Edited By: 'Karthik Vaideeswaran' (09/04/24)
# Edited By : 'Binuda Kalugalage' (10/04/2024) - added maintenance_mode, fixed display_graph, added dummy button (ped) + ultrasonic data for m2p1
# Version: '1.1'

#--- IMPORT MODULES ----
import time
import random
import matplotlib.pyplot as plt
from pymata4 import pymata4

# board = pymata4.Pymata4()

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

stageList = [1, 2, 3, 4, 5, 6] #To have an easier way of indexing through stages
ledDict = {1: ['g','r','r'], 2: ['y','r','r'], 3: ['r','r','r'], 4: ['r','g','g'], 5: ['r','y','gf'], 6: ['r','r','r']} #Dictionary containing lists of the statuses of LEDs according to stage
dataStorage = []
storageMaxSize = 15
currentData = {}

pedestrian_data = []

ultrasonicData = []
speedData = []

# maintenance mode variables
failCount = 0
paramOptions = [1, 2, 3]
paramVars = ["presetPIN", "maxAttempts", "lockedTime"]
paramValues = [2005, 4, 5]

# params = {"presetPIN": 2005,
#           "maxAttempts": 4}

def services():
    """
    Function name: services

    Description: Contains the services subsystem for the MVP and allows the user to change any value in the system 

    Parameters: None

    Returns: updatedParams (dict) a dictionary of any modified values
    """

    while True:
        print("[1] Normal \n[2] Maintenance \n[3] Data Observation")

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
            maintenance_mode()
        elif mode == 3:
            print("Entering data observation mode...")
            display_graph(ultrasonicData)


def maintenance_mode():
    global failCount, paramOptions, paramVars, paramValues

    endMaintenance = False

    stage_6() # call stage 6

    while True:
        PINAttempt = input("Please enter the PIN to enter maintenance mode, or 'exit' to return to the system menu: ")

        if PINAttempt == 'exit':
            services() # return to services menu
            break
        else:
            try:
                PINAttempt = int(PINAttempt)
            except ValueError:
                print("Invalid input")
                continue

        if PINAttempt == paramValues[paramVars.index('presetPIN')]:
            failCount = 0 # forget any previous failed attempts
            while True: 
                choice = input("Would you like to [1] modify a parameter, or [2] exit? ")

                if choice == '1':

                    for i in range(len(paramVars)):
                        print(f"[{i+1}] {paramVars[i]}: {paramValues[i]}\n")

                    chosenParam = int(input("Please enter the parameter you would like to modify [num]: "))
                    while chosenParam not in paramOptions:
                        chosenParam = int(input("Please enter the parameter you would like to modify [num]: "))

                    chosenValue = int(input(f"Please enter the value you would like to set '{paramVars[chosenParam - 1]}' to: "))
                    paramValues[chosenParam - 1] = chosenValue

                    print(f"Updated [{chosenParam}] {paramVars[chosenParam - 1]} to {chosenValue}\n")
            
                elif choice == '2':
                    endMaintenance == True
                    break # break out of this while loop
        else:
            failCount += 1

        if failCount >= paramValues[paramVars.index('maxAttempts')]:
            # display_message(segBoard, "Locd", 5, False)
            print("LOCKED")
            time.sleep(paramValues[paramVars.index('lockedTime')]) # wait 5 (or however many, feel free to edit) seconds after displaying 'locked' message
            failCount = 0

        if endMaintenance:
            services() # return to services menu
            break # break out of this while loop and end maintenance mode


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

    result = [1, 0] # temporary for m2p1
    try:
        global pedestrians
        global pollTime
        triggerPin = 3
        echoPin = 5
        pedestrians = 0
        for i in range(cycles*4):
            # -------- PEDESTRIANS -------
            # board.set_pin_mode_digital_input(6)
            # pedButton = 6
            # button = board.digital_read(pedButton)

            button = [random.randint(0,1), random.randint(0,1)]
            pedestrian_data.append(button[0])
            if len(pedestrian_data) >= 2:
                if button[0] > pedestrian_data[-1]:
                    pass
                    # print("Button pressed!")
                elif button[0] < pedestrian_data[1]:
                    pass
                    # print("Button released!")
            # --------  ULTRASONIC  -------------
            sumSpeed = 0
            # board.set_pin_mode_sonar(triggerPin,echoPin,timeout=200000)
            # result = board.sonar_read(triggerPin)     
            # result = [[1, 0], [5, 1], [7, 2] ,[9, 3], [13, 4], []]
            if i >= 1:  
                if ultrasonicData[-1][0] == 60 and result[0] < 60:
                    print("Object detected in range")
                if ultrasonicData[-1][0] < 60 and result[0] == 60:
                    print("Object has left range")
            ultrasonicData.append(result)
            result = [random.randint(1, 5), result[1]+1]
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

def display_graph(data):

    if len(data) < 20:
        print("Insufficient data. Please wait 20 seconds in the polling loop before trying again.")
        return

    ultrasonic_times = []
    ultrasonic_distances = [] 

    # take only the last 20 seconds
    u_data = data[len(data)-20:]

    for i in range(0, len(u_data)-1): # add time values to the time_values list
        ultrasonic_times.append(u_data[i][1])
        ultrasonic_distances.append(u_data[i][0])

    plt.title("Distance to oncoming traffic vs Time")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Distance (cm)")

    plt.plot(ultrasonic_times, ultrasonic_distances)

    return plt.show()

def led_status(): #TODO: Check over function and ensure it works
    """
    Function name: led_status
    
    Description: Checks which main road, side road and pedestrian LEDs are currently on/off, and changes their status based on the current stage of operation

    Returns: ledStatus (list): the list of current LEDs that are on 
    """
    global currentStage, mainRoadLights, sideRoadLights, pedestrianLights, stageChangeCycles
    while True:
        if stageChangeCycles == 0:
            i = 0
            while i in range(len(stageList)):
                nextStage = currentStage + 1
                if currentStage == 6:
                    nextStage = 1
                    mainRoadLights = ledDict[nextStage][0]
                    sideRoadLights = ledDict[nextStage][1]
                    pedestrianLights= ledDict[nextStage][2]
                elif nextStage == stageList[i]:
                    if nextStage == 2:
                        mainRoadLights = ledDict[nextStage][0]
                        sideRoadLights = ledDict[nextStage][1]
                        pedestrianLights= ledDict[nextStage][2]
                    elif nextStage == 3:
                        mainRoadLights = ledDict[nextStage][0]
                        sideRoadLights = ledDict[nextStage][1]
                        pedestrianLights= ledDict[nextStage][2]
                    elif nextStage == 4:
                        mainRoadLights = ledDict[nextStage][0]
                        sideRoadLights = ledDict[nextStage][1]
                        pedestrianLights= ledDict[nextStage][2]
                    elif nextStage == 5:
                        mainRoadLights = ledDict[nextStage][0]
                        sideRoadLights = ledDict[nextStage][1]
                        pedestrianLights= ledDict[nextStage][2]
                    elif nextStage == 6:
                        mainRoadLights = ledDict[nextStage][0]
                        sideRoadLights = ledDict[nextStage][1]
                        pedestrianLights= ledDict[nextStage][2]
            break
        else:
            continue

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
    services()