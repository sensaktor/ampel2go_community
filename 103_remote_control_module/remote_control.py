#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time, threading 
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.sql import select, func

#zaehler = 1

time.sleep(1)
CONN = create_engine('sqlite:////home/jetson/Desktop/ampel2go_code/104_user_display/db.sqlite3')
META_DATA = MetaData(bind=CONN)
MAIN_OCCUPANCY = Table(
    'main_occupancy', META_DATA,
    Column('id', Integer, primary_key=True),
    Column('capacity', Integer), 
    Column('date', DateTime),
    Column('person_count', Integer),
    Column('direction', Integer),
    )

class IRRemote:    

    def __init__(self, callback = None):        

        self.decoding = False
        self.pList = []
        self.timer = time.time()
        if callback == 'DECODE':
            self.callback = self.print_ir_code
        else:
            self.callback = callback
        self.checkTime = 150  # time in milliseconds
        self.verbose = False
        self.repeatCodeOn = True
        self.lastIRCode = 0
        self.maxPulseListLength = 70

    def pWidth(self, pin):
        """pWidth, function to record the width of the highs and lows
        of the IR remote signal and start the function to look for the
        end of the IR remote signal"""

        self.pList.append(time.time()-self.timer)
        self.timer = time.time()        

        if self.decoding == False:
            self.decoding = True
            check_loop = threading.Thread(name='self.pulse_checker',target=self.pulse_checker)
            check_loop.start()           
            
        return

    def pulse_checker(self):
        """pulse_checker, function to look for the end of the IR remote
        signal and activate the signal decode function followed by
        the callback function.

        End of signal is determined by 1 of 2 ways
        1 - if the length of the pulse list is larger than self.maxPulseListLength
          - used for initial button press codes
        2 - if the length of time receiving the pulse is great than self.checkTime
          - used for repeat codes"""

        timer = time.time()

        while True:                
                check = (time.time()-timer)*1000
                if check > self.checkTime:                    
                #    print(check, len(self.pList))
                    break
                if len(self.pList) > self.maxPulseListLength:
                #    print(check, len(self.pList))
                    break
                time.sleep(0.001)

        if len(self.pList) > self.maxPulseListLength:
            decode = self.decode_pulse(self.pList)
            self.lastIRCode = decode

        # if the length of self.pList is less than 10
        # assume repeat code found
        elif len(self.pList) < 10:
            if self.repeatCodeOn == True:
                decode = self.lastIRCode
            else:
                decode = 0
                self.lastIRCode = decode
        else:
            decode = 0
            self.lastIRCode = decode

        self.pList = []
        self.decoding = False

        if self.callback != None:
            self.callback(decode)
        
        return

    def decode_pulse(self,pList):
        """decode_pulse,  function to decode the high and low
        timespans captured by the pWidth function into a binary
        number"""

        bitList = []
        sIndex = -1

        # convert the timespans in seconds to milli-seconds
        # look for the start of the IR remote signal
        
        for p in range(0,len(pList)):
            try:
                pList[p]=float(pList[p])*1000
                if self.verbose == True:
                    print(pList[p])
                if pList[p]<11:
                    if sIndex == -1:
                        sIndex = p
            except:            
                pass

        # if no acceptable start is found return -1

        if sIndex == -1:
            return -1

        if sIndex+1 >= len(pList):
            return -1
        
        #print(sIndex, pList[sIndex], pList[sIndex+1])

        if (pList[sIndex]<4 or pList[sIndex]>11):
            return -1

        if (pList[sIndex+1]<2 or pList[sIndex+1]>6):
            return -1

        """ pulses are made up of 2 parts, a fixed length low (approx 0.5-0.6ms)
        and a variable length high.  The length of the high determines whether or
        not a 0,1 or control pulse/bit is being sent.  Highes of length approx 0.5-0.6ms
        indicate a 0, and length of approx 1.6-1.7 ms indicate a 1"""    
        
           
        for i in range(sIndex+2,len(pList),2):
            if i+1 < len(pList):
                if pList[i+1]< 0.9:  
                    bitList.append(0)
                elif pList[i+1]< 2.5:
                    bitList.append(1)
                elif (pList[i+1]> 2.5 and pList[i+1]< 45):
                    #print('end of data found')
                    break
                else:
                    break

        #if self.verbose == True:
        #    print(bitList)

        # convert the list of 1s and 0s into a
        # binary number

        pulse = 0
        bitShift = 0

        for b in bitList:            
            pulse = (pulse<<bitShift) + b
            bitShift = 1        

        return pulse

    def set_callback(self, callback = None):
        """set_callback, function to allow the user to set
        or change the callback function used at any time"""

        self.callback = callback

        return

    def remove_callback(self):
        """remove_callback, function to allow the user to remove
        the callback function used at any time"""

        self.callback = None

        return

    def print_ir_code(self, code):
        """print_ir_code, function to display IR code received"""

        #print(hex(code))

        return

    def set_verbose(self, verbose = True):
        """set_verbose, function to turn verbose mode
        on or off. Used to print out pulse width list
        and bit list"""

        self.verbose = verbose

        return

    def set_repeat(self, repeat = True):
        """set_repeat, function to enable and disable
        the IR repeat code functionality"""

        self.repeatCodeOn = repeat

        return

zaehler = 1
def writeDB(x):
    selection = select(
        [MAIN_OCCUPANCY.c.id, MAIN_OCCUPANCY.c.capacity, MAIN_OCCUPANCY.c.person_count, MAIN_OCCUPANCY.c.direction, func.max(MAIN_OCCUPANCY.c.id)])
    for i in CONN.execute(selection):
        capacity = i['capacity']
        latest_person_count =  i['person_count']
        direction =  i['direction']
    
    if x == 1: 
        print(1)
    if x == 2:
        zaehler = 1 
        #print("1er")
    if x == 3:
        zaehler = 10 
        #print("10er")

    if x == 5:
        capacity = capacity + 1
        #print(capacity)
    if x == 6: 
        capacity = capacity - 1
        #print(capacity)
    
    if x == 7:
        latest_person_count = latest_person_count - 1 
        #print(latest_person_count)
    if x == 8: 
        latest_person_count = latest_person_count + 1 
        #print(latest_person_count)

    if x == 9: 
        direction = direction* -1
        #print(direction)
    time.sleep(0.5)

    now = datetime.now()
    now = now.replace(microsecond=0)
    insert = MAIN_OCCUPANCY.insert().values(capacity=capacity, date=now, person_count=latest_person_count, direction=direction)
    CONN.execute(insert)

if __name__ == "__main__":

    def remote_callback(code):        
        #print(hex(code))
      
        if code == 0xff629d:
            writeDB(1)
            #print("Power")
        elif code == 0xff22dd:
            #print('A')
            writeDB(2)
        elif code == 0xff02fd:
            #print('B')
            writeDB(3)
        elif code == 0xffc23d:
            #print('C')
            writeDB(4)
        elif code == 0xff9867:
            #print('Up Arrow')
            writeDB(5)
        elif code == 0xff38c7:
            #print('Down Arrow')
            writeDB(6)
        elif code == 0xff30cf:
            #print('Left Arrow')
            writeDB(7)
        elif code == 0xff7a85:
            #print('Right Arrow')
            writeDB(8)
        elif code == 0xff18e7:
            #print('Select')
            writeDB(9)
        else:
            print('.')  # unknown code

        return

    ir = IRRemote('DECODE')  
            
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)  # uses numbering outside circles
    GPIO.setup(16,GPIO.IN)   # set pin 16 to input
    GPIO.add_event_detect(16,GPIO.BOTH,callback=ir.pWidth)

    #ir.set_verbose()
    print('Starting IR remote sensing using DECODE function')

    time.sleep(5)
    print('Setting up callback')
    ir.set_verbose(False)
    ir.set_callback(remote_callback)
    ir.set_repeat(True)

    try:

        while True:
            time.sleep(1)

    except:
        print('Removing callback and cleaning up GPIO')
        ir.remove_callback()
        GPIO.cleanup(16)