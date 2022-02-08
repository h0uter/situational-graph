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


    def _connect_to_spot(self):
        """Create a connection with Spot (blocking function)"""
        creating_sdk = True
        while creating_sdk:
            try:
                self._sdk = create_standard_sdk('ros_spot')
                creating_sdk = False
            except Exception as e:
                self._logger.error(f'Error creating SDK object: {e}')
                time.sleep(2.0)

        self._robot = self._sdk.create_robot(self._hostname)

        authenticating = True
        while authenticating:
            try:
                self._robot.authenticate(self._username, self._password)
                self._robot.start_time_sync()
                authenticating = False
            except RpcError as err:
                self._logger.warning(
                    f'Failed to communicate with robot: {err}')
                time.sleep(2.0)

        self._valid = True
