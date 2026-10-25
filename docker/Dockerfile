# Workspace image for PR05-PR07 (baseline: Ubuntu 26.04 + ROS 2 Lyrical + Gazebo Jetty).
#   docker build -t robots-course -f docker/Dockerfile .
#   docker run --rm -it -v "$PWD":/ws -w /ws robots-course bash
FROM osrf/ros:lyrical-desktop-full
RUN apt-get update \
 && apt-get upgrade -y --with-new-pkgs \
 && apt-get install -y --no-install-recommends \
      ros-lyrical-ackermann-msgs ros-lyrical-ros-gz \
      ros-lyrical-rosbag2-storage-mcap ros-lyrical-tf2-tools \
      liburdfdom-tools python3-pytest python3-yaml \
 && rm -rf /var/lib/apt/lists/*
ENV QT_QPA_PLATFORM=offscreen
RUN echo 'source /opt/ros/lyrical/setup.bash' >> /root/.bashrc
