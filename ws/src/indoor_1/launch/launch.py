# ROS 2 Launch file for indoor_1 package with Gazebo simulation, RViz, and ros_gz_bridge.
# Uses a YAML bridge config with explicit bridge directions.

import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('indoor_1')
    xacro_file = os.path.join(pkg_share, 'urdf', 'clown_car.urdf.xacro')
    rviz_config_file = os.path.join(pkg_share, 'config', 'indoor_1.rviz')
    world_file = os.path.join(pkg_share, 'worlds', 'test_world.sdf')
    robot_sdf_file = os.path.join(pkg_share, 'worlds', 'example_robot.sdf')
    bridge_config_file = os.path.join(pkg_share, 'config', 'bridge_config.yaml')
    teleop_config_file = os.path.join(pkg_share, 'config', 'ps4_teleop.yaml')
    gazebo_launch = os.path.join(
        get_package_share_directory('ros_gz_sim'),
        'launch',
        'gz_sim.launch.py'
    )
    teleop_launch = os.path.join(
        get_package_share_directory('teleop_twist_joy'),
        'launch',
        'teleop-launch.py'
    )

    use_sim_time = LaunchConfiguration('use_sim_time')
    use_teleop = LaunchConfiguration('use_teleop')
    joy_dev = LaunchConfiguration('joy_dev')
    spawn_x = LaunchConfiguration('spawn_x')
    spawn_y = LaunchConfiguration('spawn_y')
    spawn_z = LaunchConfiguration('spawn_z')

    robot_desc = xacro.process_file(xacro_file).toxml()
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': use_sim_time}]
    )

    # Launch Gazebo with the specified world file
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )

    spawn_robot = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-world', 'test_world',
                    '-file', robot_sdf_file,
                    '-name', 'clown_car',
                    '-x', spawn_x,
                    '-y', spawn_y,
                    '-z', spawn_z,
                ],
                output='screen'
            )
        ]
    )

    # RViz visualization
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}],
    )

    # ros_gz_bridge: bridge Gazebo and ROS topics using bridge_config.yaml
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'config_file': bridge_config_file},
        ],
        output='screen',
    )

    teleop = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(teleop_launch),
        launch_arguments={
            'joy_config': 'xbox',
            'joy_dev': joy_dev,
            'config_filepath': teleop_config_file,
            'publish_stamped_twist': 'false',
        }.items(),
        condition=IfCondition(use_teleop),
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='True', description='Use simulated clock'),
        DeclareLaunchArgument('use_teleop', default_value='False', description='Launch joystick teleop stack'),
        DeclareLaunchArgument('joy_dev', default_value='0', description='Joystick device id for teleop_twist_joy'),
        DeclareLaunchArgument('spawn_x', default_value='0.0', description='Spawn X position in world frame'),
        DeclareLaunchArgument('spawn_y', default_value='0.0', description='Spawn Y position in world frame'),
        DeclareLaunchArgument('spawn_z', default_value='0.4', description='Spawn Z position in world frame'),
        robot_state_publisher,
        gazebo,
        spawn_robot,
        rviz,
        bridge_node,
        teleop,
    ])