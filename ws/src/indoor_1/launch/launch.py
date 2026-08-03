# ROS 2 Launch file for indoor_1 package with Gazebo simulation, Nav2, and ros_gz_bridge
# Key configurations:
#   - lidar_scan_topic set to /lidar (matching <topic>lidar</topic> in URDF sensor)
#   - lidar_points_topic set to /lidar/points
#   - joint_state topic remapped to /joint_states
#   - spawn_robot delayed by 5s to avoid race condition with Gazebo loading

import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('indoor_1')
    xacro_file = os.path.join(pkg_share, 'urdf', 'clown_car.urdf.xacro')
    rviz_config_file = os.path.join(pkg_share, 'config', 'indoor_1.rviz')
    world_file = os.path.join(pkg_share, 'worlds', 'test_world.sdf')
    robot_sdf_file = os.path.join(pkg_share, 'worlds', 'example_robot.sdf')
    gazebo_launch = os.path.join(
        get_package_share_directory('ros_gz_sim'),
        'launch',
        'gz_sim.launch.py'
    )

    nav2_params_file = os.path.join(
        get_package_share_directory('nav2_bringup'),
        'params',
        'nav2_params.yaml',
    )

    robot_desc = xacro.process_file(xacro_file).toxml()
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    # Launch Gazebo with the specified world file
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )

    # Launch configuration variables
    map_yaml = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')

    # Nav2 bringup
    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('nav2_bringup'),
                'launch',
                'bringup_launch.py',
            )
        ),
        launch_arguments={
            'map': map_yaml,
            'use_sim_time': use_sim_time,
            'params_file': params_file,
        }.items(),
    )

    spawn_robot = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=['-world', 'test_world', '-file', robot_sdf_file, '-name', 'clown_car'],
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
        parameters=[{'use_sim_time': True}],
    )

    # ros_gz_bridge: bridge Gazebo topics to ROS 2 topics with remappings
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'use_sim_time': True}],
        arguments=[
            '/lidar@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/lidar/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            '/model/clown_car/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/cmd_vel@geometry_msgs/msg/Twist[gz.msgs.Twist',
            '/world/test_world/model/clown_car/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        remappings=[
            ('/lidar', '/scan'),
            ('/lidar/points', '/points'),
            ('/model/clown_car/odometry', '/odom'),
            ('/world/test_world/model/clown_car/joint_state', '/joint_states'),
        ],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument('slam', default_value='True', description='Run slam_toolbox instead of localization'),
        DeclareLaunchArgument('map', default_value='', description='Path to map YAML for AMCL localization'),
        DeclareLaunchArgument('use_sim_time', default_value='True', description='Use simulated clock'),
        DeclareLaunchArgument('params_file', default_value=nav2_params_file, description='Nav2 params file'),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0', '0', '0', '0', '0', 'odom', 'base_footprint'],
            output='screen',
            parameters=[{'use_sim_time': True}],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0', '0', '0', '0', '0', 'lidar_link', 'clown_car/lidar_link/gpu_lidar'],
            output='screen',
            parameters=[{'use_sim_time': True}],
        ),
        robot_state_publisher,
        gazebo,
        spawn_robot,
        rviz,
        bridge_node,
    ])