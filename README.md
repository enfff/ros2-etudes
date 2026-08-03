# ROS 2 Études

**Index**

- [Quick Start](#quick-start)
- [Indoor 1: LiDAR, Wheel Odometry, and IMU](#indoor-1-lidar-wheel-odometry-and-imu)


## Quick Start

> This project has been developed using [distrobox](https://distrobox.it/) and `vscode`.

**TODO** Setup Docker environment

Tracking packages:

```
apt install ros-${ROS_DISTRO}-ros-gz
apt install ros-${ROS_DISTRO}-turtlebot3-gazebo ros-${ROS_DISTRO}-navigation2 ros-${ROS_DISTRO}-nav2-bringup
```

## Gazebo Simulation

The gazebo simulation provides an empty world and a basic robot, that will be used as a canvas for the next architectural design steps

![A basic robot moving on an empty world](media/gz-sim-basics.gif)

## Indoor 1: LiDAR, Wheel Odometry, and IMU

Classic 2D SLAM setup, using LiDAR and Odometry and an IMU.

![ClownCar in RViz](media/clown_car-rviz2.png)