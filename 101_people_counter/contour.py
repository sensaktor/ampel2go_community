"handles contours and clusters"
#--------------------------------------------------------------------------------------------------#
import logging
import statistics
import cv2
import numpy as np

class Contour:
    "class for contours"
    def __init__(self):
        self.logger = logging.getLogger('training_logger')
        self.label = None
        self.contour_id = None
        self.contour = None
        self.area = None
        self.area_white = None
        self.area_grey = None
        self.centroid_x = None
        self.centroid_y = None
        self.arc_length = None
        self.hull = None
        self.hull_area = None
        self.poly = None
        self.poly_area = None
        self.rectangle_width = None
        self.rectangle_height = None
        self.angle = None
        self.cluster_id = None
        self.db_scan_cluster_id = None
        self.minimal_rect = None



    def calculate_area_white_gray(self, frame):
        "calculates the amound of grey that comes out of the backgroundsubstractor"
        mask = np.zeros(frame.shape,np.uint8) # Create black frame
        # Draw  white filled contour in black Frame
        cv2.drawContours(mask, [self.contour], -1, 255, -1)
        # Extract out the object and place into output image
        frame_cropped_contour_white_gray = np.zeros(frame.shape,np.uint8)
        frame_cropped_contour_white_gray[mask == 255] = frame[mask == 255]
        area_white_gray = cv2.countNonZero(frame_cropped_contour_white_gray)

        frame_cropped_contour_white = cv2.threshold(frame_cropped_contour_white_gray\
        , 128  , 255, cv2.THRESH_BINARY)[1]
        self.area_white = cv2.countNonZero(frame_cropped_contour_white)
        self.area_grey = area_white_gray - self.area_white
        logging.debug("calculated the area_white: %s and area_grea: %s"\
            , self.area_white, self.area_grey)

    def calculate_properties(self):
        "calculates all the properties of the contour"
        self.arc_length = round(cv2.arcLength(self.contour,True),1)
        self.hull = cv2.convexHull(self.contour)
        self.hull_area = cv2.contourArea(self.hull)
        epsilon = 0.002 * self.arc_length
        self.poly = cv2.approxPolyDP(self.contour,epsilon,True)
        self.poly_area = cv2.contourArea(self.poly)
        _, _, self.rectangle_width\
            , self.rectangle_height = cv2.boundingRect(self.contour)
        try:
            (_,_),(_,_), angle_temp = cv2.fitEllipse(self.contour)
            self.angle = round(angle_temp,1)
        except cv2.error:
            self.angle = 0
        self.minimal_rect = cv2.minAreaRect(self.contour)


    def get_observation(self):
        "returns the relevant properties of the contour_instance"
        observation = \
            {'label': self.label\
            ,'contour_id': self.contour_id\
            ,'area': self.area\
            ,'area_white': self.area_white\
            ,'area_grey': self.area_grey\
            ,'centroid_x': self.centroid_x\
            ,'centroid_y': self.centroid_y\
            ,'contour_arc_length': self.arc_length\
            #,'hull': self.hull\
            ,'hull_area': self.hull_area\
            #,'poly': self.poly\
            ,'poly_area': self.poly_area\
            ,'rectangle_width': self.rectangle_width\
            ,'rectangle_height': self.rectangle_height\
            ,'angle': self.angle\
            }
        self.logger.debug("contour_id %s has provided the following self.properties %s "\
            , self.contour_id, observation)
        return observation


class Cluster:
    "creates contour clusters and "
    def __init__(self):
        self.logger = logging.getLogger('training_logger')
        self.cluster_id = None
        self.contour_id_centroid_x_centroid_y = []
        self.centroid_x = None
        self.centroid_y = None




    def calculate_properties(self):
        "calculates properties"
        centroids_x = []
        centroids_y = []
        for item in self.contour_id_centroid_x_centroid_y:
            centroids_x.append(item[1])
            centroids_y.append(item[2])

        self.centroid_x = int(statistics.mean(centroids_x))
        self.centroid_y = int(statistics.mean(centroids_y))
        self.logger.debug('cluster_id %s, cluster_centroids (%s,%s)'\
            , self.cluster_id, self.centroid_x, self.centroid_y)
