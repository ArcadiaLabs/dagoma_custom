#!/usr/bin/env python

# WORKING
# uses complete custom gy80 lib

from datetime import datetime

try:
	from gy80 import GY80
	from gy80 import imu_degrees
	from gy80 import imu_baro
except ImportError as e:
	print("error import gy80 "+e)
	sys.exit(1)
    

while True:
	# startTime = datetime.now()
	degrees = imu_degrees()
	baro = imu_baro()
	# duration = datetime.now()-startTime
	# duration = duration.microseconds / 1000000.0
	# print ("yaw %0.1f, pitch %0.1f, roll %0.1f (duration : %f)" % (degrees[0], degrees[1], degrees[2], duration))
	print ("yaw %0.1f, pitch %0.1f, roll %0.1f, temp %0.1f, baro %0.2f, alt %0.1f" % (degrees[0], degrees[1], degrees[2], baro[0], baro[1], baro[2]))
	
#	baro = imu_baro()
#	print ("temp %0.1f, baro %0.2f, alt %0.1f" % (baro[0], baro[1], baro[2]))
