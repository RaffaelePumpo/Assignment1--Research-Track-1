
from __future__ import print_function

import time
from sr.robot import *


a_th = 2.0
""" float: Threshold for the control of the orientation"""

d_th = 0.4
""" float: Threshold for the control of the linear distance"""


R = Robot()
""" instance of the class Robot"""


offset_silver_list=[]
"""list: it will contain the Silven token's offset already moved """


offset_golden_list=[]
"""list: it will contain the Golden token's offset already having a Silver token near """


def drive(speed, seconds):
    """
    Function for setting a linear velocity
    
    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0


def turn(speed, seconds):
    """
    Function for setting an angular velocity
    
    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0


def check_offset(offset,offset_list):               #check if the offset is in the list in this case return False
    """
    Function for checking the offset of a token, it doesn't allow the robot to take twice a token
    or to release near a token that already has one close  
    """
    for i in offset_list:
        if i==offset:
            return False
    return True


def find_silver_token():
    """
    Function to find the closest token silver still not taken

    Returns:
	dist (float): distance of the closest token (-1 if no token is detected or if token detected already moved)
	rot_y (float): angle between the robot and the token (-1 if no token is detected or if token detected already moved)
    offset(float): numeric code from the lower numbered token of its type (-1 if no token is detected or if token detected already moved)
    """
    dist = 100
    for token in R.see():
        if not check_offset(token.info.offset,offset_silver_list):              #check if the token can be taken
            print("I can't grab that silver token,I have just moved it")
        elif check_offset(token.info.offset,offset_silver_list)and token.info.marker_type is MARKER_TOKEN_SILVER and token.dist < dist:
                dist = token.dist
                rot_y = token.rot_y
                offset=token.info.offset
    if dist == 100:
        return -1, -1,-1
    else:
        return dist, rot_y,offset


def find_golden_token():
    """
    Function to find the closest token silver that has not a silver token close

    Returns:
	dist (float): distance of the closest token (-1 if no token is detected or if token detected has a silver token close)
	rot_y (float): angle between the robot and the token (-1 if no token is detected or if token detected has a silver token close)
    offset(float): numeric code from the lower numbered token of its type (-1 if no token is detected or if token detected has a silver token close)
    """
    dist = 100
    for token in R.see():
        if not check_offset(token.info.offset,offset_golden_list):                      #check if near that token can be released another one
            print("I can't release close that golden token,It has already one")
        elif check_offset(token.info.offset,offset_golden_list)and token.info.marker_type is MARKER_TOKEN_GOLD and token.dist < dist:
                dist = token.dist
                rot_y = token.rot_y
                offset=token.info.offset
    if dist == 100:
        return -1, -1,-1
    else:
        return dist, rot_y,offset


def take_token():
    """
    Function to take the silver token chosen
    """
    while 1:
        dist, rot_y,offset= find_silver_token()
        if offset==-1:                        
            print("I don't see any silver token to grab!!")
            turn(+10, 1)
        if dist < d_th :
            print("Found it!")
            if R.grab():
                offset_silver_list.append(offset)               #add the token just taken to the silver list
                print("Gotcha!")
        elif -a_th <= rot_y <= a_th :
            print("Ah, that'll do.")
            drive(70,0.5)
        elif rot_y < -a_th:
            print("Left a bit...")
            turn(-2, 0.5)
        elif rot_y > a_th:
            print("Right a bit...")
            turn(+2, 0.5)


def release_token():
    """
    Function to release silver token previously taken near the golden token chosen
    """
    turn(10,3)
    while 1:
        dist, rot_y,offset= find_golden_token()
        if offset==-1:
            print("I don't see any golden token!!")
            turn(+2, 2)
        elif dist < 1.7*d_th :
            print("I am releasing silver token!!")
            R.release()
            offset_golden_list.append(offset)                   #add the gold token to the golden list
            drive(-40,1)
            turn(10, 1)
            return True
        elif -a_th <= rot_y <= a_th and offset!=-1:
            print("Ah, that'll do.")
            drive(70, 0.5)
        elif rot_y < -a_th:
            print("Left a bit...")
            turn(-2, 0.5)
        elif rot_y > a_th:
            print("Right a bit...")
            turn(+2, 0.5)

def main():
    while 1 :
        take_token()
        release_token()


main()

