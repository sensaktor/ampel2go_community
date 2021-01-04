"a frame is a single picture, cosequitively making up a video"
#--------------------------------------------------------------------------------------------------#

import logging
from collections import Counter
import pandas as pd
import numpy as np
import cv2
from sklearn.cluster import DBSCAN, AgglomerativeClustering
import contour
class Frame:
    "creates Frames"
    def __init__(self):
        self.logger = logging.getLogger('training_logger')
        self.frame_color = None
        self.frame_backgroundsubsstractor = None
        self.frame_threshold = None
        self.frame_id = None
        self.contours = [] ## merge with contour_instances in next commit to contour_instances
        self.contour_count = 0 # remove in next commit
        self.contour_instances = []
        self.contour_instance_count = 0
        self.cluster_instances = []
        self.cluster_id_set = set()



    def enhance_contrast(self):
        "enhances contrast by using Y CR CB colorspace"\
        "Y – Luminance or Luma component obtained from RGB after gamma correction."\
        "Cr = R – Y ( how far is the red component from Luma )."\
        "Cb = B – Y ( how far is the blue component from Luma )."
        frame_color_clahe = cv2.cvtColor(self.frame_color, cv2.COLOR_BGR2YCrCb)
        ycrcb_y, ycrcb_cr, ycrcb_cb = cv2.split(frame_color_clahe)
        ycrcb_y_eq =  cv2.equalizeHist(ycrcb_y)
        frame_color_clahe = cv2.merge((ycrcb_y_eq, ycrcb_cr, ycrcb_cb))
        self.frame_color = cv2.cvtColor(frame_color_clahe, cv2.COLOR_YCR_CB2BGR)




    def subsctract_background(self, backgroundsubstractor):
        "does the actual backgroundsubsctraction of this frame"
        self.frame_backgroundsubsstractor = backgroundsubstractor.apply(self.frame_color)
        # chose 180 as threshold to use only non-shadows
        self.frame_threshold = cv2.threshold(self.frame_backgroundsubsstractor\
            , 1, 255, cv2.THRESH_BINARY)[1]



    def find_contours(self):
        "finding contours"
        contours, _ = cv2.findContours(self.frame_threshold, cv2.RETR_EXTERNAL\
            , cv2.CHAIN_APPROX_SIMPLE)
        self.contours = [x for x in contours if cv2.contourArea(x) > 1000 ]

        self.contour_count = len(self.contours)
        self.frame_threshold= cv2.cvtColor(self.frame_threshold\
            , cv2.COLOR_GRAY2BGR)




    def initiate_filter_calculate_contour_instances(self,crop_window_up, crop_window_down\
        , trained_model):
        "performs all needed preparations of contours. Do not use in main_generate_training_data"
        # initiate_contour_instances(self):
        contour_index = 0
        contour_instances_temp = []
        for contour_instance in range(self.contour_count):
            contour_instance = contour.Contour()
            contour_instance.contour_id = self.frame_id + '-' + str(contour_index).rjust(10, '0')
            contour_instance.contour = self.contours[contour_index]
            contour_index += 1

            # filter_contour_instances
            contour_instance.area = cv2.contourArea(contour_instance.contour)
            moment = cv2.moments(contour_instance.contour)
            try:
                contour_instance.centroid_x = int(moment['m10']/moment['m00'])
                contour_instance.centroid_y = int(moment['m01']/moment['m00'])
            except ZeroDivisionError:
                continue
            if contour_instance.centroid_y > crop_window_up \
                and contour_instance.centroid_y < crop_window_down :
                self.logger.debug("contour_instance with id %s has area %s and is appended to "\
                    "filtered list" ,contour_instance.contour_id, contour_instance.area)
                #calculate properties
                contour_instance.calculate_properties()
                contour_instance.calculate_area_white_gray(self.frame_backgroundsubsstractor)

                #predict
                observation = [contour_instance.get_observation()]
                observation = pd.DataFrame(observation)
                observation = observation[['area'\
                    ,'area_white'\
                    ,'area_grey'\
                    ,'centroid_x'\
                    ,'centroid_y'\
                    ,'contour_arc_length'\
                    ,'hull_area'\
                    ,'poly_area'\
                    ,'rectangle_width'\
                    ,'rectangle_height'\
                    ,'angle' ]]
                contour_instance.label = trained_model.predict(observation)[0]
                self.logger.debug('predicted contour label of contour_id %s with label %s'\
                    , contour_instance.contour_id, contour_instance.label)

                if contour_instance.label == '1' or contour_instance.label == '2' \
                    or contour_instance.label == '4' or contour_instance.label == '5':
                    self.logger.debug("contour_instance with contour_id %s has label 1, 2 or 5 "\
                        "and is appended to filtered list", contour_instance.contour_id)

                    contour_instances_temp.append(contour_instance)

        self.contour_instances = contour_instances_temp
        return self.contour_instances

    def initiate_contour_instances(self):
        "only used in main_generate_training_data  processing of the contour"
        contour_index = 0
        for contour_instance in range(self.contour_count):
            contour_instance = contour.Contour()
            contour_instance.contour_id = self.frame_id + '-' + str(contour_index).rjust(10, '0')
            contour_instance.contour = self.contours[contour_index]
            self.contour_instances.append(contour_instance)
            contour_index += 1

        self.contour_instance_count = len(self.contour_instances)
        self.logger.debug("contour_instance_count after initating: %s",self.contour_instance_count)



    def filter_contour_instances(self, crop_window_up, crop_window_down):
        "only used in main_generate_training_data   filters out small contours"
        contour_instances_temp = []
        for contour_instance in self.contour_instances:
            contour_instance.area = cv2.contourArea(contour_instance.contour)
            moment = cv2.moments(contour_instance.contour)
            try:
                contour_instance.centroid_x = int(moment['m10']/moment['m00'])
                contour_instance.centroid_y = int(moment['m01']/moment['m00'])
            except ZeroDivisionError:
                continue
            if contour_instance.area > 1000 and contour_instance.centroid_y > crop_window_up \
                and contour_instance.centroid_y < crop_window_down:
                index = self.contour_instances.index(contour_instance)
                self.logger.debug("contour_instance with index %s has area "\
                    " %s and is appended to filtered list",index, contour_instance.area)
                contour_instances_temp.append(contour_instance)

        self.contour_instances = contour_instances_temp
        self.contour_instance_count = len(self.contour_instances)
        self.logger.debug("contour_instance_count after filtering: %s",self.contour_instance_count)



    def calculate_contour_instances_properties(self):
        "only used in main_generate_training_data   mainly calculates properties of each contour"
        for contour_instance in self.contour_instances:
            contour_instance.calculate_properties()
            contour_instance.calculate_area_white_gray(self.frame_backgroundsubsstractor)




    def assign_contour_instances_labels(self):
        "only used in main_generate_training_data   shows current frame with current contour"\
        "highlighted, and gets the keyinput as label"
        key_input = None
        for contour_instance in self.contour_instances:
            frame_temp = self.frame_threshold.copy()
            cv2.drawContours(frame_temp, contour_instance.contour, -1,(0,0,255))
            cv2.circle(frame_temp, (contour_instance.centroid_x, contour_instance.centroid_y)\
                , 5, (0, 0, 255), -1)
            cv2.putText(
                frame_temp, contour_instance.contour_id, (contour_instance.centroid_x\
                    , contour_instance.centroid_y), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)
            cv2.imshow('Is this: Major part of person (1), Minor part of person (2)'\
                ', something else (3), mainly two or more persons (4), more shadow than person(s)'\
                ' (5)', frame_temp)
            key_input = cv2.waitKey(0) & 0xff
            if key_input == 49:
                self.logger.info("contour_id %s has been labeled as 1 (major part of person)"\
                    , contour_instance.contour_id )
                contour_instance.label = 1
            if key_input == 50:
                self.logger.info("contour_id %s has been labeled as 2 (minor part of person)"\
                    , contour_instance.contour_id)
                contour_instance.label = 2
            if key_input == 51:
                self.logger.info("contour_id %s has been labeled as 3 (something else)"\
                    , contour_instance.contour_id)
                contour_instance.label = 3
            if key_input == 52:
                self.logger.info("contour_id %s has been labeled as 4 (mainly two or more persons)"\
                    , contour_instance.contour_id)
                contour_instance.label = 4
            if key_input == 53:
                self.logger.info("contour_id %s has been labeled as 5 (more shadow than person)"\
                    , contour_instance.contour_id)
                contour_instance.label = 5
            if key_input == 8:
                self.logger.info("This frame and the previous frame observations are not recorded")
                break
            if key_input == 27:
                self.logger.info("stopping... ")
                break
        return key_input



    def get_observations_by_frame(self):
        "gets all properties from all the contour_instances in this frame_instance as list of"\
        "lists used only in generate_training_data "
        observations_by_frame = []
        for contour_instance in self.contour_instances:
            observation = contour_instance.get_observation()
            observations_by_frame.append(observation.copy())
        self.logger.info("returning %s collected observations from all contour_instances of this"\
             "frame", len(observations_by_frame) )
        return observations_by_frame



    def predict_contour_labels(self, trained_model):
        "predicts contour lables"
        for contour_instance in self.contour_instances:
            observation = [contour_instance.get_observation()]
            observation = pd.DataFrame(observation)
            observation = observation[['area'\
                  ,'area_white'\
                  ,'area_grey'\
                  ,'centroid_x'\
                  ,'centroid_y'\
                  ,'contour_arc_length'\
                  ,'hull_area'\
                  ,'poly_area'\
                  ,'rectangle_width'\
                  ,'rectangle_height'\
                  ,'angle' ]]
            #observation = observation[['area', 'contour_arc_length']]
            contour_instance.label = trained_model.predict(observation)[0]
            self.logger.debug('predicted contour label of contour_id %s with label %s'\
                , contour_instance.contour_id, contour_instance.label)



    def filter_predicted_contours(self):
        "filters for contour_instance.label == 1, 2 and 5"
        contour_instances_temp = []
        for contour_instance in self.contour_instances:
            if contour_instance.label == '1' or contour_instance.label == '2' \
                or contour_instance.label == '4' or contour_instance.label == '5':
                index = self.contour_instances.index(contour_instance)
                self.logger.debug("contour_instance with contour_id %s has label 1, 2 or 5 "\
                    "and is appended to filtered list", contour_instance.contour_id)
                contour_instances_temp.append(contour_instance)

        self.contour_instances = contour_instances_temp
        self.contour_instance_count = len(self.contour_instances)
        self.logger.debug("contour_instance_count after predicting: %s"\
            ,self.contour_instance_count)
        return self.contour_instances

    def split_label5_contours(self):
        "splits contours, not used anymore "
        for contour_instance in self.contour_instances:
            if contour_instance.label == '4' or contour_instance.label == '5':
                contour_instance_new = contour.Contour()
                contour_instance_new.contour_id = 'clone'
                contour_instance_new.rectangle_height = contour_instance.rectangle_height
                contour_instance_new.rectangle_width = contour_instance.rectangle_width
                contour_instance_new.centroid_x = contour_instance.centroid_x
                contour_instance_new.centroid_y = contour_instance.centroid_y
                contour_instance_new.contour = contour_instance.contour


                if contour_instance_new.rectangle_width > contour_instance_new.rectangle_height:
                    contour_instance_new.centroid_x = int(contour_instance_new.centroid_x \
                        + contour_instance_new.rectangle_width*0.25)
                    contour_instance.centroid_x =  int(contour_instance.centroid_x \
                        - contour_instance.rectangle_width*0.25)

                elif contour_instance_new.rectangle_width < contour_instance_new.rectangle_height:
                    contour_instance_new.centroid_y = int(contour_instance_new.centroid_y \
                        + contour_instance_new.rectangle_height*0.25)

                    contour_instance.centroid_y = int(contour_instance.centroid_y \
                        + contour_instance.rectangle_height*0.25)

                self.contour_instances.append(contour_instance_new)

        self.contour_instance_count = len(self.contour_instances)
        self.logger.debug("contour_instance_count after splitting label 5 contours: %s"\
            ,self.contour_instance_count)
        return self.contour_instances


    def show_contour_instances(self):
        "displays all contours in self.contour_instances"
        for contour_instance in self.contour_instances:
            cv2.drawContours(self.frame_threshold\
                , contour_instance.contour, -1,(0,0,255))
            cv2.circle(self.frame_threshold,\
                (contour_instance.centroid_x, contour_instance.centroid_y), 5, (0, 0, 255), -1)
            cv2.putText(
                self.frame_threshold, contour_instance.contour_id\
                    , (contour_instance.centroid_x, contour_instance.centroid_y)\
                    , cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)

        cv2.imshow('frame_backgroundsubsstractor', self.frame_backgroundsubsstractor)
        cv2.moveWindow('frame_backgroundsubsstractor', 0,0)
        cv2.imshow('frame_threshold with predicted contours outlined', self.frame_threshold,)
        cv2.moveWindow('frame_threshold with predicted contours outlined', 650,0)
        key_input = cv2.waitKey(1) & 0xf
        return key_input


    def show_cropped_contours(self):
        try:
            for contour_instance in self.contour_instances:
                 # Create black frame
                mask = np.zeros(self.frame_backgroundsubsstractor.shape,np.uint8)
                # Draw  white filled contour in black Frame Extract out the object and place
                #  into output image
                cv2.drawContours(mask, [contour_instance.contour], -1, 255, -1)
                frame_cropped_contour_white_gray = np.zeros(\
                    self.frame_backgroundsubsstractor.shape,np.uint8)
                frame_cropped_contour_white_gray[mask == 255]\
                    = self.frame_backgroundsubsstractor[mask == 255]

            cv2.imshow('frame_cropped_contour_white_gray of predicted contours'\
                , frame_cropped_contour_white_gray,)
            cv2.moveWindow('frame_cropped_contour_white_gray of predicted contours', 0,500)

            key_input = cv2.waitKey(1) & 0xf
        except NameError:
            pass


    def determine_clusters(self):
        "calculates clusters using dbscan function"
        contour_centroids = []
        contour_list = []
        contour_to_cluster_list = []
        for contour_instance in self.contour_instances:
            contour_centroids.append([contour_instance.centroid_x,contour_instance.centroid_y])
            contour_list.append(contour_instance.contour_id)
        if len(contour_centroids) > 0:
            dbscan_output = DBSCAN(eps = 170, min_samples = 2).fit(contour_centroids)
            dbscan_output = dbscan_output.labels_.tolist()
            contour_to_cluster_list = [list(a) for a in zip(contour_list, dbscan_output)]

        self.logger.debug('determined clusters:   %s', contour_to_cluster_list)
        return contour_to_cluster_list


    def determine_clusters2(self):
        "calculates clusters using hierarchical clustering"
        contour_centroids = []
        contour_list = []
        contour_to_cluster_list = []
        for contour_instance in self.contour_instances:
            contour_centroids.append([contour_instance.centroid_x,contour_instance.centroid_y])
            contour_list.append(contour_instance.contour_id)





        if len(contour_list) == 1:
            contour_to_cluster_list = [[contour_list[0],-1]]
            self.logger.debug('len(contour_list) is %s, contour_to_cluster_list is %s'\
                ,len(contour_list), contour_to_cluster_list)
        if len(contour_list) > 1:
            output = AgglomerativeClustering(n_clusters = None\
                , distance_threshold=150).fit(contour_centroids)
            output = output.labels_.tolist()
            # assign single node clusters with -1, so that label2 single node cluster can be
            # eradicated in step "initiate_cluster
            counted_output = Counter(output)
            single_node_clusters = []
            for key,value in counted_output.items():
                if value == 1:
                    single_node_clusters.append([key])
            output_new =[ x if x not in single_node_clusters else -1 for x in output  ]
            contour_to_cluster_list = [list(a) for a in zip(contour_list, output_new)]
            self.logger.debug('len(contour_list) is %s, contour_to_cluster_list is %s'\
                ,len(contour_list), contour_to_cluster_list)


        self.logger.debug('determined clusters: %s', contour_to_cluster_list)
        #return contour_to_cluster_list


    #def initiate_cluster(self,contour_to_cluster_list):
    #    "each contour needs to belog to one cluster"

        cluster_or_label1_flag = False
        for contour_instance in self.contour_instances:
            for contour_id_cluster_id in contour_to_cluster_list:
                if contour_instance.contour_id == contour_id_cluster_id[0]:
                    contour_instance.db_scan_cluster_id = contour_id_cluster_id[1]
                    self.logger.debug('contour_instance %s has been assigned a db_scan_cluster_id'\
                        ' of %s', contour_instance.contour_id, contour_instance.db_scan_cluster_id)
                    break

            if contour_instance.db_scan_cluster_id != -1:
                contour_instance.cluster_id = contour_instance.db_scan_cluster_id
                cluster_or_label1_flag = True
                self.cluster_id_set.add(contour_instance.cluster_id)
                self.logger.debug('the true cluster with id %s has been assigned to '\
                    'contour_instance %s', contour_instance.db_scan_cluster_id\
                    , contour_instance.contour_id)
                self.logger.debug('cluster_or_label1_flag set to %s ', cluster_or_label1_flag)

            if contour_instance.db_scan_cluster_id == -1 and contour_instance.label == 1:
                # use contour_id as cluster_id, since there is only one contour in this cluster
                contour_instance.cluster_id = contour_instance.contour_id
                cluster_or_label1_flag = True
                self.cluster_id_set.add(contour_instance.cluster_id)
                self.logger.debug('single node cluster ("-1") with a contour_instance.label == 1 '\
                    'with id %s has been assigned to contour_instance %s'\
                    , contour_instance.cluster_id, contour_instance.contour_id)
                self.logger.debug('cluster_or_label1_flag set to %s ', cluster_or_label1_flag)


        self.logger.debug('(cluster_id_set is %s after assigning cluster_ids of "true" clusters '\
            'of label 1 clusters', self.cluster_id_set)

        if cluster_or_label1_flag is True:
            try:
                self.cluster_id_set.remove(-1)
                self.logger.debug('cluster_or_label1_flag has been true, removing (-1) clusters')
            except KeyError:
                pass
        # elif no true or label1 cluster has been found.Must work with the inferior label2 instances
        elif cluster_or_label1_flag is False: 
            for contour_instance in self.contour_instances:
                contour_instance.cluster_id = contour_instance.contour_id
                self.cluster_id_set.add(contour_instance.cluster_id)
                self.logger.debug('cluster_or_label1_flag has been false, assigning '\
                    'contour_instance.cluster_id %s', contour_instance.cluster_id)

        self.logger.debug('cluster_id_set is %s after assigning cluster_ids of a frame with '\
            '(-1)-clusters only', self.cluster_id_set)


        for cluster_id in self.cluster_id_set:
            cluster = contour.Cluster()
            cluster.cluster_id = cluster_id
            self.cluster_instances.append(cluster)
            self.logger.debug('initiated cluster with cluster_id %s', cluster.cluster_id)


    def calculate_cluster_properties(self):
        "first appends all the contour_instances centroids to cluster,then calculates the mean of "\
        "these centroids which are then assigned as cluster_centroids"
        for contour_instance in self.contour_instances:
            for cluster_instance in self.cluster_instances:
                if contour_instance.cluster_id == cluster_instance.cluster_id:
                    cluster_instance.contour_id_centroid_x_centroid_y.append(\
                        [contour_instance.contour_id, contour_instance.centroid_x\
                        , contour_instance.centroid_y])
                    self.logger.debug("contour_id %s was appended to cluster_instance %s"\
                        ", along with coordinates (%s,%s)", contour_instance.contour_id\
                        , cluster_instance.cluster_id, contour_instance.centroid_x\
                        , contour_instance.centroid_y)

        for cluster_instance in self.cluster_instances:
            cluster_instance.calculate_properties()



    def show_person_instances(self, person_instances, cnt_up, cnt_down):
        "displays all persons in from group.person_instances"
        logging.debug("about to show %s show_person_instances", len(person_instances))
        for person_instance in person_instances:
            person_instance.draw_id(self.frame_color)
            person_instance.draw_track(self.frame_color)
            cv2.circle(self.frame_color,(person_instance.contour_centroid_xt\
                , person_instance.contour_centroid_yt), 5, (0, 0, 255), -1)

        str_up_down = 'Up/Down: ' + str(cnt_up) + "/" + str(cnt_down)
        cv2.putText(self.frame_color, str_up_down, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5\
            , (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(self.frame_color, str_up_down, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5\
            , (0, 0, 255), 1, cv2.LINE_AA)
        cv2.imshow('showing predicted person instances', self.frame_color,)
        cv2.moveWindow('showing predicted person instances', 1300,0)
        key_input = cv2.waitKey(1) & 0xff
        return key_input


#--------------------------------------------------------------------------------------------------#