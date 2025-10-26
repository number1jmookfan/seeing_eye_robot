# !/usr/bin/env python
import os.path
# Copyright 2025 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time

from lerobot.robots.lekiwi import LeKiwiClient, LeKiwiClientConfig
from lerobot.utils.robot_utils import busy_wait
from lerobot.utils.visualization_utils import init_rerun, log_rerun_data
from whatdoesthedogsay import Barker

import TwitchPlays_Connections

FPS = 30

bark_file = os.path.abspath("bark.mp3")

 #Twitch Stuff
TWITCH_CHANNEL = 'mintchipss' 
MAX_QUEUE_LENGTH = 20
 #MAX and MIN arm articulations

#Possible Robot Commands
body_commands = ["forward", "backward", "left", "right", "rotate_left", "rotate_right"]
arm_commands = ["look up", "look down", "open", "close", "raise arm", "lower arm"]
# Converts the delta values to the actual m/s expected by the bot
def twitch_to_base_action(robot: LeKiwiClient, twitch_action):
    # Speed control, index options are 0, 1, 2 for slow, medium, fast, repsectively
    robot.speed_index = 1
    speed_setting = robot.speed_levels[robot.speed_index]
    xy_speed = speed_setting["xy"]  # e.g. 0.1, 0.25, or 0.4
    theta_speed = speed_setting["theta"]  # e.g. 30, 60, or 90

    x_cmd = 0.0  # m/s forward/backward
    y_cmd = 0.0  # m/s lateral
    theta_cmd = 0.0  # deg/s rotation

    match twitch_action:
        case "forward":
            x_cmd = xy_speed
        case "backward":
            x_cmd = -xy_speed
        case "left":
            theta_cmd = theta_speed
        case "right":
            theta_cmd = -theta_speed
    return {
        "x.vel": x_cmd,
        "y.vel": y_cmd,
        "theta.vel": theta_cmd,
    }

def twitch_to_arm_action(arm_action, twitch_action):
    match twitch_action:
        case "look up":
            if arm_action['arm_wrist_flex.pos'] + 5 <= 80:
                arm_action['arm_wrist_flex.pos'] += 5
        case "look down":
            if arm_action['arm_wrist_flex.pos'] - 5 >= 0:
                arm_action['arm_wrist_flex.pos'] -= 5
        case "open":
            arm_action['arm_gripper.pos'] = 45.00
        case "close":
            arm_action['arm_gripper.pos'] = 5.00
        case "raise arm":
            if arm_action['arm_shoulder_lift.pos'] + 3 <= -45:
                arm_action['arm_shoulder_lift.pos'] += 3
            if arm_action['arm_elbow_flex.pos'] - 10 >= -40:
                arm_action['arm_elbow_flex.pos'] -= 10
        case "lower arm":
            if arm_action['arm_shoulder_lift.pos'] - 3 >= -90:
                arm_action['arm_shoulder_lift.pos'] -= 3
            if arm_action['arm_elbow_flex.pos'] + 10 <= 90:
                arm_action['arm_elbow_flex.pos'] += 10
    return arm_action

def handle_message_body(robot, messages):
        try:
            histogram = {"don't move":0}
            for message in messages:
                msg = message['message'].lower()
                username = message['username'].lower()
                print("Got this message from " + username + ": " + msg)
                if msg in body_commands:
                    if msg in histogram.keys():
                        histogram[msg] += 1
                    else:
                        histogram[msg] = 1
            robot_command = "don't move"
            for command, frequency in histogram.items():
                if frequency > histogram[robot_command]:
                    robot_command = command
            return twitch_to_base_action(robot,robot_command)
        except Exception as e:
            print("Encountered exception: " + str(e))
            return twitch_to_base_action(robot, "don't move")

def handle_message_arm(arm_action, messages):
        try:
            histogram = {"don't move":0}
            for message in messages:
                msg = message['message'].lower()
                username = message['username'].lower()
                print("Got this message from " + username + ": " + msg)
                if msg in arm_commands:
                    if msg in histogram.keys():
                        histogram[msg] += 1
                    else:
                        histogram[msg] = 1
            robot_command = "don't move"
            for command, frequency in histogram.items():
                if frequency > histogram[robot_command]:
                    robot_command = command
            return twitch_to_arm_action(arm_action,robot_command)
        except Exception as e:
            print("Encountered exception: " + str(e))
            return twitch_to_arm_action(arm_action, "don't move")

def main():
    message_queue = []
    # Create the robot and teleoperator configurations
    robot_config = LeKiwiClientConfig(remote_ip="192.168.0.251", id="my_awesome_kiwi")

    # Initialize the robot and teleoperator
    robot = LeKiwiClient(robot_config)
    # Used to connect to OBS and play barks
    barker = Barker()

    #Intitialize arm action
    arm_action = {'arm_shoulder_pan.pos': 0.00,
                        'arm_shoulder_lift.pos': -90.00,
                        'arm_elbow_flex.pos': 90.00,
                        'arm_wrist_flex.pos': 0.00,
                        'arm_wrist_roll.pos': 0.00,
                        'arm_gripper.pos': 5.00}

    # Connect to the robot and teleoperator
    # To connect you already should have this script running on LeKiwi: `python -m lerobot.robots.lekiwi.lekiwi_host --robot.id=my_awesome_kiwi`
    robot.connect()
    # Connect to OBS for playing sound effect
    barker.connect()
    # Give the name of the scene you want to play the sound on, the name you want for the source, and the path to the audio file.
    barker.set_source("Robot", "DogBark", bark_file)

    # Init rerun viewer
    init_rerun(session_name="lekiwi_teleop")

    #if not robot.is_connected or not leader_arm.is_connected or not twitch.is_connected:
    if not robot.is_connected:
        raise ValueError("Robot or teleop is not connected!")
    #Connecting to Twitch
    t = TwitchPlays_Connections.Twitch()
    t.twitch_connect(TWITCH_CHANNEL)
    print("Starting teleop loop...")
    while True:
        t0 = time.perf_counter()
        #Twitch Stuff
        #active_tasks = [t for t in active_tasks if not t.done()]
        #Check for messages
        new_messages = t.twitch_receive_messages()
        if new_messages:
            message_queue += new_messages #Adds new messages to queue
            message_queue = message_queue[:MAX_QUEUE_LENGTH] #Limits queue length
        
        if not message_queue:
            time.sleep(1)
        else:
            # Get robot observation
            observation = robot.get_observation()

            #pops messages from queue
            messages_to_handle = message_queue[0:len(message_queue)]
            message_queue = []
            
            # For debug purposes, just to test that the action is sent to the bot correctly
            #twitch_action = "rotate_right"
            base_action = handle_message_body(robot, messages_to_handle) #twitch_to_base_action(robot, twitch_action)
            arm_action = handle_message_arm(arm_action, messages_to_handle)
            action = {**arm_action, **base_action} if len(base_action) > 0 else arm_action

            # Send action to robot
            _ = robot.send_action(action)

            # Visualize
            log_rerun_data(observation=observation, action=action)

            busy_wait(max(1.0 / FPS - (time.perf_counter() - t0), 0.0))

if __name__ == "__main__":
    main()