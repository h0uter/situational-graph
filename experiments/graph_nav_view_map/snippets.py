response = self._robot_command(
    RobotCommandBuilder.synchro_se2_trajectory_point_command(
        goal_x=goal_x,
        goal_y=goal_y,
        goal_heading=goal_heading,
        frame_name=frame_name,
        params=self._mobility_params,
    ),
    end_time_secs=end_time,
)
