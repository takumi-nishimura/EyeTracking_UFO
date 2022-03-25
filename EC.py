from re import S
import tobii_research as tr
import screeninfo
import tkinter as tk
import pyautogui as pg
from xarm.wrapper import XArmAPI
from scipy import signal
import numpy as np
import threading
import sys
import matplotlib.pyplot as plt
import time

def gaze_data_callback(gaze_data):
    global eye_x, eye_y

    right_point = list(gaze_data["right_gaze_point_on_display_area"])
    left_point = list(gaze_data["left_gaze_point_on_display_area"])

    eye_x = (left_point[0]+right_point[0])/2*s_width
    eye_y = (left_point[1]+right_point[1])/2*s_height

def eye(eyetracker):
    
    eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA,gaze_data_callback,as_dictionary=True)

    if condition == "q":
        eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA,gaze_data_callback)

class EYE:
    def __init__(self,x,y,size=80,color='blue'):
        self.x1 = x - size/2
        self.y1 = y - size/2
        self.x2 = x + size/2
        self.y2 = y + size/2
        self.size = size
        self.color = color
    
    def draw(self,canvas):
        canvas.delete('EYE')
        canvas.create_oval(self.x1,self.y1,self.x2,self.y2,fill=self.color,tag='EYE')
    
    def move(self):
        self.x1 = filt_P[0] - self.size/2
        self.y1 = filt_P[1] - self.size/2
        self.x2 = self.x1 + self.size/2
        self.y2 = self.y1 + self.size/2

class BUTTON:
    def __init__(self,x,y,button,size=250):
        self.button = button
        self.x1 = x - size/2
        self.y1 = y - size/2
        self.x2 = x + size/2
        self.y2 = y + size/2
        self.on = False
        self.on_time = 0
        self.x = 0
        self.y = 0

    def draw(self,canvas,reset=True):
        canvas.delete(self.button)
        if self.on:
            canvas.create_rectangle(self.x1,self.y1,self.x2,self.y2,outline='red',fill='red',tag=self.button)
        else:
            canvas.create_rectangle(self.x1,self.y1,self.x2,self.y2,outline='blue',fill='blue',tag=self.button)
        if reset:
            self.on = False
        else:
            pass

    def change(self,on_limit=50):
        self.s_on = 0
        if self.x1 < filt_P[0] and filt_P[0] < self.x2 and self.y1 < (filt_P[1]) and (filt_P[1]) < self.y2:
            self.on_time += 1
            if self.on_time > on_limit:
                self.s_on = 1
                self.on = True
        else:
            self.on_time = 0
        return self.s_on

class BREAK_OUT:
    TICK = 1
    def __init__(self):
        self.s = 0
        self.dx = 0
        self.dy = 0

        self.master = tk.Tk()

        self.is_playing = False

        self.canvas = tk.Canvas(self.master,width=s_width,height=s_height)

        self.createWidgets()
        
        self.keybind()
        self.draw()

    def createWidgets(self):
        self.center = (s_width//2,s_height//2)
        self.b_up = BUTTON(self.center[0]*0.5,self.center[1]*0.4,'up')
        self.b_down = BUTTON(self.center[0]*0.5,self.center[1]*1.4,'down')
        self.b_left = BUTTON(self.center[0]*0.15,self.center[1]*0.9,'left')
        self.b_right = BUTTON(self.center[0]*0.85,self.center[1]*0.9,'right')
        self.b_start = BUTTON(self.center[0]*1.5,self.center[1]*0.4,'start',180)
        self.b_end = BUTTON(self.center[0]*1.5,self.center[1]*1.3,'end',180)
        self.eye = EYE(self.center[0],self.center[1])

    def show(self,robot):
        self.xarm = robot
        self.is_playing = 1
        self.play()
        try:
            self.master.mainloop()
        except KeyboardInterrupt:
            self.quit()

    def play(self):
        global filt_P
        try:
            t = time.perf_counter()-start
            f = 1/(t-t_l[0])
            t_l[0] = t
            f_l.append(f)
            pos = [eye_x,eye_y]
            if np.isnan(pos[0]):
                pos[0] = 0
                if np.isnan(pos[1]):
                    pos[1] = 0
            filt_x = filt.lowpass(pos[0])
            filt_y = filt.lowpass(pos[1])
            filt_P = [filt_x[-1],filt_y[-1]]
            record_pos.append(filt_P[0])
            if self.is_playing == 1:
                self.operate()
                self.draw()
                self.master.after(self.TICK,self.play)
                if self.start == 1:
                    self.is_playing = 2
                    self.dx = 0
                    self.dy = 0
            elif self.is_playing == 2:
                self.operate()
                self.draw()
                self.master.after(self.TICK,self.play)
                self.xarm.SendDataToRobot(self.dx,self.dy)
                if self.end == 1:
                    self.is_playing = 3
            elif self.is_playing == 3:
                self.master.destroy()
                print('mean f',np.mean(f_l))
                N = 250
                freq = np.fft.fftfreq(N,0.004)
                sp = np.fft.fft(record_pos)
                Amp = np.abs(sp/(N/2))
                plt.plot(freq[1:int(N/2)],Amp[1:int(N/2)])
                # plt.show()
                sys.exit()
        except KeyboardInterrupt:
            self.quit()

    def operate(self):
        self.eye.move()
        self.up = self.b_up.change()
        self.down = self.b_down.change()
        self.left = self.b_left.change()
        self.right = self.b_right.change()
        self.start = self.b_start.change(on_limit=300)
        self.end = self.b_end.change(on_limit=300)
        self.dx += (self.right - self.left) * 0.04
        self.dy += (self.up - self.down) * 0.04
        self.dx = round(self.dx,3)
        self.dy = round(self.dy,3)

    def draw(self):
        self.b_up.draw(self.canvas)
        self.b_down.draw(self.canvas)
        self.b_left.draw(self.canvas)
        self.b_right.draw(self.canvas)
        self.b_start.draw(self.canvas,reset=False)
        self.b_end.draw(self.canvas,reset=False)
        self.eye.draw(self.canvas)
        self.canvas.pack()

    def quit(self, *args):
        self.master.quit()

    def keybind(self):
        self.master.bind("q", self.quit)

class RobotControl:
    def __init__(self,isEnableArm=False) -> None:
        self.xArmIP = '192.168.1.240'
        self.initX, self.initY, self.initZ, self.initRoll, self.initPitch, self.initYaw = 200,0,200,180,0,0
        if isEnableArm:
            self.arm = XArmAPI(self.xArmIP)
            self.InitializeAll(self.xArmIP)
            print('!!!ready!!!')

    def SendDataToRobot(self,x,y):
        self.mvpose = [self.initX+x,self.initY+y,self.initZ,self.initRoll,self.initPitch,self.initYaw]
        # self.arm.set_servo_cartesian(self.mvpose)
        print(self.mvpose)

    def InitializeAll(self,robotArm,isSetInitPosition=True):
        robotArm.connect()
        if robotArm.warn_code != 0:
            robotArm.clean_warn()
        if robotArm.error_code != 0:
            robotArm.clean_error()
        robotArm.motion_enable(enable=True)
        robotArm.set_mode(0)
        robotArm.set_state(state=0)
        if isSetInitPosition:
            robotArm.set_position(x=self.initX, y=self.initY, z=self.initZ, roll=self.initRoll, pitch=self.initPitch, yaw=self.initYaw, wait=True)
        else:
            robotArm.reset(wait=True)
        print('Initialized > xArm')

        robotArm.set_tgpio_modbus_baudrate(2000000)
        robotArm.set_gripper_mode(0)
        robotArm.set_gripper_enable(True)
        robotArm.set_gripper_position(850, speed=5000)
        robotArm.getset_tgpio_modbus_data(self.ConvertToModbusData(425))
        print('Initialized > xArm gripper')

        robotArm.set_mode(1)
        robotArm.set_state(state=0)

class FILT:
    def __init__(self,samplerate,fp,fs,gpass,gstop):
        self.data = [0]*30
        self.samplerate = samplerate
        self.Fs = fs
        fn = samplerate/2
        wp = fp/fn
        ws = fs/fn
        N, Wn = signal.buttord(wp,ws,gpass,gstop)
        self.b, self.a = signal.butter(4,Wn,'low')

    def lowpass(self,x):
        self.data.append(x)
        y = signal.filtfilt(self.b,self.a,self.data)
        return y

if __name__ == "__main__":
    start = time.perf_counter()
    t_l = [start]
    f_l = []

    condition = "a"

    # eyetracker initialize
    found_eyetrackers = tr.find_all_eyetrackers()
    my_eyetracker = found_eyetrackers[0]
    print("tobii model: ",my_eyetracker.model)
    eye_x = 0.5
    eye_y = 0.5

    record_pos = []

    filt = FILT(250,80,150,50,250)

    # get screen information
    s_info = screeninfo.get_monitors()
    if len(s_info) == 1:
        s_info = s_info[0]
        s_width = s_info.width
        s_height = s_info.height
    elif len(s_info) == 2:
        s_info = s_info[1]
        s_width = s_info.width
        s_height = s_info.height
    print("screen information: ",s_info)

    et = threading.Thread(target=eye(my_eyetracker))
    et.start

    xarm = RobotControl(isEnableArm=False)
    BREAK_OUT().show(xarm)