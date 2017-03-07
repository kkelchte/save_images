#!/usr/bin/env python
import rospy
# OpenCV2 for saving an image
from cv_bridge import CvBridge, CvBridgeError
import cv2
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
from std_msgs.msg import Empty

import sys, select, tty, os, os.path

# Instantiate CvBridge
bridge = CvBridge()

saving_location = '/home/klaas/unknown'

index=0
last_control=[0,0,0,0,0,0]
last_imu=[0,0,0]
last_position=[]
ready=False
start_time=0
delay_evaluation = 3

def write_info():
  if not ready or (rospy.get_time()-start_time) < delay_evaluation: return
  with open(saving_location+'/meta_info.txt','a') as metafile:
    metafile.write("{0:010d} {1}\n".format(index, str(last_imu)[1:-1]))
  with open(saving_location+'/control_info.txt','a') as controlfile:
    controlfile.write("{0:010d} {1[0]} {1[1]} {1[2]} {1[3]} {1[4]} {1[5]}\n".format(index, last_control))
  with open(saving_location+'/position_info.txt','a') as positionfile:
    positionfile.write("{0:010d} {1}\n".format(index, str(last_position)[1:-1]))
  
def image_callback(msg):
  global index
  if not ready or (rospy.get_time()-start_time) < delay_evaluation: return
  try:
    # Convert your ROS Image message to OpenCV2
    cv2_img = bridge.imgmsg_to_cv2(msg, "bgr8")
  except CvBridgeError, e:
    print(e)
  else:
    # Save your OpenCV2 image as a jpeg 
    print('write image: {:010d}'.format(index))
    cv2.imwrite(saving_location+"/RGB/{:010d}.jpg".format(index), cv2_img)
    write_info()
    index+=1

def control_callback(data):
  global last_control
  last_control=[data.linear.x,
			data.linear.y,
			data.linear.z,
			data.angular.x,
			data.angular.y,
			data.angular.z]
  #print('received control:', data.linear.x,', ',data.linear.y,', ',data.linear.z)

def odometry_callback(data):
  global last_imu
  last_imu=[data.pose.pose.orientation.x,
	    data.pose.pose.orientation.y,
	    data.pose.pose.orientation.z]
  #print('received odo: ',last_imu)
  
def imu_callback(data):
  global last_imu
  last_imu=[data.orientation.x,
	    data.orientation.y,
	    data.orientation.z,
	    data.orientation.w,
	    data.angular_velocity.x,
	    data.angular_velocity.y,
	    data.angular_velocity.z,
	    data.linear_acceleration.x,
	    data.linear_acceleration.y,
	    data.linear_acceleration.z]
  
def gt_callback(data):
  global last_position
  last_position=[data.pose.pose.position.x,
		 data.pose.pose.position.y,
		 data.pose.pose.position.z]
  print(last_position)
  
def ready_callback(msg):
  global ready, start_time
  if not ready:
    ready=True
    start_time=rospy.get_time()
    print('evaluate start: ', start_time)

if __name__=="__main__":
  if rospy.has_param('delay_evaluation'):
    delay_evaluation=rospy.get_param('delay_evaluation')
  
  # create necessary directories
  if rospy.has_param('saving_location'):
    loc=rospy.get_param('saving_location')
    if loc[0]=='/':
      saving_location=loc
    else:
      saving_location='/home/klaas/pilot_data/'+loc
  if not os.path.exists(saving_location+'/RGB'):
      os.makedirs(saving_location+'/RGB')
  #else:
      #raise IOError('saving folder: '+saving_location+' already exists.')


  rospy.init_node('create_dataset', anonymous=True)
  #rospy.Subscriber('/bebop/cmd_vel', Twist, control_callback)
  #rospy.Subscriber('/bebop/image_raw', Image, image_callback)
  #rospy.Subscriber('/bebop/odom', Odometry, odometry_callback)

  rospy.Subscriber('/ardrone/kinect/image_raw', Image, image_callback)
  rospy.Subscriber('/ardrone/imu', Imu, imu_callback)
  rospy.Subscriber('/cmd_vel', Twist, control_callback)
  rospy.Subscriber('/ground_truth/state', Odometry, gt_callback)
  rospy.Subscriber('/ready', Empty, ready_callback)
  
  # spin() simply keeps python from exiting until this node is stopped	
  rospy.spin()


