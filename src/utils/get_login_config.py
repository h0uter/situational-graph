import json
from dataclasses import dataclass
import os


@dataclass
class LoginConfig:
    wifi_hostname: str
    lan_hostname: str
    username: str
    password: str

def get_login_config() -> LoginConfig:
    '''
    It takes a robot name and a share directory, and returns a LoginConfig object
    
    :param robot_name: The name of the robot ("sean" or "snowboy")
    :type robot_name: str
    :param share_directory: The directory where the robot's shared files are located
    :type share_directory: str
    :return: A LoginConfig object.
    '''
    path = os.path.join('knowledge_roadmap', 'data_providers')
    with open(f'{path}/login.json', 'r') as file:
        return LoginConfig(**json.load(file))
