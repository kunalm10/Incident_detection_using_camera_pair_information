# INCIDENT DETECTION LEVERAGING CAMERA PAIR INFORMATION

## DESCRIPTION
	
The objective of this program is to identify an incident on a highway automatically. One solution to this problem is that we can compare the information of 2 cameras and then judge if there is an incident or potential Jam on that highway. In this program, with the help of vehicle detection and tracking results, we will compare the flow rates of the vehicles and deduce the highway's incident status. The accurate average flow rate and average speed of the cars can significantly contribute to precise incident detection. 

## DEPENDENCY ON OTHER MODULES
This program reads all the data from the Database, so one requirement is that the infomration generated from those modules should be accurate otherwise this incident detection module will generate false results. 
The programs are interconnected to each other so if the first program in the heirarchy isn't worrking fine this program won't work as it is supposed to.

This program imports databse.py module which again imports pymysql library.


## INSTALLATION
To make sure the program works perfectly fine, make sure there is a database connection is properly estabilished on the PC.
The database.py script and incident_detection_two_cameras.py should be present in the same directory.

## METHOD

Input: We need to pass the camera list to generate_status(cam_list) funtion for which we need to check the 	incident status. 
Also, there is a funtion named 'get_all_cameras()' in the incident_detection_two_cameras module to create a list of all the cameras present in the INDOT camera list stored in database. if user wants to use this 	function instead of giving list by themselve,that can be done too.

Other intermediate inputs like neighbor cameras, current directions, right side flow rate, left side flow rate are internally taken by the algorithm from the database.

Outout: The program will generate Jam Status as 'Normal', 'Moderate', 'High', and 'Unknown' along with the timestamp at which result is generated. The status will be uploaded in databse in Jam_status_current table 	and Jam_status_history table.
	

### TO make understand dhiraj
hi dhiraj
