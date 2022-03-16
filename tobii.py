import tobii_research as tr
import time
import cv2
import sys

global_gaze_data = None

def gaze_data_callback(gaze_data):
    global global_gaze_data
    global_gaze_data = gaze_data
    print(gaze_data)

def gaze_data(eyetracker):
    global global_gaze_data

    print(eyetracker.model)
    eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA,gaze_data_callback,as_dictionary=True)

    time.sleep(5)

    eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA,gaze_data_callback)
    print(global_gaze_data)
    # sys.exit()

def execute(eyetracker):
    gaze_data(eyetracker)

def draw_caribration_points(point):
    img_file_name = 'img/image' + str(point[0]) + '_' + str(point[1]) + '.png'
    img = cv2.imread(img_file_name)
    cv2.namedWindow('screen', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(
        'screen', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow('screen', img)
    cv2.waitKey(2500)  # 2.5秒キャリブレーションする

def calibration(eyetracker):
    calibration = tr.ScreenBasedCalibration(eyetracker)
    calibration.enter_calibration_mode()

    points_to_calibrate = [(0.5,0.5),(0.1,0.1),(0.1,0.9),(0.9,0.1),(0.9,0.9)]

    for point in points_to_calibrate:
        print(("Show a point on screen at {0}.").format(point))
        draw_caribration_points(point)
        
        print(("Collecting data at {0}.").format(point))
        
        if calibration.collect_data(point[0], point[1]) != tr.CALIBRATION_STATUS_SUCCESS:
            calibration.collect_data(point[0], point[1])

    print('Computing and applying calibration.')
    calibration_result = calibration.compute_and_apply()
    print(('Compute and apply returned {0} and collected at {1} points.').
          format(calibration_result.status, len(calibration_result.calibration_points)))

    calibration.leave_calibration_mode()
    print('Left calibration mode.')

found = tr.find_all_eyetrackers()
my = found[0]

# calibration(my)

execute(my)
sys.exit()