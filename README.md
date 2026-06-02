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

## Indoor 1: LiDAR, Wheel Odometry, and IMU

Classic 2D SLAM setup, using LiDAR and Odometry and an IMU.