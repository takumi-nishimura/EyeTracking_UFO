def execute(eyetracker):
    gaze_data(eyetracker)

import tobii_research as tr
import time

global_gaze_data = None

def gaze_data_callback(gaze_data):
    global global_gaze_data
    global_gaze_data = gaze_data

def gaze_data(eyetracker):
    global global_gaze_data

    print(eyetracker.model)
    eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA,gaze_data_callback,as_dictionary=True)

    time.sleep(2)

    eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA,gaze_data_callback)
    print(global_gaze_data)

found = tr.find_all_eyetrackers()
my = found[0]

execute(my)