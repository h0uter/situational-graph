from time import time

# import all the boston shite
from bosdyn.client.frame_helpers import (
    BODY_FRAME_NAME,
    VISION_FRAME_NAME,
    ODOM_FRAME_NAME,
)
from bosdyn.client.robot_command import RobotCommandClient, RobotCommandBuilder

from knowledge_roadmap.data_providers.spot_wrapper import SpotWrapper
from knowledge_roadmap.entities.abstract_agent import AbstractAgent
from knowledge_roadmap.utils.get_login_config import get_login_config


import logging

class SpotRobot(AbstractAgent):

    def __init__(self, parameter_overrides=None, offline=False):
        """
        Main function for the SpotROS class.
        Gets config from ROS and initializes the wrapper.
        Holds lease from wrapper and updates all async tasks at the ROS rate
        """

        self._logger = logging.getLogger(__name__)
        # self._logger = logging
        logging.basicConfig(level=logging.INFO)



        rates = {
            'graph_nav': 5,
            'local_grid': 2,
            'robot_state': 5,
            'metrics': 1,
            'lease': 1,
            'front_image': 1,
            'side_image': 1,
            'rear_image': 1,
        }  # [Hz]

        self.auto_claim = True
        self.auto_power_on = True
        self.auto_stand = True
        self.timer_period = 0.1  # [second]

        print("what up")
        
        cfg = get_login_config()
        self.spot_wrapper = SpotWrapper(
            username=cfg.username,
            password=cfg.password,
            hostname=cfg.wifi_hostname,
            logger=self._logger,
            rates=rates,
            # callbacks=self.callbacks,
            # offline=offline,
        )
        print("eyo")

        if self.spot_wrapper.is_valid:
            self._logger.info("Spot wrapper is valid")
            print("yoyoyoyoy")

            # self._apply_mobility_parameters()

            if self.auto_claim:
                claim_status = self.spot_wrapper.claim()
                self._logger.info(f'claim_status: {claim_status}')
                if self.auto_power_on:
                    power_on_status = self.spot_wrapper.power_on()
                    self._logger.info(f'power_on_status: {power_on_status}')
                    if self.auto_stand:
                        stand_status = self.spot_wrapper.stand()
                        self._logger.info(f'stand_status: {stand_status}')

            # self.timer = self.create_timer(
            #     timer_period_sec=self.timer_period,
            #     callback=self._timer_callback)
        else:
            self._logger.warning("Spot wrapper is not valid!")



    # def __init__(self, debug=False, start_pos=None):
    #     # super().__init__(debug=debug, start_pos=start_pos)

    def move_to_pos(self, pos:tuple):
        pass

    def get_localization(self) -> tuple:
        pass






if __name__ == "__main__":
    spot = SpotRobot()

#     spot.connect

#     # connect to robot


#     # get localization



#     # set movement command
#     cmd_duration = 5
#     end_time = time.time() + cmd_duration

#     response = self._robot_command(
#     RobotCommandBuilder.synchro_se2_trajectory_point_command(
#         goal_x=goal_x,
#         goal_y=goal_y,
#         goal_heading=goal_heading,
#         frame_name=ODOM_FRAME_NAME,
#         params=self._mobility_params,
#     ),
#     end_time_secs=end_time,
# )
