"""this file contains the myperson class,
 which is initiated each time a moving object is recognized"
"""
#--------------------------------------------------------------------------------------------------#
import logging
from random import randint
import cv2 as cv
import numpy as np

class MyPerson:
    "defines methods of a detected person"
    tracks = []
    def __init__(self, person_counter, contour_centroid_xt_new, contour_centroid_yt_new, max_age):
        self.logger = logging.getLogger('training_logger')
        self.person_id = person_counter
        self.contour_centroid_xt = contour_centroid_xt_new
        self.contour_centroid_yt = contour_centroid_yt_new
        self.tracks = [[self.contour_centroid_xt, self.contour_centroid_yt]]
        self.random_red = randint(0,255)
        self.random_green = randint(0,255)
        self.random_blue = randint(0,255)
        self.done = False
        self.age = 0
        self.max_age = max_age
        self.thrust_absolute = 0
        self.thrust_binary = 0
        self.is_going_up_down = 0 # Values 1, 0, -1
        self.has_crossed_up = False
        self.has_crossed_down = False
        self.contour_centroid_xt_hat = None
        self.contour_centroid_yt_hat = None
        self.prospects = None

    def get_rgb(self):
        "get the random color to person_instance"
        return (self.random_red,self.random_green,self.random_blue)
    def get_tracks(self):
        "get the tracks of the person_instance"
        return self.tracks
    def get_id(self):
        "get the person_id"
        return self.person_id


    def update_coords(self, contour_centroid_x_new, contour_centroid_y_new):
        "update the coordinates of the centroid to the new location"
        if contour_centroid_y_new > self.contour_centroid_yt:
            self.is_going_up_down = 1
        elif contour_centroid_y_new < self.contour_centroid_yt:
            self.is_going_up_down = -1
        else:
            self.is_going_up_down = 0
        self.contour_centroid_xt = contour_centroid_x_new
        self.contour_centroid_yt = contour_centroid_y_new
        self.tracks.insert(0,[self.contour_centroid_xt, self.contour_centroid_yt])

    def update_age(self, age_reset_down_thres, age_reset_up_thres):
        "updates  the age of the person"
        # make age dependend on thrust, so that they live longer while undetected
        if self.tracks[0][1] <= age_reset_up_thres or self.tracks[0][1] >= age_reset_down_thres:
            self.age -= 1
            self.age = max(self.age, -8)

        if len(self.tracks) >= 2 and abs(self.tracks[0][1] - self.tracks[1][1]) > 5:
            self.age -= 4
            self.age = max(self.age, -40)
        if len(self.tracks) >= 30 and abs(self.tracks[0][1] - self.tracks[1][1]) > 5:
            self.age -= 4
            self.age = max(self.age, -80)



    def update_thrust(self): ########
        """sums up the direction-points of walking across the picture.
         positive for going up, negative for going down"""
        # going up y-values increase from top to down: if y_t < y_t-1 then it's going up.
        if len(self.tracks) >= 2 and self.tracks[0][1] - self.tracks[1][1]  < 0:
            self.thrust_absolute -= abs(self.tracks[0][1] - self.tracks[1][1])
            self.thrust_binary -= 1
            if self.has_crossed_up is True:
                self.thrust_absolute = max(self.thrust_absolute, -1 )
                self.thrust_binary = max(self.thrust_binary, -1 )

        # going down  y-values increase from top to down: if y_t > y_t-1 then it's going down
        if len(self.tracks) >= 2 and self.tracks[0][1] - self.tracks[1][1] > 0:
            self.thrust_absolute += abs(self.tracks[0][1] - self.tracks[1][1])
            self.thrust_binary += 1
            if self.has_crossed_down is True:
                self.thrust_absolute = min(self.thrust_absolute, 1 )
                self.thrust_binary = min(self.thrust_binary, 1 )

    def set_done(self):
        "set the person_instance to done, i.e. out of picture or timedout"
        self.done = True




    def crossing_up(self, thrust_abs_crossing_threshold, thrust_bin_crossing_threshold):
        "the underscore is a placeholder, since crossing_up / crossing_down works the same, but "\
        " different inputs are used"
        if (self.has_crossed_up is False) and (self.has_crossed_down is False) \
            and (self.thrust_absolute * (-1) > thrust_abs_crossing_threshold) \
            and (self.thrust_binary * (-1) > thrust_bin_crossing_threshold):
            self.has_crossed_up = True
            return True
        # consider uturns:
        elif (self.has_crossed_up is False) and (self.has_crossed_down is True) \
            and (self.thrust_absolute * (-1) > thrust_abs_crossing_threshold) \
            and (self.thrust_binary * (-1) > thrust_bin_crossing_threshold):
            self.has_crossed_up = True
            self.has_crossed_down = False
            return True
        else:
            return False



    def crossing_down(self, thrust_abs_crossing_threshold, thrust_bin_crossing_threshold):
        "the underscore is a placeholder, since crossing_up / crossing_down works the same, but "\
        " different inputs are used"
        if (self.has_crossed_down is False) and (self.has_crossed_up is False)   \
            and (self.thrust_absolute  > thrust_abs_crossing_threshold) \
            and (self.thrust_binary  > thrust_bin_crossing_threshold):
            self.has_crossed_down = True
            return True
        # consider uturns:
        elif (self.has_crossed_down is False) and (self.has_crossed_up is True)   \
            and (self.thrust_absolute  > thrust_abs_crossing_threshold) \
            and (self.thrust_binary  > thrust_bin_crossing_threshold):
            self.has_crossed_down = True
            self.has_crossed_up = False
            return True
        else:
            return False



    def draw_id(self, img):
        "draws the ID of the person_instance next to the centroid"
        text = "Person: " + str(self.get_id()) + " age=" + str(self.age) + " dirTotal: " \
            + str(self.thrust_absolute)
        cv.putText(img, text, (self.contour_centroid_xt, self.contour_centroid_yt)\
            , cv.FONT_HERSHEY_SIMPLEX, 0.5, self.get_rgb(), 1, cv.LINE_AA)



    def draw_track(self, img):
        "draws the track of the person_instance (centroid)"
        if len(self.get_tracks()) >= 2:
            pts = np.array(self.get_tracks(), np.int32)
            pts = pts.reshape((-1,1,2))
            img = cv.polylines(img,[pts],False,self.get_rgb())



    def age_one(self, frame_count):
        "Ages the person_instace by 1"
        self.age += 1
        if self.age > self.max_age:
            self.done = True
            self.logger.debug("person done, too old: person_id %s, frame_count %s"\
                , str(self.person_id), str(frame_count))
        return True
