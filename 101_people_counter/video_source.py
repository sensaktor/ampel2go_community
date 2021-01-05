"""Video Sourc is a video or a file. Within each Video, there are many instances of class Frame"""
#--------------------------------------------------------------------------------------------------#

import logging
import cv2
import time



class VideoSource:
    "video source class for training of data"
    def __init__(self):
        self.args_input = None
        self.logger = logging.getLogger('training_logger')
        self.cap = None
        self.backgroundsubstractor = None
        self.parameter_space_instance = ParameterSpace()
        self.frame_height = None
        self.frame_width = None
        self.expected_up_down = ()
        self.output = None
        self.out_stream = None
        self.args_output = None

    def open_input(self, args_input, args_output):
        "opens videos"
        self.args_input = args_input
        self.args_output = args_output
        if self.args_input == 'camera':
            #mac:
            #self.cap = cv2.VideoCapture(0)
            #jetson 
            self.cap = cv2.VideoCapture("/dev/video0")
            if not self.cap.isOpened():
                self.logger.error("Cannot open camera")
                exit()
        else:
            file_extension = args_input[-3:]
            if file_extension in ("mov", "avi"):
                self.cap = cv2.VideoCapture(args_input)
            else:
                raise ValueError("only mov or avi allowed")

        try:
            expected_up = int(args_input[-16:-13])
            expected_down = int(args_input[-7:-4])
            self.expected_up_down = (expected_up, expected_down)
        except ValueError:
            self.logger.warning("Input file name does not contain target values for up"\
                "and down.")
            self.expected_up_down = (-1, -1)


        self.logger.info("input named '%s' is chosen ", args_input )
        self.frame_width  = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.frame_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)


        if args_output:
            if args_output[-3:] != "avi":
                raise Exception("Output file must have extenstion .avi")
            self.args_output = args_output
            self.out_stream = cv2.VideoWriter(self.args_output, cv2.VideoWriter_fourcc(
                'moment', 'J', 'P', 'G'), 10, (int(self.frame_width), int(self.frame_height)))


    def create_backgroundsubstractor(self):
        "initiates the backgroundsubsctractor to 'see' moving parts"
        self.backgroundsubstractor = cv2.createBackgroundSubtractorMOG2(\
            history = self.parameter_space_instance.history\
                , varThreshold = self.parameter_space_instance.var_threshold\
            )

    def get_next_frame(self):
        "gets the next frame"
        last_frame = False
        ret, frame = self.cap.read()
        if not ret:
            last_frame = True
            self.logger.info("last Frame %s ", last_frame)

        if self.args_output:
            self.out_stream.write(frame)
        self.logger.debug('got next frame')
        return frame, last_frame

    def close_video(self):
        "closes the video"
        self.cap.release()
        if self.args_output:
            self.out_stream.release()



class ParameterSpace():
    "Class that contains parameters only"
    def __init__(self):
        self.id = None
        self.history = None
        self.var_threshold = None
        self.new_person_horizontal_threshold = None
        self.new_person_vertical_threshold = None
        self.age_reset_up_thres = None
        self.age_reset_down_thres = None
        self.thrust_abs_crossing_threshold = None
        self.thrust_bin_crossing_threshold = None
        self.person_age_threshold = None
        self.crop_window_up = None
        self.crop_window_down = None

    def assign_parameter_space(self, parameter_space_id, frame_height):
        "assigns parameters of olash to video_source_instance"
        if parameter_space_id == 'olash':
            self.id = 'olash'
            self.history = 300
            self.var_threshold = 80
            self.new_person_horizontal_threshold = 150
            self.new_person_vertical_threshold = 170
            self.thrust_abs_crossing_threshold = 150
            self.thrust_bin_crossing_threshold = 3
            self.person_age_threshold = 3
            self.age_reset_up_thres = int(1 * (frame_height/5))
            self.age_reset_down_thres = int(3.8 * (frame_height/5))
            self.crop_window_up = int(0.01 * (frame_height/5))
            self.crop_window_down = int(4.5 * (frame_height/5))

        elif parameter_space_id == 'markthalle':
            self.id = 'markthalle'
            self.history = 300
            self.var_threshold = 80
            self.new_person_horizontal_threshold = 175
            self.new_person_vertical_threshold = 170
            self.thrust_abs_crossing_threshold = 140
            self.thrust_bin_crossing_threshold = 3
            self.person_age_threshold = 2
            self.age_reset_up_thres = int(1 * (frame_height/5))
            self.age_reset_down_thres = int(4 * (frame_height/5))
            self.crop_window_up = int(0.01 * (frame_height/5))
            self.crop_window_down = int(4.0 * (frame_height/5))
        else:
            raise NameError('The chosen parameter space does not exist')
