import serial
import struct
import serial

class SerialCar(object):
	def __init__(self, port, speed = 115200):
		self._ser = serial.Serial(port, speed)
		self._extra = 0
	
	def _set_speed(self, left, right):
		left = int(round(left * 126))
		right = int(round(right * 126))

		left = min(126, max(-126, left))
		right = min(126, max(-126, right))

		self._ser.write(struct.pack('Bbbb', 0xff, -right, -left, self._extra))
	
	def set_speed(self, speed, turn):
		speed *= 0.4
		turn *= 0.7

		left = speed - turn / 2.0
		right = speed + turn / 2.0
		self._set_speed(left, right)
	
	def set_extra(self, extra):
		self._extra = extra
		
if __name__ == "__main__":
	import time

	a = SerialCar('/dev/ttyUSB0', 38400)
	a.set_extra(4)
	while True:
		a._set_speed(0.35, 0.2)
		time.sleep(0.1)
