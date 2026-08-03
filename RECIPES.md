# RECIPES

Useful commands

- `ros2 run tf2_tools view_frames`, exports a `.pdf` graphical repreentation of the transform in a tree diagram

- `xacro /path/to/robot.xacro > /tmp/robot.urdf`, validates a `.xacro` file
- `check_urdf /tmp/robot.urdf`, validates a `.urdf` file
- `gz sdf -p /tmp/robot.urdf`, converts `.urdf` to `.sdf`
- `urdf_to_graphviz /tmp/robot.urdf`, generates a graphical repreentation of the joint and link connections