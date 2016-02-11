# ------
# Robot.py class
# This runs the robot.
# Copyright 2015. Pioneers in Engineering.
# ------
'''
This module contains functions for reading data from the robot, and for
manipulating the robot.

To use this module, you must first import it:

>>> from api import Robot
'''
import memcache
memcache_port = 12357
mc = memcache.Client(['127.0.0.1:%d' % memcache_port]) # connect to memcache

motor = {}

def _lookup(name): #Returns actual UID given name
    return name

def get_motor(name):
    """Returns the current power value for a motor.

    :param name: A string that identifies the motor
    :returns: A value between -100 and 100, which is the power level of that motor.

    :Examples:

    >>> motor = get_motor(motor1)

    """
    name_to_value = mc.get('motor_values')
    assert type(name) is str, "Type Mismatch: Must pass in a string"
    try:
        return name_to_value[name]
    except KeyError:
        raise KeyError("Motor name not found.")

def set_motor(name, value):

    """Sets a motor to the specified power value.

    :param name: A string that identifies the motor.
    :param value: A decimal value between -100 and 100, the power level you want to set.

    :Examples:

    >>> set_motor("motor1", 50)

    """
    assert type(name) is str, "Type Mismatch: Must pass in a string to name."
    assert type(value) is int or type(name) is float, "Type Mismatch: Must pass in an integer or float to value."
    assert value <= 100 and value >= -100, "Motor value must be a decimal between -100 and 100 inclusive."
    name_to_value = mc.get('motor_values')
    try:
        name_to_value[name] = value
        mc.set('motor_values', name_to_value)
    except KeyError:
        raise KeyError("No motor with that name")


def get_sensor(name):

    """Returns the value, or reading corresponding to the specified sensor.

    :param name: A string that identifies the sensor.
    :returns: The reading of the sensor at the current point in time.
    """
    name = _lookup(name)
    all_data = mc.get('sensor_values')
    try:
        return all_data[name]
    except KeyError:
        raise KeyError("No Sensor with that name")

def get_all_motors():
    """Returns the current power values for every connected motor.
    """
    return mc.get('motor_values')

def set_flag(name,light0,light1,light2,light3):  #TODO UID convert to int
    """Sets the brightness of every LED on the team flag.

    Each LED has four levels, represented by integers. Each light is set to 0 (off), 
    1 (low), 2 (medium), or 3 (high)

    :param name: A string that identifies the team flag. 
    :param light0: An integer (0,1,2,3) which sets brightness for LED 0
    :param light1: An integer (0,1,2,3) which sets brightness for LED 1
    :param light2: An integer (0,1,2,3) which sets brightness for LED 2
    :param light3: An integer (0,1,2,3) which sets brightness for LED 3

    :Examples:

    >>> set_flag("flag1",3,2,3,0)

    """
    correct_range = range(4)
    assert light1 in correct_range, "Error: input for light0 must be an integer between 0 and 3 inclusive"
    assert light2 in correct_range, "Error: input for light1 must be an integer between 0 and 3 inclusive"
    assert light3 in correct_range, "Error: input for light2 must be an integer between 0 and 3 inclusive"
    assert light4 in correct_range, "Error: input for light3 must be an integer between 0 and 3 inclusive"
    name = _lookup(name)
    flag_data = list(name) + list(light1) + list(light2) + list(light3) + list(light4)
    mc.set('flag_values',flag_data)

def set_LED(name,light,value): #TODO UID convert to int
    """Sets the brightness of a specific LED on the team flag.

    Each LED has four levels, represented by integers. Each light is set to 0 (off),
    1 (low), 2 (medium), or 3 (high). Each light has a specific index associated with it, 
    an integer 0, 1, 2, 3.

    :param name: A string that identifies the team flag.
    :param light: An integer (0,1,2,3) which identifies which LED top set.
    :param value: An integer (0,1,2,3) which sets brightness for the specified LED

    :Examples: 

    >>> set_LED("flag1",2,2)
    >>> set_LED("flag1",3,2)
    """
    name = _lookup(name)
    assert light in range(1,5), "Error: light number must be an Integer between 1 and 4 inclusive"
    assert value in range(4),"Error: value must be an integer between 0 and 3 inclusive"
    flag_data = list(name) + [-1,-1,-1,-1]
    flag_data[light] = value
    mc.set('flag_values',flag_data)

def set_all_servos(name,servo0,servo1,servo2,servo3): #TODO How does the servos specifically work
    """Sets a degree for each servo to turn.

    Each servo (0,1,2,3) is set to turn an interger amount of degrees (0-180)

    :param name: A string that identifies the servos.
    :param servo0: An integer between 0 and 180 which sets the amount to (turn in degrees) for servo 0
    :param servo1: An integer between 0 and 180 which sets the amount to (turn in degrees) for servo 1
    :param servo2: An integer between 0 and 180 which sets the amount to (turn in degrees) for servo 2
    :param servo3: An integer between 0 and 180 which sets the amount to (turn in degrees) for servo 3
    
    :Examples:

    >>> set_all_servos("servo1",90,40,30,20)

    """
    name = _lookup(name)
    correct_range = range(181)
    assert servo0 in correct_range, "servo0 must be between 0 and 180 inclusive"
    assert servo1 in correct_range, "servo1 must be between 0 and 180 inclusive"
    assert servo2 in correct_range, "servo2 must be between 0 and 180 inclusive"
    assert servo3 in correct_range, "servo3 must be between 0 and 180 inclusive"
    servo_data = list(name) + list(servo0) + list(servo1) + list(servo2) + list(servo3)
    mc.set('servo_values',servo_data)

def set_servo(name,servo,value):
    """Sets a degree for a specific servo to turn.

    One servo as specified by its number (0,1,2,3) is set to turn an integer amount of degrees (0-180)

    :param name: A string that identifies the servo
    :param servo: A integer (0,1,2,3) which identifies which servo to turn
    :param value: An integer between 0 and 180 which sets the amount to turn (in degrees)

    :Examples:

    >>> set_servo("servo1",3,90)
    >>> set_servo("servo1",2,150)

    """
    name = _lookup(name)
    servo_data = list(name) + [-1,-1,-1,-1]
    servo_data[servo + 1] = value
    mc.set('servo_values',servo_data)


def get_color_sensor(name,color):
    """Returns the value from the color sensor for a specific color.

    Each color sensor senses red, green, and blue, returning a 
    number between 0 and 1, where 1 indicates a higher intensity. This function returns
    the result from one specific color sensor.

    :param name: A string that identifies the color sensor
    :param color: A integer that identifies which specific color sensor to return
                  where 0 specifies the red sensor, 1 specifies the green sensor, 
                  and 2 specifies the blue sensor
    :returns: A double between 0 and 1, where 1 indicates a higher intensity

    :Examples:

    >>> color = get_color_sensor("color1",1)
    >>> color
    0.873748

    """
    all_data = mc.get('sensor_values')
    name = _lookup(name)
    try:
        return all_data[name][color]
    except KeyError:
        raise KeyError("No sensor with that name")

def get_luminosity(name):
    """Returns the luminosity for the specified color sensor.

    The color sensor returns the luminosity detected by the color sensor, represnted by
    a decimal between 0 and 1, where 1 indicates higher intensity.

    :param name: A string that identifies the color sensor
    :returns: A double between 0 and 1, where 1 indicates a higher intensity

    :Examples:

    >>> lum = get_luminosity("color1")
    >>> lum
    0.89783

    """
    all_data = mc.get('sensor_values')
    name = _lookup(name)
    try:
        return all_data[name][3]
    except KeyError:
        raise KeyError("No sensor with that name")

def get_hue(name):
    """Returns the hue detected at the specified color sensor.

    This uses the red, green, and blue sensors on the color sensor to return the 
    detected hue, which is represented as a double between 0 and 360. See 
    https://en.wikipedia.org/wiki/Hue for more information on hue.

    :param name: A string that identifies the color sensor
    :returns: A double between 0 and 360 representing the detected hue

    :Examples:

    >>> hue = get_hue("color1")
    >>> hue
    254.01

    """
    all_data = mc.get('sensor_values')
    name = _lookup(name)
    try:
        r = all_data[name][0]
        g = all_data[name][1]
        b = all_data[name][2]
        denom = max(r,g,b) - min(r,g,b)
        if r > g and r > b:
            return (g - b)/denom
        elif g > r and g > b:
            return 2.0 + (b - r)/denom
        else:
            return 4.0 + (r - g)/denom
    except KeyError:
        raise KeyError("No Sensor with that name")

def get_distance_sensor(name):
    """Returns the distance away from the sensor an object is, measured in centimeters

    :param name: A String that identifies the distance sensor
    :returns: A double representing how many centimeters away the object is from the sensor

    :Examples: 

    >>> distance = get_distance_sensor("distance1")

    """
    all_data = mc.get('sensor_values')
    name = _lookup(name)
    try:
        return all_data[name][0]
    except KeyError:
        raise KeyError("No Sensor with that name")

def get_all_switches(name):
    """Returns whether each limit switch on the identified device is pressed or not

    Each of the four limit switches on the device return either True (pressed)
    or False (not pressed). Each limit switch is specified with an intger, 
    either 0, 1, 2, 3.

    :param name: A String that identifies the limit switch smart device (contains four limit switches)
    :returns: A list of boolean values, where True is pressed and False is not pressed. 
              The value at index 0 corresponds to limit switch 0, index 1 to switch 1, and so forth.

    :Examples:

    >>> switches = get_all_switches("switch1")
    >>> switches
    [True,True,False,True]

    """
    return [False,False,False,False] #TODO Implement

def get_limit_switch(name,switch):
    """Returns whether a specified limit switch on the identified device is pressed or not

    The specified limit switch returns a boolean, either True (pressed) 
    or False (not pressed). Each limit switch is specified with an integer, either
    0, 1, 2, 3.

    :param name: A String that identifies the limit switch smart device (contains four limit switches)
    :param switch: A integer (0,1,2,3) which specifies the limit switch (out of four)
    :returns: A boolean value, where True is pressed and False is not pressed.

    :Examples:

    >>> switch = get_limit_switch("switch1",3)
    >>> switch
    True

    """
    return False #TODO Implement

def drive_distance_all(distances, motors):
    """Drives all motors in the list a set number of encoder ticks set by the distances list.
  
    The specified motors will run until it reaches the specified number of encoder ticks.
    The number of encoder ticks per degree of rotation is different for each motor, due to
    differences in gear ratios and encoders but in general, it is analogous to degrees for 
    rotation except there could be more or less than 360 encoder ticks per rotation. 
    
    :param ticks: A list of integers corresponding to the number of ticks to be moved. 
                The index of the distance should match the index of the motor names.
    :param motor: A list of strings corresponding to the motor names to be rotated. 
                The index of the motor names should match the index of the distance.

    """
    return null
  
  #TODO, need to reset positions each time these two methods are called.
def drive_distance(degrees, motor, gear_ratio): #TODO Finish documentation
    """Drives the specified motor a set number of rotations and holds the motor there. 
  
    The specified motor will run until it reaches the specified degree of rotation and will hold the motor there.
    The gear ratio should be indicated on the physical motor itself. If the user is using PID mode, 

    pololu.com. 19:1 and 67:1 motors 37D motors geared. Be able to change PID constants. Move and stay - set point. once it is called again, reset and redo function. 
    
    :param ticks: An integer corresponding to the number of ticks to be moved
    :param motor: A String corresponding to the motor name to be rotated

    """
  return null



def set_drive_mode(mode):
  """Sets the drive mode of all the motors between coasting, full braking, 
  
  
  """
def change_PID_mode(mode):
    return null;

def change PID constants(value, constant):
    return null;

def get_all_potentiometers(name):
  return null

def get_potentiometer(name, potentiometer):
  return null

#TODO: ask wth this is and if it is even included since we can't find it in hibike
def get_metal_detector(name):
  return null

class SensorValueOutOfBounds(Exception):
    pass
