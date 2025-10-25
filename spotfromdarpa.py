# !/usr/bin/env python

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
#from teleop_twitch import TwitchTeleop, TwitchTeleopConfig
from lerobot.teleoperators.so100_leader import SO100Leader, SO100LeaderConfig
from lerobot.utils.robot_utils import busy_wait
from lerobot.utils.visualization_utils import init_rerun, log_rerun_data

FPS = 30

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
        case "foward":
            x_cmd = xy_speed
        case "backward":
            x_cmd = -xy_speed
        case "left":
            y_cmd = xy_speed
        case "right":
            y_cmd = -xy_speed
        case "rotate_left":
            theta_cmd = theta_speed
        case "rotate_right":
            theta_cmd = -theta_speed
            
    return {
        "x.vel": x_cmd,
        "y.vel": y_cmd,
        "theta.vel": theta_cmd,
    }

def main():
    # Create the robot and teleoperator configurations
    robot_config = LeKiwiClientConfig(remote_ip="172.18.134.136", id="my_lekiwi")
    teleop_arm_config = SO100LeaderConfig(port="/dev/tty.usbmodem585A0077581", id="my_awesome_leader_arm")
    #twitch_config = TwitchTeleopConfig(id="twitch_chat")

    # Initialize the robot and teleoperator
    robot = LeKiwiClient(robot_config)
    leader_arm = SO100Leader(teleop_arm_config)
    #twitch = TwitchTeleop(twitch_config)


    # Connect to the robot and teleoperator
    # To connect you already should have this script running on LeKiwi: `python -m lerobot.robots.lekiwi.lekiwi_host --robot.id=my_awesome_kiwi`
    robot.connect()
    leader_arm.connect()
    # twitch.connect()
    # Below is for debug until twitch connection is actually programmed

    twitch = object
    twitch.is_connected = True

    # Init rerun viewer
    init_rerun(session_name="lekiwi_teleop")

    #if not robot.is_connected or not leader_arm.is_connected or not twitch.is_connected:
    if not robot.is_connected or not leader_arm.is_connected or not twitch.is_connected:
        raise ValueError("Robot or teleop is not connected!")

    print("Starting teleop loop...")
    while True:
        t0 = time.perf_counter()

        # Get robot observation
        observation = robot.get_observation()

        # Get teleop action
        # Arm
        arm_action = leader_arm.get_action()
        arm_action = {f"arm_{k}": v for k, v in arm_action.items()}
        # twitch_action = twitch.get_action()
        twitch_action = "rotate_right" # For debug purposes, just to test that the action is sent to the bot correctly
        base_action = twitch_to_base_action(robot, twitch_action)
        #base_action = robot._from_keyboard_to_base_action(keyboard_keys)

        action = {**arm_action, **base_action} if len(base_action) > 0 else arm_action

        # Send action to robot
        _ = robot.send_action(action)

        # Visualize
        log_rerun_data(observation=observation, action=action)

        busy_wait(max(1.0 / FPS - (time.perf_counter() - t0), 0.0))

if __name__ == "__main__":
    main()