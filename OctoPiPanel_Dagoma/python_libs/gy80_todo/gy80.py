#!/usr/bin/env python

from __future__ import print_function

import sys
from time import sleep, time
from math import pi, sin, cos, asin, acos, atan2, sqrt
import numpy as np
import smbus

try:
    from adxl345 import ADXL345
except ImportError:
    print("error : import ADXL345")
    sys.exit(1)
    
try:
    from hmc5883l import HMC5883L
except ImportError:
    print("error : import HMC5883L")
    sys.exit(1)
    
try:
    from bmp085 import BMP085
except ImportError:
    print("error : import BMP085")
    sys.exit(1)
    
try:
    from l3g4200d import L3G4200D
except ImportError:
    print("error : import L3G4200D")
    sys.exit(1)
    
try:
    from i2cutils import i2c_raspberry_pi_bus_number
except ImportError:
    print("error : import i2cutils")
    sys.exit(1)
    
try:
    from quaternions import _check_close
    from quaternions import quaternion_to_rotation_matrix_rows, quaternion_from_rotation_matrix_rows
    from quaternions import quaternion_from_axis_angle
    from quaternions import quaternion_from_euler_angles, quaternion_to_euler_angles
    from quaternions import quaternion_multiply, quaternion_normalise
except ImportError:
    print("error : import quaternions")
    sys.exit(1)
    
class GY80(object):
    def __init__(self, bus=None):
        if bus is None:
            bus = smbus.SMBus(1)

        #Default ADXL345 range +/- 2g is ideal for telescope use
        self.accel = ADXL345(bus, 0x53, name="accel")
        self.gyro = L3G4200D(bus, 0x69, name="gyro")
        self.compass = HMC5883L(bus, 0x1e, name="compass")
        self.barometer = BMP085(bus, 0x77, name="barometer")

        self._last_gyro_time = 0 #needed for interpreting gyro
        self.read_gyro_delta() #Discard first reading
        q_start = self.current_orientation_quaternion_mag_acc_only()
        self._q_start = q_start
        self._current_hybrid_orientation_q = q_start
        self._current_gyro_only_q = q_start

    def update(self):
        """Read the current sensor values & store them for smoothing. No return value."""
        t = time()
        delta_t = t - self._last_gyro_time
        if delta_t < 0.020:
            #Want at least 20ms of data
            return
        v_gyro = np.array(self.read_gyro(), np.float)
        v_acc = np.array(self.read_accel(), np.float)
        v_mag = np.array(self.read_compass(), np.float)
        self._last_gyro_time = t

        #Gyro only quaternion calculation (expected to drift)
        rot_mag = sqrt(sum(v_gyro**2))
        v_rotation = v_gyro / rot_mag
        q_rotation = quaternion_from_axis_angle(v_rotation, rot_mag * delta_t)
        self._current_gyro_only_q = quaternion_multiply(self._current_gyro_only_q, q_rotation)
        self._current_hybrid_orientation_q = quaternion_multiply(self._current_hybrid_orientation_q, q_rotation)

        if abs(sqrt(sum(v_acc**2)) - 1) < 0.3:
            #Approx 1g, should be stationary, and can use this for down axis...
            v_down = v_acc * -1.0
            v_east = np.cross(v_down, v_mag)
            v_north = np.cross(v_east, v_down)
            v_down /= sqrt((v_down**2).sum())
            v_east /= sqrt((v_east**2).sum())
            v_north /= sqrt((v_north**2).sum())
            #Complementary Filter
            #Combine (noisy) orientation from acc/mag, 2%
            #with (drifting) orientation from gyro, 98%
            q_mag_acc = quaternion_from_rotation_matrix_rows(v_north, v_east, v_down)
            self._current_hybrid_orientation_q = tuple(0.02*a + 0.98*b for a, b in
                                                       zip(q_mag_acc, self._current_hybrid_orientation_q))


        #1st order approximation of quaternion for this rotation (v_rotation, delta_t)
        #using small angle approximation, cos(theta) = 1, sin(theta) = theta
        #w, x, y, z = (1, v_rotation[0] * delta_t/2, v_rotation[1] *delta_t/2, v_rotation[2] * delta_t/2)
        #q_rotation = (1, v_rotation[0] * delta_t/2, v_rotation[1] *delta_t/2, v_rotation[2] * delta_t/2)
        return

    def current_orientation_quaternion_hybrid(self):
        """Current orientation using North, East, Down (NED) frame of reference."""
        self.update()
        return self._current_hybrid_orientation_q

    def current_orientation_quaternion_mag_acc_only(self):
        """Current orientation using North, East, Down (NED) frame of reference."""
        #Can't use v_mag directly as North since it will usually not be
        #quite horizontal (requiring tilt compensation), establish this
        #using the up/down axis from the accelerometer.
        #Note assumes starting at rest so only acceleration is gravity.
        v_acc = np.array(self.read_accel(), np.float)
        v_mag = np.array(self.read_compass(), np.float)
        return self._quaternion_from_acc_mag(v_acc, v_mag)

    def _quaternion_from_acc_mag(self, v_acc, v_mag):
        v_down = v_acc * -1.0 #(sign change depends on sensor design?)
        v_east = np.cross(v_down, v_mag)
        v_north = np.cross(v_east, v_down)
        #Normalise the vectors...
        v_down /= sqrt((v_down ** 2).sum())
        v_east /= sqrt((v_east ** 2).sum())
        v_north /= sqrt((v_north ** 2).sum())
        return quaternion_from_rotation_matrix_rows(v_north, v_east, v_down)

    def current_orientation_euler_angles_hybrid(self):
        """Current orientation using yaw, pitch, roll (radians) using sensor's frame."""
        return quaternion_to_euler_angles(*self.current_orientation_quaternion_hybrid())

    def current_orientation_euler_angles_mag_acc_only(self):
        """Current orientation using yaw, pitch, roll (radians) using sensor's frame."""
        return quaternion_to_euler_angles(*self.current_orientation_quaternion_mag_acc_only())

    def read_accel(self, scaled=True):
        """Returns an X, Y, Z tuple; if scaled in units of gravity."""
        accel = self.accel
        accel.read_raw_data()
        if scaled:
            return accel.accel_scaled_x, accel.accel_scaled_y, accel.accel_scaled_z
        else:
            return accel.accel_raw_x, accel.accel_raw_y, accel.accel_raw_z

    def read_gyro(self, scaled=True):
        """Returns an X, Y, Z tuple; If scaled uses radians/second.

        WARNING: Calling this method directly will interfere with the higher-level
        methods like ``read_gyro_delta`` which integrate the gyroscope readings to
        track orientation (it will miss out on the rotation reported in this call).
        """
        gyro = self.gyro
        gyro.read_raw_data()
        if scaled:
            return gyro.gyro_scaled_x, gyro.gyro_scaled_y, gyro.gyro_scaled_z
        else:
            return gyro.gyro_raw_x, gyro.gyro_raw_y, gyro.gyro_raw_z

    def read_gyro_delta(self):
        """Returns an X, Y, Z tuple - radians since last call."""
        g = self.gyro
        t = time()
        g.read_raw_data()
        d = np.array([g.gyro_scaled_x, g.gyro_scaled_y, g.gyro_scaled_z], np.float) / (t - self._last_gyro_time)
        self._last_gyro_time = t
        return d

    def read_compass(self, scaled=True):
        """Returns an X, Y, Z tuple."""
        compass = self.compass
        compass.read_raw_data()
        if scaled:
            return compass.scaled_x, compass.scaled_y, compass.scaled_z
        else:
            return compass.raw_x, compass.raw_y, compass.raw_z
            
def imu_degrees():
    imu = GY80()
    imu.update()   
#    w, x, y, z = imu.current_orientation_quaternion_mag_acc_only()
    w, x, y, z = imu._current_gyro_only_q
    yaw, pitch, roll = quaternion_to_euler_angles(w, x, y, z)
    return(yaw   * 180.0 / pi + 180, pitch * 180.0 / pi + 180, roll  * 180.0 / pi + 180)
	
def imu_baro():
    bus = smbus.SMBus(1)
    bmp085 = BMP085(bus, 0x77 , "BMP085")
    temperature, pressure, altitude = bmp085.read_temperature_and_pressure()
    return(temperature, pressure, altitude)
    

