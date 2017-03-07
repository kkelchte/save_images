# create dataset
Basic code that listens to topic: 
/bebop/image_raw, 
/bebop/vel_cmd, 
/bebop/odom/pose/pose/orientation

#Launch bebop autonomy
roslaunch bebop_tools bebop_nodelet_iv.launch
#Launch ps3 controller
roslaunch bebop_tools joy_teleop.launch
#Launch create dataset
To run: `rosrun create_dataset create_dataset.py`



