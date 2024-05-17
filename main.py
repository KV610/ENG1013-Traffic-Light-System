# File name: main.py 
# Purpose: Contains the traffic light system logic 
# Version '0.0' - Edited By: 'James Armit' (09/04/24) - file created with polling loop and control subsystem
# Version '1.0' - Edited By: 'Karthik Vaideeswaran' (09/04/24) - created function led_status for m2p1
# Version '2.0' - Edited By: 'Binuda Kalugalage' (10/04/2024) - added maintenance_mode, fixed display_graph, added dummy button (ped) + ultrasonicDistance data for m2p1
# Version '3.0' - Edited By: 'James Armit' (21/04/24) - hardware integration
# Version '4.0' - Edited By: 'Binuda Kalugalage' (21/04/2024) - improved maintenance and services functions' logic; improved system parameter handling and console readability
# Version '4.2' - Edited By: 'James Armit' (21/04/2024) - Fixed up necessary deliverables for MVP
# Version '5.0' - Edited By: 'James Armit' (16/05/2024) - Introduced Milestone 3 

#--- IMPORT MODULES ----
import time
from pymata4 import pymata4
import matplotlib.pyplot as plt
import math

import seven_segment_display as ss

board = pymata4.Pymata4()

allPins = [2, 3, 6, 7, 8, 9, 10]
for pin in allPins:
    board.set_pin_mode_digital_output(pin)


#   ----------------------- INITIALISE GLOBAL VARIABLES AND VARIABLE DICTIONARY------------------------------
pedestrians = 0
pollTime = 0
pollCycles = 3
pollInterval = 0.2
currentStage = 1 
stageChangeCycles = 2
stage1Duration = 2
stage2Duration = 1
stage3Duration = 1
stage4Duration = 2
stage5Duration = 1
stage6Duration = 1
cycleDuration = 3.00
mainRoadLights = "Green"
sideRoadLights = "Red"
pedestrianLights = "Red"
storageMaxSize = 2
pulseOn = True
closeDistance = 10
lastHeightBreach = None

RGBPin = 11
buzzerPin = 10
maxHeight = 15 #Changeable
vehicleHeight = 0

failCount = 0


# -- VARIABLE DICTIONARY CONTATINING DEFAULT VALUES -- 
# This dictionary is the one which can be updated in the services subsection
# Only editable variables should be in this dictionary 
systemVariables = {
    'pollCycles' : 1,
    'pollInterval' : 0.2,
    'stage1Duration': 2,
    'stage2Duration': 1,
    'stage3Duration': 1,
    'stage4Duration': 2,
    'stage5Duration': 1,
    'stage6Duration': 1,
    'cycleDuration': 3.00,
    'storageMaxSize': 2,
    "presetPIN": 2005,
    "maxPinAttempts": 3, 
    "lockedTime": 5
}




dataStorage = []
currentData = {}

pedestrianData = []

ultrasonicDataDistance = []
ultrasonicDataHeight = []

ldrFinal = []
tempData = []
ultrasonicPlaceholder = []
speedData = []

# Steinheart - Hart Coefficients
A = 1.1279/1000
B = 2.3429/10000
C = 8.7298/(10**8)



def display_graph(inputData, graph_type):
    """
    Function: display_graph

    Description: Called in Data Observation to produce a graph of the last 20 seconds of ultrasonic sensor data

    Parameters: ultrasonic (list) a list containing the past 20 seconds of ultrasonic data 

    Returns: None 
    """
    global dataStorage
    yAxisData = []
    timeData = []
    
    print(inputData)
    if graph_type != "T":
        firstTime = inputData[0][0][1]
        for j in range(len(inputData)):
            for i in inputData[j]:
                yAxisData.append(i[0])
                timeData.append((i[1]-firstTime))

    else:
        firstTime = inputData[0][0]
        print(inputData[0])
        for i in inputData[0]:
            # if i not in yAxisData:
            #     yAxisData.append(i)
            if inputData[0].index(i) not in timeData and i not in yAxisData:
                timeData.append(inputData[0].index(i))
                yAxisData.append(i)

        # for j in range(len(inputData)):
        #     for i in inputData[j]:
        #         yAxisData.append(i)
        #         timeData.append((i[1]-firstTime))

    if len(timeData) < 7:
       print("\nInsufficient data. Please wait 20 seconds in the polling loop before trying again.\n")
       time.sleep(2)
       return
    
    try:
        if graph_type == "D":
            plt.title("Distance from oncoming traffic vs Time")
            plt.ylabel("Distance (cm)")
            saveTitle = "Ultrasonic_Distance_Data.png"

        elif graph_type == "H":
            plt.title("Height of vehicle vs Time")
            plt.ylabel("Distance (cm)")
            saveTitle = "Ultrasonic_Height_Data.png"
        
        elif graph_type == "T":
            plt.title("Temperature vs Time")
            plt.ylabel("Temperature (°C)")
            saveTitle = "Temperature_Data.png"



        plt.plot(timeData[-80:-1],yAxisData[-80:-1], marker="o")
        plt.xlabel("Time (seconds)")
        plt.grid(True)
        plt.show() 

        plt.savefig(f"{saveTitle}.png")

        return plt
    except IndexError:
        print("\nInsufficient Data")
        time.sleep(2)

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
    serPin = 11
    srclk = 12
    rclk = 13
    board.set_pin_mode_digital_output(serPin)
    board.set_pin_mode_digital_output(srclk)
    board.set_pin_mode_digital_output(rclk)
    board.set_pin_mode_digital_output(14)
    ledList = [1,0,0,1,0,0,1,0]
    for i in ledList:
        board.digital_write(serPin,i)
        board.digital_write(srclk,0)
        board.digital_write(srclk,1)
    board.digital_write(rclk,0)
    board.digital_write(rclk,1)
    board.digital_pin_write(14,1)
    while True:

        ss.display_message("Services", 'static', "01001001", board, 1, False)
        board.set_pin_mode_digital_output(14)
        board.digital_pin_write(14,1)

        print("\n---------------------------")
        print("SYSTEM MENU                ")
        print("---------------------------")   
        print("[1] Normal \n[2] Maintenance \n[3] Data Observation \n*Type 'end' to end program")
        print("---------------------------\n")

        try:
            mode = input("Please select the mode you would like to enter: ")


            if mode == 'end':
                print("Shutting down...")
                serPin = 11
                srclk = 12
                rclk = 13
                board.set_pin_mode_digital_output(serPin)
                board.set_pin_mode_digital_output(srclk)
                board.set_pin_mode_digital_output(rclk)
                ledList = [0,0,0,0,0,0,0,0]
                for i in ledList:
                    board.digital_write(serPin,i)
                    board.digital_write(srclk,0)
                    board.digital_write(srclk,1)
                board.digital_write(rclk,0)
                board.digital_write(rclk,1)
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
                    board.digital_pin_write(14,0)
                    main()
                elif mode == 2:
                    print("\nEntering maintenance mode...")
                    maintenance()
                elif mode == 3:
                    inputDataDistance = []
                    inputDataHeight = []
                    inputDataTemp = []
                    print("\nEntering data observation mode...\n")
                    inputData = []
                    try:
                        for i in range(len(dataStorage[0])):
                            inputDataDistance.append(dataStorage[i]['data']['ultrasonicDistance'])
                            inputDataHeight.append(dataStorage[i]['data']['ultrasonicHeight'])
                            inputDataTemp.append(dataStorage[i]['data']['Temperature']),
                        
                        while True:
                            graph = input("Would you like to display Distance, Height or Temperature? (D/H/T): ")
                                
                            if graph == "D":
                                display_graph(inputDataDistance, "D")
                                break
                            elif graph == "H":
                                display_graph(inputDataHeight, "H")
                                break
                            elif graph == "T":
                                display_graph(inputDataTemp, "T")
                                break

                        print("Graph displayed")
                    except IndexError:
                        print("\nNo data available to graph, please run normal operations for at least 20 seconds\n")
                        time.sleep(0.5)
                else:
                    print("\nPlease select one of the shown modes.\n")
                    time.sleep(1)
                    continue
        except KeyboardInterrupt:
            continue

def update_system_variables(updatedVariables):
    """
    Function: update_system_variables

    Description: Called to update the global variables of the file to the values found in systemVariables. 
    This allows the modified variables from maintenence to be saved, displayed and used.

    Parameters: updatedVariables (dict) An updated list of variables passed in from maintenence (AS OF V4.1, THIS IS NOT RELEVANT)

    Returs: None
    """
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

def maintenance():
    """
    Function name: maintenance_mode
    
    Description: This function contains the logic for the maintenance mode.
                 System parameters can be modified through this function.
    
    Parameters: None

    Returns: None
    """

    global failCount, systemVariables, currentData,systemVariables,pollCycles,pollInterval,stage1Duration,stage4Duration

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
                                chosenValue = float(input(f"Please enter the value you would like to set '{chosenKey}' to: "))
                                systemVariables[chosenKey] = chosenValue
                                update_system_variables(systemVariables)

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
                        ss.display_message("Locked", '3.252', "00000000", board, systemVariables['lockedTime'], True)
                        # time.sleep(systemVariables['lockedTime'])
                        failCount = 0
                    else:
                        print("\nIncorrect PIN. Please try again.")
                        # time.sleep(1)
                    continue
        except KeyboardInterrupt:
            print()
            continue



def ultrasonic_max_height_check(heightResult, maximumHeight):
    """
    Function name: ultrasonic_max_height_check

    Description: This function checks the recent height measurement from the 2nd ultrasonicDistance to trigger led and buzzer


    Parameters:
        heightResult(int): most recent height measurement
        maximumHeight(int): the maximum height before led and buzzer is triggered
    
    Returns:
        None
    """
    global lastHeightBreach
    print(heightResult)
    if heightResult > maximumHeight:
        print("Vehicle too high")
        board.digital_write(RGBPin,1)
        board.digital_write(buzzerPin,1)
        lastHeightBreach = time.time()
    if lastHeightBreach is not None and time.time() - lastHeightBreach >= 6:
        board.digital_write(RGBPin,0)
    if lastHeightBreach is not None and time.time() - lastHeightBreach >= 2:
        board.digital_write(buzzerPin,0)





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
        global pedestrians,currentStage
        global pollTime
        global pulseOn
        triggerPinDistance = 5
        echoPinDistance = 4
        triggerPinHeight = 13
        echoPinHeight = 12
        for i in range(int(round(cycles*4))):
            # --------  FLASHING ----------
            # This software version should/could be replaced with hardware logic 
            # Since flashing lights will have to be done for the maintenence lights anyways
            if currentStage == 5:
                serPin = 11
                srclk = 12
                rclk = 13
                board.set_pin_mode_digital_output(serPin)
                board.set_pin_mode_digital_output(srclk)
                board.set_pin_mode_digital_output(rclk)
                pulseONList = "00101010"
                pulseOFFList = "00101000"
                if pulseOn == True:
                    ss.display_message("stg5", str(lastHeightBreach), pulseONList, board, 1, False)
                    pulseOn = False
                elif pulseOn == False:
                    ss.display_message("stg5", str(lastHeightBreach), pulseOFFList, board, 1, False)
                    pulseOn = True 
            # -------- PEDESTRIANS -------
            #-------LDR---------
            ldrData = []    
            #set pins
            ldrPin = 3
            board.set_pin_mode_analog_input(ldrPin) 
            #store data to a variable
            ldrResult = board.analog_read(ldrPin)   
            #append input data to list
            ldrData.append(ldrResult)   
            #Loop through thermData to separate signal readings and append to thermFinal
            for k in range(len(ldrData)):
                ldrFinal.append(ldrData[k][0])
            #-------THERMISTOR-------
            thermData = []  
            #set pins
            thermPin = 4
            board.set_pin_mode_analog_input(thermPin)   
            #store data to a variable
            thermResult = board.analog_read(thermPin)   
            #append input data to list
            thermData.append(thermResult)   
            #Loop through thermData to separate signal readings and append to thermFinal
            thermFinal = []
            resistanceData = []
            for num in range(len(thermData)):
                thermFinal.append([thermData[num][0],time.time()])

            #Calculae Resistance
            for n in range(len(thermFinal)):
                thermRes = 10000*(thermFinal[n][0]/(1023-thermFinal[n][0]))
                resistanceData.append(thermRes)

            #Find Temperature
            for m in range(len(resistanceData)):
                if resistanceData[m] > 0.0:
                    invTemp = A + (B*(math.log(resistanceData[n]))) + (C*((math.log(resistanceData[n]))**3))
                    temp = 1/invTemp - 273.15
                    tempData.append(temp)
                else:
                    continue
            # --------  ULTRASONIC DISTANCE  -------------
            speedData = []
            sumSpeed = 0
            board.set_pin_mode_sonar(triggerPinDistance,echoPinDistance,timeout=250000)
            resultDistance = board.sonar_read(triggerPinDistance)     
            #if i >= 3:  
            #    if ultrasonicDataDistance[-1][0] == 60 and resultDistance[0] < 60:
            #        print("Object detected in range")
            #    if ultrasonicDataDistance[-1][0] < 60 and resultDistance[0] == 60:
            #        print("Object has left range")

            #print(f"The nearest object is {resultDistance[0]} cm away at {resultDistance[1]}")
            # Find the change in distance and time over one inteval
            # Note that ultrasonicDataDistance[-1] = ultrasonicDataDistance[-2] for some reason

             # --------  ULTRASONIC-HEIGHT ----------------
            board.set_pin_mode_sonar(triggerPinHeight,echoPinHeight, timeout=250000)
            resultHeight = board.sonar_read(triggerPinHeight)
            print(resultHeight)
            if resultHeight[0] != 0:
                resultHeight[0] = 28 - resultHeight[0]
                if resultHeight[0] < 0:
                    resultHeight[0] = 0
                
                if resultHeight[0] > 0:
                    vehicleHeight = resultHeight[0]
                
                ultrasonic_max_height_check(resultHeight[0], maxHeight)

            
            if i >= 2 and len(ultrasonicDataDistance) > 2:
                try:
                    deltaD = (resultDistance[0] - ultrasonicDataDistance[-1][0])
                    deltaT = resultDistance[1] - ultrasonicDataDistance[-1][1]
                    speed = deltaD / deltaT
                    if speed > 0.01:
                        #print(f"The current speed is {speed:.3f} cm/s")
                        speedData.append(speed)
                    else:
                        #print(f"No movement detected")
                        pass
                except ZeroDivisionError:
                    pass
            if resultDistance[1] != 0:
                ultrasonicDataDistance.append(resultDistance)   
            if resultHeight[1] != 0:
                ultrasonicDataHeight.append(resultHeight)   
            # ss.display_message(str(lastHeightBreach), "    ", board, intervalLength, False)
            time.sleep(intervalLength)
            pollTime += intervalLength

        for i in speedData:
            sumSpeed += i
        averageSpeed = sumSpeed / cycles * 4
        print(f"The average speed during the intervals was {averageSpeed:.3f} cm/s")
        for i in range(len(pedestrianData)):
            if pedestrianData[i] == 1:
                if pedestrianData[i] > pedestrianData[i-1]:
                    pedestrians += 1
        #print(f"{pedestrians} have pushed the button during the stage") - For debugging 
        
        output = {
            'pedestrian': pedestrianData,
            'ultrasonicDistance': ultrasonicDataDistance,
            'ultrasonicHeight': ultrasonicDataHeight,
            'LDR': ldrFinal,
            'Temperature': tempData
        }

        #print(tempData)
        # print(output)
        return output
    except KeyboardInterrupt:
        services()
        return


# TEST INPUTS / PLACEHOLDER FUNCTION
#def input_data_placeholder(cycles,intervalLength):
    """
    Function name: input_data_placeholder

    Description: Provides randomised input data from the pedestrian button and ultrasonicDistance sensor
    This data is random but has limits such that it will return a resultDistance that is within the boundries 
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
   #     'ultrasonicDistance' : ultrasonicPlaceholder,
   #     'pedestrian' : pedestrianPlaceholder
   # }
   # time.sleep((cycles*4)*intervalLength)
   # pollTime = 0
   # timestamp = ultrasonicPlaceholder[-1][1]
   # return output
    
def stage_1():
    """
    Function name: stage 1

    Description: A function which sets the colours of the LED lights and resets the number of cycles to stage change

    Parameters: None 
    Returns: None
    """
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 1

    mainRoadLights = "Green"
    sideRoadLights = "Red"
    pedestrianLights = "Red"

    pedestrians = 0

    for l in range(len(tempData)):
        if tempData[l] > 35.0:
            stageChangeCycles = stage1Duration + 2
        else:
            stageChangeCycles = stage1Duration

    for p in range(len(ldrFinal)):
        if ldrFinal[p] > 1000:
            stageChangeCycles = stage1Duration + 5
        else:
            stageChangeCycles = stage1Duration

    stageChangeCycles = stage1Duration


def stage_2():
    """
    Function name: stage 2

    Description: A function which sets the colours of the LED lights and resets the number of cycles to stage change

    Parameters: None 
    Returns: None
    """
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 2

    mainRoadLights = "Yellow"
    sideRoadLights = "Red"
    pedestrianLights = "Red"

    stageChangeCycles = stage2Duration

def stage_3():
    """
    Function name: stage 1

    Description: A function which sets the colours of the LED lights and resets the number of cycles to stage change

    Parameters: None 
    Returns: None
    """
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 3

    mainRoadLights = "Red"
    sideRoadLights = "Red"
    pedestrianLights = "Red"

    print(f"\nPedestrians detected: {pedestrians} ")

    stageChangeCycles = stage3Duration

    

def stage_4():
    """
    Function name: stage 1

    Description: A function which sets the colours of the LED lights and resets the number of cycles to stage change

    Parameters: None 
    Returns: None
    """
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 4

    mainRoadLights = "Red"
    sideRoadLights = "Green"
    pedestrianLights = "Green"

    for l in range(len(tempData)):
        if tempData[l] > 35.0:
            stageChangeCycles = stage4Duration + 2
        else:
            stageChangeCycles = stage4Duration
    
        for q in range(len(tempData)):
            if ldrFinal[q] > 1000:
                stageChangeCycles = stage4Duration + 3
            else:
                stageChangeCycles = stage4Duration

    stageChangeCycles = stage4Duration

    

def stage_5():
    """
    Function name: stage 1

    Description: A function which sets the colours of the LED lights and resets the number of cycles to stage change

    Parameters: None 
    Returns: None
    """
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 5

    mainRoadLights = "Red"
    sideRoadLights = "Yellow"
    pedestrianLights = "Green"

    stageChangeCycles = stage5Duration


def stage_6():
    """
    Function name: stage 1

    Description: A function which sets the colours of the LED lights and resets the number of cycles to stage change

    Parameters: None 
    Returns: None
    """
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles
    currentStage = 6

    mainRoadLights = "Red"
    sideRoadLights = "Red"
    pedestrianLights = "Red"

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
    print(f"\n-----------------\n    STAGE {currentStage}   \n-----------------")


def update_LED():
    """
    Function: update_LED_placeholder

    Description: Sends a 0V output to all pins associated with LED's before selectivley turning the necessary LED's on 
    as per the value of the main, side and pedestrian lights

    Parameters: ledDict (dict) a dictionary with the current colours of the main, side and pedestrian lights as per the stage

    Returns: None
    """
    global currentStage
    serPin = 11
    LED_SRCLK = 12
    LED_RCLK = 13
    board.set_pin_mode_digital_output(serPin)
    board.set_pin_mode_digital_output(LED_SRCLK)
    board.set_pin_mode_digital_output(LED_RCLK)
    ledDict = {
        1:[1,0,1,0,0,0,0,1],
        2:[1,0,1,0,0,0,1,0],
        3:[1,0,1,0,0,1,0,0],
        4:[0,1,0,0,1,1,0,0],
        5:[0,1,0,1,0,1,0,0],
        6:[1,0,1,0,0,1,0,0]
    }      
    # for i in ledDict[currentStage]:
    #     board.digital_write(serPin,i)
    #     board.digital_write(LED_SRCLK,0)
    #     board.digital_write(LED_SRCLK,1)
    # board.digital_write(LED_RCLK,0)
    # board.digital_write(LED_RCLK,1)

    return ''.join(str(x) for x in ledDict[currentStage][::-1])

    


def main():
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles,pollTime,dataStorage,closeDistance
    """
    Function name: main 

    Description: This function will contain the main polling loop which operates
    when the system is in Normal Operations. It will be constantly running unless 
    otherwise stopped so long as the file is not imported as a module

    Parameters: None 
    Returns: None 
    """
    # Keep the loop running infinitely 
    # If a Keyboard inturrupt is used, exit the program to services. Otherwise, keep running
    try:
        while True:

            # reset the value of 'currentData' to a blank dictionary
            currentData = {}
            # reset PollTime to 0
            pollTime = 0
            # call all input functions
            #   currentData['data'] = input_data(12,0.05)  THIS IS THE ACTUAL HARDWARE INTEGRATED FUNCTION
            # Add a header in the console
            print(f"\n-----------------\n    CYCLE     ")
            currentData['data'] = input_data(pollCycles,pollInterval)
            dataStorage.append(currentData)

            delayTime = cycleDuration - pollTime

            if len(dataStorage) > storageMaxSize:
                dataStorage.remove(dataStorage[0])
            # Check distance to vehicles at stage 
            lastPosition = currentData['data']['ultrasonicDistance'][-1][0]
            firstPosition = currentData['data']['ultrasonicDistance'][1][0]
            if currentStage == 1 and lastPosition == firstPosition:
                print(f"\n----- ALERT -----\nVehicle has not moved from {lastPosition} during green light")
            # Extend yellow light if vehicles are close
            #if currentStage == 2 and lastPosition <= closeDistance:
            #    stageChangeCycles += 1 
                                    
            if stageChangeCycles <= 0: # Check in case the duration is edited such that the value is now negative
                set_stage(currentStage)
            if pedestrians > 1:
                if currentStage == 1:
                    if currentData['data']['ultrasonicDistance'][-1][0] == 60 :
                        if stageChangeCycles > 2:
                            stageChangeCycles = 2
                else:
                    pass
            else:
                pass
            # print(f"Cycles to stage change: {stageChangeCycles}") - Only for debugging
            print(f"\nThe last object was detected at {currentData['data']['ultrasonicDistance'][-1][0]:.2f} cm")

            ss.display_message(f"Stage {currentStage}", str(lastHeightBreach), update_LED(), board, delayTime, True)

            print(f"The sensor poll took {pollTime:.2f} seconds")
            stageChangeCycles -= 1 
            # time.sleep(delayTime)
    except KeyboardInterrupt:
        services()
        return
    
if __name__ == "__main__":
    services()
