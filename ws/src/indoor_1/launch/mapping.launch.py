import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_share = get_package_share_directory('indoor_1')
    sim_launch = os.path.join(pkg_share, 'launch', 'sim.launch.py')
    slam_launch = os.path.join(
        get_package_share_directory('slam_toolbox'),
        'launch', 'online_async_launch.py')
    mapper_params = os.path.join(pkg_share, 'config', 'mapper_params.yaml')

    sim_args = {
        'use_sim_time': LaunchConfiguration('use_sim_time'),
        'use_teleop': LaunchConfiguration('use_teleop'),
        'joy_dev': LaunchConfiguration('joy_dev'),
        'map': LaunchConfiguration('map'),
        'spawn_x': LaunchConfiguration('spawn_x'),
        'spawn_y': LaunchConfiguration('spawn_y'),
        'spawn_z': LaunchConfiguration('spawn_z'),
    }

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(sim_launch),
        launch_arguments=sim_args.items()
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(slam_launch),
        launch_arguments={
            'slam_params_file': mapper_params,
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }.items()
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='True'),
        DeclareLaunchArgument('map', default_value='test_world.sdf',
                              description='World .sdf file format'),
        DeclareLaunchArgument('spawn_x', default_value='0.0', description='Spawn X'),
        DeclareLaunchArgument('spawn_y', default_value='0.0', description='Spawn Y'),
        DeclareLaunchArgument('spawn_z', default_value='0.4', description='Spawn Z'),
        DeclareLaunchArgument('use_teleop', default_value='False',
                              description='Enable joystick teleop'),
        DeclareLaunchArgument('joy_dev', default_value='0',
                              description='Joystick device index'),
        sim,
        slam,
    ])
