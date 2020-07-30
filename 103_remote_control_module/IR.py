#!/usr/bin/python3
import time
import serial
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.sql import select, func

print("Recive IR UART")
serial_port = serial.Serial(
    port="/dev/ttyTHS1",
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
)
# Wait a second to let the port initialize
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

zaehler = 1
try:
    # Send a simple header
    serial_port.write("UART Demonstration Program\r\n".encode())
    serial_port.write("NVIDIA Jetson Nano Developer Kit\r\n".encode())
    
    while True:
        selection = select(
            [MAIN_OCCUPANCY.c.id, MAIN_OCCUPANCY.c.capacity, MAIN_OCCUPANCY.c.person_count, MAIN_OCCUPANCY.c.direction, func.max(MAIN_OCCUPANCY.c.id)])
        for i in CONN.execute(selection):
            capacity = i['capacity']
            latest_person_count =  i['person_count']
            direction =  i['direction']

        if serial_port.inWaiting() > 0:
            data = serial_port.read()
            #print(data.decode('utf-8'))
            if data.decode('utf-8') == '1': 
                print(1)
            if data.decode('utf-8') == '2':
                zaehler = 1 
                print("1er")
            if data.decode('utf-8') == '3':
                zaehler = 10 
                print("10er")

            if data.decode('utf-8') == '5':
                capacity = capacity + 1*zaehler
                print(capacity)
            if data.decode('utf-8') == '6': 
                capacity = capacity - 1*zaehler
                print(capacity)
    
            if data.decode('utf-8') == '7':
                latest_person_count = latest_person_count - 1*zaehler 
                print(latest_person_count)
            if data.decode('utf-8') == '8': 
                latest_person_count = latest_person_count + 1*zaehler 
                print(latest_person_count)

            if data.decode('utf-8') == '9': 
                print(direction)
        # write message into db    
       
        now = datetime.now()
        now = now.replace(microsecond=0)
        insert = MAIN_OCCUPANCY.insert().values(capacity=capacity, date=now, person_count=latest_person_count, direction=direction)
        CONN.execute(insert)

except KeyboardInterrupt:
    print("Exiting Program")

except Exception as exception_error:
    print("Error occurred. Exiting Program")
    print("Error: " + str(exception_error))

finally:
    serial_port.close()
    pass