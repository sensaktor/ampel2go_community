import time
from datetime import datetime
import numpy as np
from sqlalchemy import create_engine, Table, Column, Integer, DateTime, String, MetaData, ForeignKey
from sqlalchemy.sql import select, func
import cv2
import Person

# Initialize sqlAlchem
CONN = create_engine('sqlite:////home/jetson/Desktop/ampel2go_code/104_user_display/db.sqlite3')
#CONN = create_engine('sqlite:////Users/fk/Desktop/ampel2go_code/104_user_display/db.sqlite3')

META_DATA = MetaData(bind=CONN)
MAIN_OCCUPANCY = Table(
    'main_occupancy', META_DATA,
    Column('id', Integer, primary_key=True),
    Column('capacity', Integer), Column('date', DateTime),
    Column('person_count', Integer),
    Column('direction', Integer),
    )

MAIN_AREATHRESHOLD = Table(
    'main_areathreshold', META_DATA,
    Column('id', Integer, primary_key=True),
    Column('area_threshold', Integer),
    )

# gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
# Defaults to 1280x720 @ 30fps
# Flip the image by setting the flip_method (most common values: 0 and 2)
# display_width and display_height determine the size of the window on the screen

try:
    LOG = open('LOG.txt', "w")
except FileNotFoundError:
    print("No se puede abrir el archivo log")


CNT_UP = 0
CNT_DOWN = 0

def gstreamer_pipeline(
        capture_width=1024,
        capture_height=600,
        display_width=820,
        display_height=500,
        framerate=21,
        flip_method=2,
    ):
    "resizing input video"
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

#PI CAM
#CAP = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)

#USB CAM
CAP = cv2.VideoCapture("/dev/video0")

#Video Check
#CAP = cv2.VideoCapture(0)
#CAP = cv2.VideoCapture("/Volumes/GoogleDrive/My Drive/02_IT/test_videos/test_small_2.mov")

# For running on macbook: 
#CAP = cv2.VideoCapture("/Users/fk/Desktop/test_videos/test_small_2.mov")

#camera = PiCamera()
#camera.resolution = (160,120)
#camera.framerate = 5
#rawCapture = PiRGBArray(camera, size=(160,120))
#time.sleep(0.1)

#Propiedades del video
#CAP.set(3,160) #Width
#CAP.set(4,120) #Height


for i in range(19):
    print(i, CAP.get(i))


H = 480
W = 640
FRAME_AREA = H * W

# get area threshold parameter from db:
SELECTION = select(
    [MAIN_AREATHRESHOLD.c.id,
     MAIN_AREATHRESHOLD.c.area_threshold,
     func.max(MAIN_AREATHRESHOLD.c.id)]
    )
for i in CONN.execute(SELECTION):
    AREA_THRESHOLD = i['area_threshold']

#for manual setting, uncomment
#AREA_THRESHOLD = 13


AREA_TH = FRAME_AREA/AREA_THRESHOLD
print('Area Threshold final:', AREA_TH, 'Area Threshold parameter:', AREA_THRESHOLD)


LINE_UP = int(2*(H/5))
LINE_DOWN = int(3*(H/5))

UP_LIMIT = int(1*(H/5))
DOWN_LIMIT = int(4*(H/5))

print("Red line y:", str(LINE_DOWN))
print("Blue line y:", str(LINE_UP))
LINE_DOWN_COLOR = (255, 0, 0)
LINE_UP_COLOR = (0, 0, 255)
PT1 = [0, LINE_DOWN]
PT2 = [W, LINE_DOWN]
PTS_L1 = np.array([PT1, PT2], np.int32)
PTS_L1 = PTS_L1.reshape((-1, 1, 2))
PT3 = [0, LINE_UP]
PT4 = [W, LINE_UP]
PTS_L2 = np.array([PT3, PT4], np.int32)
PTS_L2 = PTS_L2.reshape((-1, 1, 2))

PT5 = [0, UP_LIMIT]
PT6 = [W, UP_LIMIT]
PTS_L3 = np.array([PT5, PT6], np.int32)
PTS_L3 = PTS_L3.reshape((-1, 1, 2))
PT7 = [0, DOWN_LIMIT]
PT8 = [W, DOWN_LIMIT]
PTS_L4 = np.array([PT7, PT8], np.int32)
PTS_L4 = PTS_L4.reshape((-1, 1, 2))

#old
#FGBG = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
#fk: better recognition
FGBG = cv2.createBackgroundSubtractorMOG2(history=400, varThreshold=10, detectShadows=False)

KERNEL_OP = np.ones((3, 3), np.uint8)
KERNEL_OP2 = np.ones((5, 5), np.uint8)
KERNEL_CL = np.ones((11, 11), np.uint8)

#Variables
FONT = cv2.FONT_HERSHEY_SIMPLEX
PERSONS = []
MAX_P_AGE = 5
PID = 1

FRAME_COUNT = 0

while CAP.isOpened():
##for image in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    #Lee una imagen de la fuente de video
    RET, FRAME = CAP.read()
##    FRAME = image.array

    FRAME_COUNT += 1
    for i in PERSONS:
        i.age_one() #age every person one FRAM
    #########################
    #   PRE-PROCESAMIENTO   #
    #########################
    if FRAME_COUNT % 4 == 0:
        #continue
        pass
    FGMASK = FGBG.apply(FRAME)
    FGMASK2 = FGBG.apply(FRAME)

    try:
        RET, IM_BIN = cv2.threshold(FGMASK, 200, 255, cv2.THRESH_BINARY)
        RET, IM_BIN2 = cv2.threshold(FGMASK2, 200, 255, cv2.THRESH_BINARY)
        #Opening (erode->dilate) para quitar ruido.
        MASK = cv2.morphologyEx(IM_BIN, cv2.MORPH_OPEN, KERNEL_OP)
        MASK2 = cv2.morphologyEx(IM_BIN2, cv2.MORPH_OPEN, KERNEL_OP)
        #Closing (dilate -> erode) para juntar regiones blancas.
        MASK = cv2.morphologyEx(MASK, cv2.MORPH_CLOSE, KERNEL_CL)
        MASK2 = cv2.morphologyEx(MASK2, cv2.MORPH_CLOSE, KERNEL_CL)
    except FileExistsError: # fk: placeholdererror until we find out about potential errors
        print('EOF')
        print('UP:', CNT_UP)
        print('DOWN:', CNT_DOWN)
        break
    #################
    #   CONTORNOS   #
    #################

    CONTOURS0, HIERARCHY = cv2.findContours(MASK2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in CONTOURS0:
        area = cv2.contourArea(cnt)
        if area > AREA_TH:
            #################
            #   TRACKING    #
            #################

            M = cv2.moments(cnt)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            x, y, w, h = cv2.boundingRect(cnt)

            new = True
            if cy in range(UP_LIMIT, DOWN_LIMIT):
                for i in PERSONS:
                    if abs(x-i.getX()) <= w and abs(y-i.getY()) <= h:
                        new = False
                        i.updateCoords(cx, cy)
                        if i.going_UP(LINE_DOWN, LINE_UP) is True:
                            CNT_UP += 1
                            change_up_or_down = 1
                            print("ID:", i.getId(), 'crossed going up at', time.strftime("%c"))
                            LOG.write(
                                "ID: " + str(i.getId())+' crossed going up at ' + time.strftime("%c") + '\n')

                            #get current data from DB
                            SELECTION = select([
                                MAIN_OCCUPANCY.c.id,
                                MAIN_OCCUPANCY.c.capacity,
                                MAIN_OCCUPANCY.c.person_count,
                                MAIN_OCCUPANCY.c.direction,
                                func.max(MAIN_OCCUPANCY.c.id)
                                ])

                            for j in CONN.execute(SELECTION):
                                capacity = j['capacity']
                                latest_person_count = j['person_count']
                                direction = j['direction']

                            # write message into db
                            person_count = latest_person_count + change_up_or_down * direction
                            now = datetime.now()
                            now = now.replace(microsecond=0)
                            insert = MAIN_OCCUPANCY.insert(None).values(
                                capacity=capacity,
                                date=now,
                                person_count=person_count,
                                direction=direction
                                )
                            CONN.execute(insert)

                        elif i.going_DOWN(LINE_DOWN, LINE_UP) is True:
                            CNT_DOWN += 1
                            change_up_or_down = -1
                            print("ID:", i.getId(), 'crossed going down at', time.strftime("%c"))
                            LOG.write(
                                "ID: " + str(i.getId()) + ' crossed going down at ' + time.strftime("%c") + '\n')

                            #get current data from DB
                            SELECTION = select([
                                MAIN_OCCUPANCY.c.id,
                                MAIN_OCCUPANCY.c.capacity,
                                MAIN_OCCUPANCY.c.person_count,
                                MAIN_OCCUPANCY.c.direction,
                                func.max(MAIN_OCCUPANCY.c.id)
                                ])

                            for j in CONN.execute(SELECTION):
                                capacity = j['capacity']
                                latest_person_count = j['person_count']
                                direction = j['direction']

                            # write message into db
                            person_count = latest_person_count + change_up_or_down * direction
                            now = datetime.now()
                            now = now.replace(microsecond=0)
                            insert = MAIN_OCCUPANCY.insert(None).values(
                                capacity=capacity,
                                date=now,
                                person_count=person_count,
                                direction=direction)
                            CONN.execute(insert)
                    if i.getState() == '1':
                        if i.getDir() == 'down' and i.getY() > DOWN_LIMIT:
                            i.setDone()
                        elif i.getDir() == 'up' and i.getY() < UP_LIMIT:
                            i.setDone()
                    if i.timedOut():
                        index = PERSONS.index(i)
                        PERSONS.pop(index)
                        del i
                        break
                
                if new is True:
                    p = Person.MyPerson(PID, cx, cy, MAX_P_AGE)
                    PERSONS.append(p)
                    PID += 1
            #################
            #   DIBUJOS     #
            #################
            cv2.circle(FRAME, (cx, cy), 5, (0, 0, 255), -1)
            img = cv2.rectangle(FRAME, (x, y), (x+w, y+h), (0, 255, 0), 2)
            #cv2.drawContours(FRAME, cnt, -1, (0,255,0), 3)

    #END for cnt in CONTOURS0

    #########################
    # DIBUJAR TRAYECTORIAS  #
    #########################
    for i in PERSONS:
##        if len(i.getTracks()) >= 2:
##            pts = np.array(i.getTracks(), np.int32)
##            pts = pts.reshape((-1,1,2))
##            FRAME = cv2.polylines(FRAME,[pts],False,i.getRGB())
##        if i.getId() == 9:
##            print str(i.getX()), ',', str(i.getY())
        cv2.putText(
            FRAME, str(i.getId()), (i.getX(), i.getY()), FONT, 0.3, i.getRGB(), 1, cv2.LINE_AA)
#################
    #   IMAGANES    #
    #################
    STR_UP = 'UP: '+ str(CNT_UP)
    STR_DOWN = 'DOWN: '+ str(CNT_DOWN)
    FRAME = cv2.polylines(FRAME, [PTS_L1], False, LINE_DOWN_COLOR, thickness=2)
    FRAME = cv2.polylines(FRAME, [PTS_L2], False, LINE_UP_COLOR, thickness=2)
    FRAME = cv2.polylines(FRAME, [PTS_L3], False, (255, 255, 255), thickness=1)
    FRAME = cv2.polylines(FRAME, [PTS_L4], False, (255, 255, 255), thickness=1)
    cv2.putText(FRAME, STR_UP, (10, 40), FONT, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(FRAME, STR_UP, (10, 40), FONT, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
    cv2.putText(FRAME, STR_DOWN, (10, 90), FONT, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(FRAME, STR_DOWN, (10, 90), FONT, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

# comment for headless run
    #cv2.imshow('FRAME', FRAME)
    #cv2.imshow('MASK', MASK)

##    rawCapture.truncate(0)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
#END while(CAP.isOpened())

#################
#   LIMPIEZA    #
#################
LOG.flush()
LOG.close()
CAP.release()
cv2.destroyAllWindows()
