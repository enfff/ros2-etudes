import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('indoor_1')
    urdf_file = os.path.join(pkg_share, 'urdf', 'clown_car.urdf')
    rviz_config_file = os.path.join(pkg_share, 'config', 'indoor_1.rviz')
    world_file = os.path.join(pkg_share, 'worlds', 'test_world.sdf')
    nav2_params_file = os.path.join(
        get_package_share_directory('nav2_bringup'),
        'params',
        'nav2_params.yaml',
    )
    lidar_scan_topic = '/world/test_world/model/clown_car/link/base_footprint/sensor/gpu_lidar/scan'
    lidar_points_topic = '/world/test_world/model/clown_car/link/base_footprint/sensor/gpu_lidar/scan/points'
    odom_topic = '/model/clown_car/odometry'
    gazebo_launch = os.path.join(
        get_package_share_directory('ros_gz_sim'),
        'launch',
        'gz_sim.launch.py'
    )

    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()
        
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}]
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )

    slam = LaunchConfiguration('slam')
    map_yaml = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')

    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('nav2_bringup'),
                'launch',
                'bringup_launch.py',
            )
        ),
        launch_arguments={
            'slam': slam,
            'map': map_yaml,
            'use_sim_time': use_sim_time,
            'params_file': params_file,
        }.items(),
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-file', urdf_file, '-name', 'clown_car'],
        output='screen'
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file]
    )

    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            f'{lidar_scan_topic}@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            f'{lidar_points_topic}@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            f'{odom_topic}@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/cmd_vel@geometry_msgs/msg/Twist[gz.msgs.Twist',
        ],
        remappings=[
            (lidar_scan_topic, '/scan'),
            (lidar_points_topic, '/points'),
            (odom_topic, '/odom'),
        ],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('slam', default_value='True', description='Run slam_toolbox instead of localization'),
        DeclareLaunchArgument('map', default_value='', description='Path to map YAML for AMCL localization'),
        DeclareLaunchArgument('use_sim_time', default_value='True', description='Use simulated clock'),
        DeclareLaunchArgument('params_file', default_value=nav2_params_file, description='Nav2 params file'),
        robot_state_publisher,
        gazebo,
        spawn_robot,
        rviz,
        bridge_node,
        nav2_bringup,
    ])