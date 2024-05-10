# File name: main.py 
# Purpose: Contains the traffic light system logic 
# Version '0.0' - Edited By: 'James Armit' (09/04/24) - file created with polling loop and control subsystem
# Version '1.0' - Edited By: 'Karthik Vaideeswaran' (09/04/24) - created function led_status for m2p1
# Version '2.0' - Edited By: 'Binuda Kalugalage' (10/04/2024) - added maintenance_mode, fixed display_graph, added dummy button (ped) + ultrasonic data for m2p1
# Version '3.0' - Edited By: 'James Armit' (21/04/24) - hardware integration
# Version '4.0' - Edited By: 'Binuda Kalugalage' (21/04/2024) - improved maintenance and services functions' logic; improved system parameter handling and console readability
# Version '4.2' - Edited By: 'James Armit' (21/04/2024) - Fixed up necessary deliverables for MVP
# Version '4.3' - Edited By: 'Karthik Vaideeswaran' (08/05/2024) - Added LDR, Thermistor and 2nd Ultrasonic Sensor Data Collection
# Version '4.4' - Edited By: 'Karthik Vaideeswaran' (09/05/2024) - Updated Thermisor and LDR data collection to update stageChangeCycles according to temperature and light level, respectively

#--- IMPORT MODULES ----
import time
from pymata4 import pymata4
import matplotlib.pyplot as plt
import math

board = pymata4.Pymata4()

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
failCount = 0

# -- VARIABLE DICTIONARY CONTATINING DEFAULT VALUES -- 
# This dictionary is the one which can be updated in the services subsection
# Only editable variables should be in this dictionary 
systemVariables = {
    'pollCycles' : 12,
    'pollInterval' : 0.05,
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

ldrFinal = []
tempData = []

ultrasonicDataDistance = []
ultrasonicDataHeight = []
ultrasonicPlaceholder = []
speedData = []

#Steinhart-Hart Equation Coefficients
A = 1.1279/1000
B = 2.3429/10000
C = 8.7298/(10**8)

def seven_seg_display_placeholder(message):
    """
    Function: seven_seg_display_placeholder

    Descrpition: A placeholder function which provides console outputs where the 7 segment display would be updated. 
    During demonstration, the outputs of this function can be typed immediatly into the 7 segment display file

    Parameters: message (string): A 4 character message which can include any alphanumeric characters. If the string is longer than
    4 characters, any characters after 4 are ignored

    Returns: None
    """
    print("\n--- 7 SEG DISPLAY OUTPUT ---")
    if type(message) == str:
        if len(message) != 4:
            message = message[:,4]
        print(f"Message displayed: '{message}'")
    else:
        print("Message must be a string")

def display_graph(ultrasonic, graph_type):
    """
    Function: display_graph

    Description: Called in Data Observation to produce a graph of the last 20 seconds of ultrasonic sensor data

    Parameters: ultrasonic (list) a list containing the past 20 seconds of ultrasonic data 

    Returns: None 
    """
    global dataStorage
    xAxisData = []
    timeData = []

    firstTime = ultrasonic[0][0][1]

    for j in range(len(ultrasonic)):
        for i in ultrasonic[j]:
            xAxisData.append(i[0])
            timeData.append((i[1]-firstTime))

    if len(timeData) < 7:
       print("\nInsufficient data. Please wait 20 seconds in the polling loop before trying again.\n")
       time.sleep(2)
       return
    
    try:
        if graph_type == "D":
            plt.title("Distance from oncoming traffic vs Time")
            plt.ylabel("Height (cm)")
        elif graph_type == "H":
            plt.title("Height of vehicle vs Time")
            plt.ylabel("Height (cm)")



        plt.plot(timeData[-80:-1],xAxisData[-80:-1], marker="o")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Distance (cm)")
        plt.grid(True)
        plt.show() 

        plt.savefig("Ultrasonic Data.png")

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
    while True:
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
                    inputDataDistance = []
                    inputDataHeight = []
                    try:
                        for i in range(len(dataStorage[0])):
                            inputDataDistance.append(dataStorage[i]['data']['ultrasonicDistance'])
                            inputDataHeight.append(dataStorage[i]['data']['ultrasonicHeight'])

                        print(inputDataHeight)
                        
                        while True:
                            graph = input("Would you like to display Distance or Height? (D/H): ")

                            if graph == "D":
                                display_graph(inputDataDistance, "D").savefig("Ultrasonic_Data_Distance.png")
                                break
                            elif graph == "H":
                                display_graph(inputDataHeight, "H").savefig("Ultrasonic_Data_Distance.png")
                                break
                            else:
                                continue

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

    seven_seg_display_placeholder("adjt")

    global failCount, systemVariables, currentData,systemVariables,pollCycles,pollInterval,stage1Duration,stage4Duration

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
                        seven_seg_display_placeholder("Locd")
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
        maxHeight (int): the maximum height of a passing vechile before over-height led is triggered
    Returns: 
        ouput (dictionary): contains the arrays output by each sensor to be interpreted in the polling loop
    
    """
    try:
        global pedestrians,currentStage
        global pollTime
        global pulseOn
        global ldrData, thermData
        triggerPinDistance = 5
        echoPinDistance = 4
        triggerPinHeight = 2
        echoPinHeight = 1
        pedestrians = 0
        for i in range(int(round(cycles*4))):
            # --------  FLASHING ----------
            if currentStage == 5:
                board.set_pin_mode_digital_output(7)
                if pulseOn == True:
                    board.digital_write(7,1)
                    pulseOn = False
                elif pulseOn == False:
                    board.digital_write(7,0)
                    pulseOn = True 
            # -------- PEDESTRIANS -------
            board.set_pin_mode_digital_input(3)
            pedButton = 3
            button = board.digital_read(pedButton)
            pedestrianData.append(button[0])
            #print(pedestrianData)
            if len(pedestrianData) >= 2:
                if button[0] > pedestrianData[-1]:
                    print("Button pressed!")
                elif button[0] < pedestrianData[1]:
                    print("Button released!")
            # --------  ULTRASONIC-DISTANCE  -------------
            speedData = []
            sumSpeed = 0
            board.set_pin_mode_sonar(triggerPinDistance,echoPinDistance,timeout=250000)
            resultDistance = board.sonar_read(triggerPinDistance)     
            #if i >= 3:  
            #    if ultrasonicData[-1][0] == 60 and result[0] < 60:
            #        print("Object detected in range")
            #    if ultrasonicData[-1][0] < 60 and result[0] == 60:
            #        print("Object has left range")
            
            #print(f"The nearest object is {result[0]} cm away at {result[1]}")
            # Find the change in distance and time over one inteval
            # Note that ultrasonicData[-1] = ultrasonicData[-2] for some reason

            # --------- ULTRASONIC-HEIGHT ------------
            board.set_pin_mode_sonar(triggerPinHeight,echoPinHeight,timeout = 250000)
            resultHeight = board.sonar_read(triggerPinHeight)
            resultHeight[0] = 28 - resultHeight[0]


            # if resultHeight[0] > maxHeight:
            #     #Do stuff


            # if resultHeight[0] > 0:
            #     #Display resultHeight on 7-SEG
            # else:
            #     pass
            # --------- SPEED ------------
            if i >= 2:
                try:
                    deltaD = abs(resultDistance[0] - ultrasonicDataDistance[-1][0])
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
                ultrasonicDataHeight.append(resultHeight)
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
                thermFinal.append(thermData[num][0])
            
            #Calculae Resistance
            for n in range(len(thermFinal)):
                thermRes = 10000*(thermFinal[n]/(1023-thermFinal[n]))
                resistanceData.append(thermRes)
            
            #Find Temperature
            for m in range(len(resistanceData)):
                if resistanceData[m] > 0.0:
                    invTemp = A + (B*(math.log(resistanceData[n]))) + (C*((math.log(resistanceData[n]))**3))
                    temp = 1/invTemp - 273.15
                    tempData.append(temp)
                else:
                    continue

        #---------OUTPUT DICTIONARY--------- 
        output = {
            'pedestrian': pedestrianData,
            'ultrasonicDistance': ultrasonicDataDistance,
            'ultrasonicHeight': ultrasonicDataHeight,
            'LDR': ldrFinal,
            'Temperature': tempData
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
    """
    Function name: stage 1

    Description: A function which sets the colours of the LED lights and resets the number of cycles to stage change

    Parameters: None 
    Returns: None
    """
    global currentStage,mainRoadLights,sideRoadLights,pedestrianLights,pedestrians,stageChangeCycles, tempData
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

    seven_seg_display_placeholder("stg1")

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

    seven_seg_display_placeholder("stg2")

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

    seven_seg_display_placeholder("stg3")

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

    seven_seg_display_placeholder("stg4")

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

    seven_seg_display_placeholder("stg5")

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
    print(f"\n-----------------\n    STAGE {currentStage}   \n-----------------")

def update_LED_placeholder(ledDict):
    """
    Function: update_LED_placeholder

    Description: Sends a 0V output to all pins associated with LED's before selectivley turning the necessary LED's on 
    as per the value of the main, side and pedestrian lights

    Parameters: ledDict (dict) a dictionary with the current colours of the main, side and pedestrian lights as per the stage

    Returns: None
    """
    global currentStage
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
        },
        'pedestrian': {
            "Green": 7,
            "Red": 6
        }
    }
    for keys in ledDict:
        print(f"{keys} is set to {ledDict[keys]} LED active")
    for i in range(6,14):
        board.set_pin_mode_digital_output(i)
        board.digital_write(i,0)
    board.digital_write(ledMapping['main'][mainRoadLights],1)
    board.digital_write(ledMapping["side"][sideRoadLights],1)
    board.digital_write(ledMapping["pedestrian"][pedestrianLights],1)
    


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
            if len(dataStorage) > storageMaxSize:
                dataStorage.remove(dataStorage[0])
                                    
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
            ledDict = {
                'Main Road Light': mainRoadLights,
                'Side Road Light': sideRoadLights,
                'Pedestrian Light': pedestrianLights
            }

            update_LED_placeholder(ledDict)

            delayTime = cycleDuration - pollTime
            print(f"The sensor poll took {pollTime:.2f} seconds")
            stageChangeCycles -= 1 
            time.sleep(delayTime)
    except KeyboardInterrupt:
        services()
        return
    
if __name__ == "__main__":
    services()
