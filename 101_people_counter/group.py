"contains class for persons"
#--------------------------------------------------------------------------------------------------#
import logging
import math
import time
import person


class Group:
    "class for handling a crowd of persons"
    def __init__(self):
        self.person_instances = []
        self.logger = logging.getLogger('training_logger')
        self.person_counter = 0

    def next_frame_aging(self, frame_count):
        "ages each person by one and de-lists 'done' persons"
        persons_temp =[]
        for person_instance in self.person_instances:
            person_instance.age_one(frame_count)  # age every person each frame
            if person_instance.done is False:
                persons_temp.append(person_instance)
                self.logger.debug('next_frame_aging(): person_id %s was aged by one, but is not '\
                    'too old, i.e. is still part of person_instances', person_instance.person_id)
        self.person_instances = persons_temp



    def get_closest_person(self, contour_centroid_xt_new, contour_centroid_yt_new):
        "selects the closest person. This is algorithm can still be improved on: Think of a "\
        "situation where two centroids are to be matched to two persons. both are within the "\
        "new_person_x_thresholds, but the one that is closest to person 1 should actually be "\
        "fitted to person 2, and the valid 'leftover' centroid, should be assigend to person 1"
        distances = []
        closest_person_id = None
        # sort persons by age, look which contours are within their new_person_thresholds and
        # assign the cluster to this person
        for person_instance in self.person_instances:
            person_instance_distance = math.sqrt(\
                (person_instance.contour_centroid_xt - contour_centroid_xt_new)**2
                + (person_instance.contour_centroid_yt - contour_centroid_yt_new)**2
            )
            # introduce additional pull if person is of age
            person_instance_distance =max(0, person_instance_distance \
                - min(person_instance.age * 2, 75))
            distances.append((person_instance.person_id, person_instance_distance))
        try:
            closest_person_id = min(distances, key = lambda t: t[1])[0]
        except ValueError:
            pass

        self.logger.debug("closest person to contour centroids (%s,%s) is personID %s "\
            ,  contour_centroid_xt_new, contour_centroid_yt_new, closest_person_id)
        return closest_person_id

#--------------------------------------------------------------------------------------------------#


    def calculate_cluster_person_distance_list(self, cluster_instances, parameter_space_instance):
        """calculates distances from clusters to persons. If no person is in reach, a new person is
        created and assigned"""
        self.logger.debug("calculate_cluster_person_distance_list(): creating"\
            "cluster_person_distance_list...")
        cluster_person_distance_list = []
        for cluster_instance in cluster_instances:
            one_person_within_threshold = False

            for person_instance in self.person_instances:
                distance = int(math.sqrt(\
                    (person_instance.contour_centroid_xt - cluster_instance.centroid_x)**2
                    + (person_instance.contour_centroid_yt - cluster_instance.centroid_y)**2))
                self.logger.debug("calculate_cluster_person_distance_list(): person_instance"\
                    ".person_id %s and cluster_instance.cluster_id %s have distance %s"\
                    , person_instance.person_id, cluster_instance.cluster_id, distance)
                if distance < parameter_space_instance.new_person_horizontal_threshold:
                    cluster_person_distance_list.append([ cluster_instance.cluster_id\
                        , person_instance.person_id, distance])
                    self.logger.debug("calculate_cluster_person_distance_list(): appended to "\
                        "cluster_person_distance_list: %s, %s, %s "\
                        , person_instance.person_id, cluster_instance.cluster_id, distance)
                    one_person_within_threshold = True

            if one_person_within_threshold is False:
                person_instance = person.MyPerson(self.person_counter\
                    , cluster_instance.centroid_x, cluster_instance.centroid_y\
                    , parameter_space_instance.person_age_threshold)
                self.logger.debug("calculate_cluster_person_distance_list(): no existing person in"\
                    "reach, created a new person: person_counter %s, cluster_id %s,  y %s, x %s"\
                    , str(self.person_counter), str(cluster_instance.cluster_id)\
                    ,  str(cluster_instance.centroid_x), str(cluster_instance.centroid_y))
                self.person_instances.append(person_instance)
                self.person_counter += 1
                distance = 0
                cluster_person_distance_list.append([cluster_instance.cluster_id\
                    , person_instance.person_id, distance])

        return cluster_person_distance_list



    def person_to_cluster_assignment(self, cluster_person_distance_list):
        "resolves matching: every person to one contour within thresholds.For those with more than"\
        "one contour at choice, let persons with one choice choose first. then go through the"\
        "persons with more than one choice and assign the closest cluster form the clusters that"\
        " are still available "
        free_clusters_set = set([ x[0] for x in cluster_person_distance_list ])
        free_persons_set = set([ x[1] for x in cluster_person_distance_list ])
        person_to_cluster_assignmen_list = [] # reset person_to_cluster_assignment
        # first iteration:
        self.logger.debug("person_to_cluster_assignment(): free_clusters_set = %s "\
            ", free_persons_set = %s starting first iteration to assign clusters to persons..."\
            , free_clusters_set, free_persons_set)
        self.person_instances.sort(key=lambda x: x.age, reverse=False)
        for person_instance in self.person_instances:
            prospects = [ x for x in cluster_person_distance_list if x[1] \
                == person_instance.person_id]
            self.logger.debug("person_id %s has the following prospective clusters: %s" \
                ,person_instance.person_id, prospects)
            if len(prospects) == 1 and prospects[0][0] in free_clusters_set:
                person_to_cluster_assignmen_list.append([person_instance.person_id\
                    , prospects[0][0]])
                free_clusters_set.remove(prospects[0][0])
                free_persons_set.remove(prospects[0][1])
                self.logger.debug("cluster_id %s is assigned to person_id %s,because person_id has"\
                    "exactly one cluster in reach",  prospects[0][0], person_instance.person_id )

        self.logger.debug("lenth cluster_person_distance_list is %s before removing assinged "\
            "clusters", len(cluster_person_distance_list))
        cluster_person_distance_list_temp = []
        for item in cluster_person_distance_list:
            if item[0] in free_clusters_set and item[1] in free_persons_set:
                cluster_person_distance_list_temp.append(item)
        cluster_person_distance_list = cluster_person_distance_list_temp
        self.logger.debug("lenth cluster_person_distance_list is %s after removing assinged "\
            "clusters", len(cluster_person_distance_list))

        if len(cluster_person_distance_list) == 0:
            return person_to_cluster_assignmen_list

        # second iteration:
        self.logger.debug("starting second iteration to assign clusters to persons...")
        self.person_instances.sort(key=lambda x: x.age, reverse=False)
        for person_instance in self.person_instances:
            if person_instance.person_id in free_persons_set:
                prospects = [ x for x in cluster_person_distance_list if x[1] \
                    == person_instance.person_id]
                if len(prospects) == 0:
                    self.logger.debug("person_id %s has no prospects in second iteration. "\
                        "continuing to next person", person_instance.person_id)
                    continue
                self.logger.debug("person_id %s has the following prospects : %s (from "\
                    "cluster_person_distance_list)", person_instance.person_id, prospects)
                prospect_min = min(prospects, key = lambda t: t[2])
                self.logger.debug("person_id %s has the following min-prospect : %s (from "\
                    "cluster_person_distance_list)", person_instance.person_id, prospect_min)

                person_to_cluster_assignmen_list.append([person_instance.person_id\
                    , prospect_min[0]])
                free_clusters_set.remove(prospect_min[0])
                free_persons_set.remove(prospect_min[1])
                self.logger.debug("person_to_cluster_assignment(): free_clusters_set = %s, "\
                    "free_persons_set = %s in second iteration after removal"\
                    , free_clusters_set, free_persons_set)
                self.logger.debug("lenth cluster_person_distance_list is %s before removing "\
                    "assinged clusters", len(cluster_person_distance_list))
                cluster_person_distance_list_temp = []
                for item in cluster_person_distance_list:
                    if item[0] in free_clusters_set and item[1] in free_persons_set:
                        cluster_person_distance_list_temp.append(item)
                cluster_person_distance_list = cluster_person_distance_list_temp
                self.logger.debug("lenth cluster_person_distance_list is %s after removing "\
                    "assinged clusters", len(cluster_person_distance_list))

        # there can be person_instances without cluster, and also cluster without person instance.
        if len(free_clusters_set) > 0:
            self.logger.debug("clusters %s are unassigned after completion of assignment" \
                , free_clusters_set)
        return person_to_cluster_assignmen_list


    def runner2(self, cluster_instances, parameter_space_instance, ai_db,cnt_up, cnt_down\
        , frame_count):
        "makeover of the legendary runner "
        cluster_person_distance_list = self.calculate_cluster_person_distance_list(\
            cluster_instances, parameter_space_instance)
        person_to_cluster_assignmen_list = self.person_to_cluster_assignment(\
            cluster_person_distance_list)

        for person_cluster in person_to_cluster_assignmen_list:
            person_instance = [x for x in self.person_instances if x.person_id \
                == person_cluster[0]][0]
            cluster_instance = [x for x in cluster_instances if x.cluster_id \
                == person_cluster[1]][0]

            person_instance.update_coords(cluster_instance.centroid_x, cluster_instance.centroid_y)
            person_instance.update_age(parameter_space_instance.age_reset_down_thres\
                , parameter_space_instance.age_reset_up_thres)
            person_instance.update_thrust()

            self.logger.info("matched person to cluster: Person ID: %s | cluster_id %s | "\
                "frame_count %s | P(x/y): (%s / %s) | thrust_absolute: %s | thrust_binary %s | "\
                "age %s  ", str(person_instance.person_id), str(cluster_instance.cluster_id)\
                , str(frame_count), str(cluster_instance.centroid_x)\
                , str(cluster_instance.centroid_y)\
                , str(person_instance.thrust_absolute), str(person_instance.thrust_binary)\
                , str(person_instance.age))

            if person_instance.crossing_up(parameter_space_instance.thrust_abs_crossing_threshold\
                , parameter_space_instance.thrust_bin_crossing_threshold) is True:
                cnt_up += 1
                change_up_or_down = 1
                person_instance.has_crossed_up = True
                # reset thrust
                person_instance.thrust_absolute = 0
                person_instance.thrust_binary = 0

                #  write message into db
                capacity, latest_person_count, direction \
                    = ai_db.get_current_data()
                latest_person_count = max(latest_person_count \
                    + change_up_or_down * direction, 0)
                ai_db.set_current_data(capacity, latest_person_count, direction)

                # logging
                self.logger.info("ID: %s crossed going up at %s " \
                    , str(person_instance.get_id()), str(time.strftime("%c")))
                self.logger.debug("current person count: %s" \
                    ,  str(latest_person_count))
                #self.logger_reporting.info("%s;%s;",  str(change_up_or_down * direction) \
                #    ,str(latest_person_count) )

            if person_instance.crossing_down(parameter_space_instance.thrust_abs_crossing_threshold\
                , parameter_space_instance.thrust_bin_crossing_threshold) is True:
                cnt_down += 1
                change_up_or_down = -1
                person_instance.has_crossed_down = True
                # reset thrust
                person_instance.thrust_absolute = 0
                person_instance.thrust_binary = 0

                # write message into db
                capacity, latest_person_count, direction \
                    = ai_db.get_current_data()
                latest_person_count = max(latest_person_count \
                    + change_up_or_down * direction, 0)
                ai_db.set_current_data(capacity, latest_person_count, direction)

                #logging
                self.logger.info("ID: %s crossed going down at %s " \
                    , str(person_instance.get_id()), str(time.strftime("%c")))
                self.logger.debug("current person count: %s "\
                    , str(latest_person_count))
                #self.logger_reporting.info("%s;%s;", str(change_up_or_down * direction) \
                #    , str(latest_person_count))
        return cnt_up, cnt_down



#--------------------------------------------------------------------------------------------------#
