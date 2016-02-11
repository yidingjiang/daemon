
import subprocess, multiprocessing, time
import memcache, ansible, hibike
from grizzly import *
import usb
import os

# Useful motor mappings
name_to_grizzly, name_to_values, name_to_ids = {}, {}, {}
student_proc, console_proc = None, None
robot_status = 0 # a boolean for whether or not the robot is executing 
battery_UID = 0 #TODO, what if no battery buzzer, what if not safe battery buzzer
mc.set('flag_values',[]) #set flag color initial status
mc.set('servo_values',[])

if 'HIBIKE_SIMULATOR' in os.environ and os.environ['HIBIKE_SIMULATOR'] in ['1', 'True', 'true']:
    import hibike_simulator
    h = hibike_simulator.Hibike()
else:
    h = hibike.Hibike()
connectedDevices = h.getEnumeratedDevices()    #list of tuples, first val of tuple is UID, second is int Devicetype

init_battery()
#TODO Device Delay Value
h.subToDevices([(device, 20) for (device, device_type) in connectedDevices]) 

connect to memcache
memcache_port = 12357
mc = memcache.Client(['127.0.0.1:%d' % memcache_port])

def init_battery():
    for _, dev in connectedDevices: #TODO What if Battery buzzer not found
        if dev == 4: #TODO Battery Buzzer device number
            battery_UID = dev[0]
    if not battery_UID:
        stop_motors()
        raise Exception("No Battery Buzzer Found") #TODO Raise Errors correctly
    battery_safe = bool(h.getData(battery_UID,dataUpdate)[0]) #TODO What value does battery buzzer return

def get_all_data(connectedDevices):
    all_data = {}
    for t in connectedDevices:
        all_data[str(t[0])] = h.getData(t[0], "dataUpdate")  # i is the data for each sensor
    return all_data


def set_flags(values):
    for i in range(1,values.length):
        light = values[i]
        if light != -1:
            if light == 1:
                light = -1
            elif light == 2:
                light = -64
            elif light == 3:
                light = -128
            h.writeValue(values[0], "s" + string(i), light)

def set_servos(values):
    for i in range(0,values.length-1):
        h.writeValue(values[0],"servo" + string(i), values[i+1])
    mc.set("servo_value",[])

def test_battery():
    if battery_UID not in mc.get('sensor_values'):
        stop_motors()
        raise Exception('Battery buzzer not connected')
    if not battery_safe:
        stop_motors()
        raise Exception('Battery unsafe')
# Called on starte of student code, finds and configures all the connected motors
def initialize_motors():
    try:
        addrs = Grizzly.get_all_ids()
    except usb.USBError:
        print("WARNING: no Grizzly Bear devices found")
        addrs = []

    # Brute force to find all
    for index in range(len(addrs)):
        # default name for motors is motor0, motor1, motor2, etc
        grizzly_motor = Grizzly(addrs[index])
        grizzly_motor.set_mode(ControlMode.NO_PID, DriveMode.DRIVE_COAST)
        grizzly_motor.set_target(0)

        name_to_grizzly['motor' + str(index)] = grizzly_motor
        name_to_values['motor' + str(index)] = 0
        name_to_ids['motor' + str(index)] = addrs[index]

    mc.set('motor_values', name_to_values)

# Called on end of student code, sets all motor values to zero
def stop_motors():
    for name, grizzly in name_to_grizzly.iteritems():
        grizzly.set_target(0)
        name_to_values[name] = 0

    mc.set('motor_values', name_to_values)

# A process for sending the output of student code to the UI
def log_output(stream):
    #TODO: figure out a way to limit speed of sending messages, so
    # ansible is not overflowed by printing too fast
    for line in stream:
        ansible.send_message('UPDATE_CONSOLE', {
            'console_output': {
                'value': line
            }
        })

def msg_handling(msg):
    global robot_status, student_proc, console_proc
    msg_type, content = msg['header']['msg_type'], msg['content']
    if msg_type == 'execute' and not robot_status:
        with open('student_code.py', 'w+') as f:
            f.write(msg['content']['code'])
        student_proc = subprocess.Popen(['python', '-u', 'student_code/student_code.py'],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # turns student process stdout into a stream for sending to frontend
        lines_iter = iter(student_proc.stdout.readline, b'')
        # start process for watching for student code output
        console_proc = multiprocessing.Process(target=log_output, args=(lines_iter,))
        console_proc.start()
        initialize_motors()
        robot_status= 1
    elif msg_type == 'stop' and robot_status:
        student_proc.terminate()
        console_proc.terminate()
        stop_motors()
        robot_status = 0

peripheral_data_last_sent = 0
def send_peripheral_data(data):
    global peripheral_data_last_sent
    # TODO: This is a hack. Should put this into a separate process
    if time.time() < peripheral_data_last_sent + 1:
        return
    peripheral_data_last_sent = time.time()

    # Send sensor data
    for device_id, value in data.items():
        ansible.send_message('UPDATE_PERIPHERAL', {
            'peripheral': {
                'name': 'sensor_{}'.format(device_id),
                'peripheralType':'SENSOR_SCALAR',
                'value': value,
                'id': device_id
                }
            })

while True:
    test_battery()
    battery_safe = bool(h.getData(battery_UID,dataUpdate)[0])
    msg = ansible.recv()
    # Handle any incoming commands from the UI
    if msg:
        msg_handling(msg)

    # Send whether or not robot is executing code
    ansible.send_message('UPDATE_STATUS', {
        'status': {'value': robot_status}
    })

    # Update sensor values, and send to UI
    all_sensor_data = get_all_data(connectedDevices)
    send_peripheral_data(all_sensor_data)
    mc.set('sensor_values', all_sensor_data)

    # Send battery level
    ansible.send_message('UPDATE_BATTERY', {
        'battery': {
            'value': h.getData(battery_UID,dataUpdate)[5], # TODO: Make this not a lie
            'connected': battery_UID in mc.get('sensor_values'), #TODO Implement On UI Side 
            'safe': battery_safe
        }
    })
    
    #Set Team Flag
    flag_values = mc.get('flag_values')
    if not flag_values:
        set_flags(flag_values)

    #Set Servos
    servo_values = mc.get('servo_values')
    if not servo_values:
        set_servos(servo_values)

    # Send motor values to UI, if the robot is running
    if robot_status:
        name_to_value = mc.get('motor_values') or {}
        for name in name_to_value:
            grizzly = name_to_grizzly[name]
            try:
                grizzly.set_target(name_to_value[name])
            except:
                stop_motors()
            ansible.send_message('UPDATE_PERIPHERAL', {
                'peripheral': {
                    'name': name,
                    'peripheralType':'MOTOR_SCALAR',
                    'value': name_to_value[name],
                    'id': name_to_ids[name]
                }
            })




    time.sleep(0.02)