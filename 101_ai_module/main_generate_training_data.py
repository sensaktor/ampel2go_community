



"main function, entry point for "
import logging
import argparse
import video_source as vs
import frame as f
import contour as c
import cv2
import time
import pickle
import pandas as pd
import datetime
import os

if __name__ == "__main__":

#--------------------------------------------------------------------------------------------------#
    # Logger & Parameter

    # Logger: create logger
    logger = logging.getLogger('training_logger')
    logger.setLevel(logging.DEBUG)

    # Logger: create file handler which logs even debug messages
    filehandler_debug = logging.FileHandler('../204_logs/training_debug.log')
    filehandler_debug.setLevel(logging.DEBUG)

    # Logger: create file handler which logs even debug messages
    filehandler_info = logging.FileHandler('../204_logs/training_info.log')
    filehandler_info.setLevel(logging.INFO)



    # Logger: create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Logger: create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s |')
    filehandler_debug.setFormatter(formatter)
    filehandler_info.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Logger: add the handlers to the logger
    logger.addHandler(filehandler_debug)
    logger.addHandler(filehandler_info)
    logger.addHandler(ch)

    # END Logger & Parameter
#--------------------------------------------------------------------------------------------------#


#--------------------------------------------------------------------------------------------------#
    # Parse Args

    parser = argparse.ArgumentParser(
        description='Ampel2Go training module',
        epilog="")
    parser.add_argument(
        '-i', '--input',  help="If input is given, the videofile will be used as input,"\
            , default='thresh_frame_1.png')
    parser.add_argument(
        '-o', '--output',
        help="if this arg is given, the video is saved into output file = save file")
    parser.add_argument(
        '-c', '--customer',
        help="if this arg is given, the video is saved into output file = save file", required=True)
    parser.add_argument(
        '-s', '--playback_speed',
        help="amount of miliseconds waitingtime between each loop  normal inserts waiting "\
            "time between each loop", default=0)
    args = parser.parse_args()

    # END Parse Args #
#--------------------------------------------------------------------------------------------------#

    # Only a check whether the outputfilename exists: 
    print(args.customer)
    outputfilename_csv = '../109_training/observations_' + args.customer + '_csv/observations_' + os.path.basename(args.input) \
        + '_' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.csv'

    outputfilename_pickle ='../109_training/observations_' + args.customer + '_pickle/observations_' + os.path.basename(args.input) \
        + '_' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.pickle'

    df = pd.DataFrame()

    df.to_csv(outputfilename_csv, mode='a', index=False, sep=';', header=False)


    # start of routine

    video_source_instance = vs.VideoSource()



    video_source_instance.open_input(args.input)
    video_source_instance.parameter_space_instance.assign_parameter_space(args.customer, video_source_instance.frame_height)
    video_source_instance.create_backgroundsubstractor()



    FRAME_COUNT = 0
    observations_by_input = []

    for frame_instance in range(video_source_instance.total_frame_count):
        frame_instance = f.Frame()
        frame_instance.frame_id = args.input + '-' + str(FRAME_COUNT).rjust(6, '0')

        frame_instance.frame_color, last_frame  = video_source_instance.get_next_frame()
        if last_frame:
            logger.info("last frame processed, over and out.")
            break

        logger.debug("Received new Frame and assigned frame_id %s", frame_instance.frame_id)

        frame_instance.enhance_contrast()

        frame_instance.subsctract_background(video_source_instance.backgroundsubstractor)
        frame_instance.find_contours()
        frame_instance.initiate_contour_instances()
        frame_instance.filter_contour_instances(video_source_instance.parameter_space_instance.crop_window_up\
            , video_source_instance.parameter_space_instance.crop_window_down)
        frame_instance.calculate_contour_instances_properties()

        key_input = frame_instance.assign_contour_instances_labels()
        if key_input ==27:
            raise EOFError
        if key_input == 8:
            observations_by_input.pop()
            continue
        observations_by_frame = frame_instance.get_observations_by_frame()
        observations_by_input.extend(observations_by_frame)
        time.sleep(float(args.playback_speed)*0.1)
        FRAME_COUNT += 1


    # write output into files:

    df = pd.DataFrame(observations_by_input)

    

    #output filename defined above, so that potential error happens befor generating the data


    df.to_csv(outputfilename_csv, mode='a', index=False, sep=';', header=False)



    with open(outputfilename_pickle,'wb') as file:
        pickle.dump(df, file)

    # with open('test.txt', 'w') as file :
    #     file.write(str(observations_by_input))


else:
    raise ImportError("Run this file directly, don't import it!")
