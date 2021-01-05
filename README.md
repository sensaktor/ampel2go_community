# Ampel2Go - An algorithm to count the amount of bidirectional movements

We have built a python library that is capable of detecting moving objects and counting the direction in real-time using minimal computing power (i.e. it runs on a RaspberryPi 4b)

After our intensive research, we have concluded this to be by far the best performing open source people counter using low cost edge-computers.


Content: 

- 101_ai_module: This is the main and core part of our work containting the movement detection and counting algorithms
- 102_user_display_and_settings_module: A django application that reads relevant values (counts, etc. ) from the central database, displays it, and enables changes via the settings screen.
- 103_remote_control_module: This is a second option to changes settings accomanying the settings module using a infrared-remote-control
- 201_sample_videos: Contains sample videos to be referenced in 101_ai_module
- 204_logs: Folder containing logs


# How to get started with the detection algorithm using pretrained models

1. Clone repo and cd into the folder
2. Start the pipenv ("pipenv shell") (the pipfile is located in the parent directory) 
3. Run this command: "python3 101_people_counter/main_people_counter.py  --input 201_sample_videos/olash3h043_testtype-norma-height-240-up-000-down-001.avi"
4. Three windows will pop up displaying the following:


https://youtu.be/QgYK4C2Ncl8


# How to get started with the labeling application

You can train the model to adapt to special situations. In our sample-videos, the model is trained to ignore the moving door that enters the picture from below. Entry point is the file: main_generate_training_data.py, which starts the labeling procedure.


# If you have any questions feel free to contact us!





