



"main function, entry point for "
import logging
import argparse
import time
import pickle
import video_source as vs
import frame as f
import group as g
import ai_db as db

if __name__ == "__main__":

#--------------------------------------------------------------------------------------------------#
    # Logger & Parameter

    # Logger: create logger
    logger = logging.getLogger('training_logger')
    logger.propagate = False
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

    # Logger: create file handler for "test for Up/Down", where only the results Passed / not passed
    # are recorded
    filehandler_testresults = logging.FileHandler('../204_logs/test_results.log')
    filehandler_testresults.setLevel(logging.WARNING)

    # Logger: create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s |')
    filehandler_debug.setFormatter(formatter)
    filehandler_info.setFormatter(formatter)
    filehandler_testresults.setFormatter(formatter)
    ch.setFormatter(formatter)


    # Logger: add the handlers to the logger
    logger.addHandler(filehandler_debug)
    logger.addHandler(filehandler_info)
    logger.addHandler(filehandler_testresults)
    logger.addHandler(ch)
    
    # END Logger & Parameter
#--------------------------------------------------------------------------------------------------#


#--------------------------------------------------------------------------------------------------#
    # Parse Args

    parser = argparse.ArgumentParser(
        description='Ampel2Go training module',
        epilog="")
    parser.add_argument(
        '-i', '--input',  help="If input is given, the videofile will be used as input,else camera"\
            , default='camera')
    parser.add_argument(
        '-o', '--output',
        help="if this arg is given, the video is saved into output file = save file")
    parser.add_argument(
        '-c', '--customer',
        help="if this arg is given, the video is saved into output file = save file", default='olash')
    parser.add_argument(
        '-s', '--playback_speed',
        help="amount of miliseconds waitingtime between each loop  normal inserts waiting "\
            "time between each loop", default=0)
    parser.add_argument(
        '--headless', action="store_true",
        help="Runs program headless, without visual output", default=False)
    parser.add_argument(
        '-l', '--logging', action="store_true",
        help="Runs program without logging, whenever input == camera, logging is turned off"\
            "anyways", default=False)
    args = parser.parse_args()

    # END Parse Args #
#--------------------------------------------------------------------------------------------------#



    if args.logging is False:
        logging.disable(logging.CRITICAL)

    if args.output:
        logger.info("output is saved in file %s", args.output)


    video_source_instance = vs.VideoSource()


    video_source_instance.open_input(args.input, args.output)

    video_source_instance.parameter_space_instance.assign_parameter_space(args.customer\
        , video_source_instance.frame_height)

    video_source_instance.create_backgroundsubstractor()



    FRAME_COUNT = 0
    FRAME_COUNT_TIMER = 0
    observations_by_input = []
    regressorpath = '../109_people_counter/regressor_' + args.customer + '.pickle'
    trained_model = pickle.load(open(regressorpath, 'rb'))

    #persons
    group_instance = g.Group()
    CNT_UP = 0
    CNT_DOWN = 0
    #ai_db
    SQL_CONNECTION = 'sqlite:///../104_user_display/db.sqlite3'
    ai_db = db.AiDatabase(SQL_CONNECTION)

    while True:
        



        frame_instance = f.Frame()
        #frame_instance.frame_id = args.input + '-' + str(FRAME_COUNT).rjust(6, '0')
        frame_instance.frame_id = str(FRAME_COUNT).rjust(6, '0')
        frame_instance.frame_color, last_frame  = video_source_instance.get_next_frame()
        logger.info("lhello.%s %s", frame_instance.frame_color, last_frame)

        if last_frame:
            logger.info("last frame processed, over and out.")
            break

        logger.debug("Received new Frame and assigned frame_id %s", frame_instance.frame_id)

        frame_instance.enhance_contrast()

        frame_instance.subsctract_background(video_source_instance.backgroundsubstractor)

        frame_instance.find_contours()

        contour_instances = frame_instance.initiate_filter_calculate_contour_instances(\
            video_source_instance.parameter_space_instance.crop_window_up\
            , video_source_instance.parameter_space_instance.crop_window_down, trained_model)

        if not args.headless:
            key_input = frame_instance.show_contour_instances()
            if key_input ==27:
                raise EOFError
            #key_input = frame_instance.show_cropped_contours()
            #if key_input ==27:
            #    raise EOFError
            #timer
            if FRAME_COUNT_TIMER == 0:
                tic = time.perf_counter()
            FRAME_COUNT_TIMER += 1
            if FRAME_COUNT_TIMER % 50 == 0:
                toc = time.perf_counter()
                toc_tic = toc - tic
                frames_per_second = FRAME_COUNT_TIMER / toc_tic
                logger.info("Current frames per second: %s", frames_per_second)
                print(frames_per_second)
                FRAME_COUNT_TIMER = 0
                tic = time.perf_counter()

        frame_instance.determine_clusters2()
        frame_instance.calculate_cluster_properties()

        # update persons
        group_instance.next_frame_aging(FRAME_COUNT)
        CNT_UP, CNT_DOWN = group_instance.runner2(frame_instance.cluster_instances\
            , video_source_instance.parameter_space_instance\
            , ai_db, CNT_UP, CNT_DOWN, FRAME_COUNT)


        if not args.headless:
            key_input = frame_instance.show_person_instances(group_instance.person_instances\
                , CNT_UP, CNT_DOWN)
            if key_input ==27:
                raise EOFError

        time.sleep(float(args.playback_speed)*0.1)
        FRAME_COUNT += 1


    video_source_instance.close_video()


    PASSED = 0
    if CNT_UP == video_source_instance.expected_up_down[0] \
        and CNT_DOWN == video_source_instance.expected_up_down[1]:
        PASSED = 1

    logger.info("Testing-Result: up target / up estimation: %s / %s "\
        ", down target / down estimation : %s / %s"\
        , str(video_source_instance.expected_up_down[0]), str(CNT_UP)\
        , str(video_source_instance.expected_up_down[1]) , str(CNT_DOWN))
    logger.warning("PASSED: %s | input: %s | assigned_parameter_space: %s"\
        , PASSED, args.input, args.customer)


else:
    raise ImportError("Run this file directly, don't import it!")
