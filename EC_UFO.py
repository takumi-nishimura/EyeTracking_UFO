import tkinter as tk
import pyautogui as pg
from screeninfo import get_monitors
from xarm.wrapper import XArmAPI
# import tobii_research as tr

class EYE:
	def __init__(self,x,y,size=30,color='blue'):
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
		self.x1 = pg.position()[0] - self.size/2
		self.y1 = pg.position()[1] - self.size/2 - 28
		self.x2 = self.x1 + self.size/2
		self.y2 = self.y1 + self.size/2

class BUTTON:
	def __init__(self,x,y,button,size=180):
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

	def change(self,on_limit=200):
		self.s_on = 0
		if self.x1 < pg.position()[0] and pg.position()[0] < self.x2 and self.y1 < (pg.position()[1]-28) and (pg.position()[1]-28) < self.y2:
			self.on_time += 1
			# print(self.button,self.on_time)
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

		self.window_width = self.master.winfo_screenwidth()
		self.window_height = self.master.winfo_screenheight()
		print(self.window_width,self.window_height)
		s = get_monitors()
		print(s[0].width)

		self.is_playing = False

		self.canvas = tk.Canvas(self.master,width=self.window_width,height=self.window_height)

		self.createWidgets()
		
		self.keybind()
		self.draw()

	def createWidgets(self):
		self.center = (self.window_width//2,self.window_height//2)
		self.b_up = BUTTON(self.center[0]*0.5,self.center[1]*0.4,'up')
		self.b_down = BUTTON(self.center[0]*0.5,self.center[1]*1.4,'down')
		self.b_left = BUTTON(self.center[0]*0.15,self.center[1]*0.9,'left')
		self.b_right = BUTTON(self.center[0]*0.85,self.center[1]*0.9,'right')
		self.b_start = BUTTON(self.center[0],self.center[1]*0.3,'start',100)
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
		try:
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
			else:
				self.quit()
		except KeyboardInterrupt:
			self.quit()

	def operate(self):
		self.eye.move()
		self.up = self.b_up.change()
		self.down = self.b_down.change()
		self.left = self.b_left.change()
		self.right = self.b_right.change()
		self.start = self.b_start.change(on_limit=300)
		self.dx += (self.right - self.left) * 0.002
		self.dy += (self.up - self.down) * 0.002
		self.dx = round(self.dx,3)
		self.dy = round(self.dy,3)

	def draw(self):
		self.b_up.draw(self.canvas)
		self.b_down.draw(self.canvas)
		self.b_left.draw(self.canvas)
		self.b_right.draw(self.canvas)
		self.b_start.draw(self.canvas,reset=False)
		self.eye.draw(self.canvas)
		self.canvas.pack()

	def quit(self, *args):
		self.master.quit()

	def keybind(self):
		self.master.bind("q", self.quit)

class EyeTracking:
	def __init__(self):
		# self.Found_EyeTrackers = tr.find_all_eyetrackers()
		# self.My_EyeTracker =  self.Found_EyeTrackers[0]

		self.e_x = []
		self.e_y = []
		
		self.s_info = get_monitors()[0]
		self.w_width = self.s_info.width
		self.w_height = self.s_info.height

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
		robotArm.set_mode(0)             # set mode: position control mode
		robotArm.set_state(state=0)      # set state: sport state
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

if __name__ in '__main__':
	# xarm = RobotControl(isEnableArm=False)
	# BREAK_OUT().show(xarm)
	eyetracking = EyeTracking()
	# keycode = input('Input > "s": start control \n')
	# if keycode == 's':					
	# 	taskStartTime = time.perf_counter()
		# BREAK_OUT().show()
	# BREAK_OUT().show()