"""robot_state_publisher for vehicle.urdf.xacro, optionally with RViz.

  ros2 launch course_description display.launch.py rviz:=true
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    share = FindPackageShare('course_description')
    model = LaunchConfiguration('model')
    use_sim_time = LaunchConfiguration('use_sim_time')

    robot_description = ParameterValue(Command(['xacro ', model]), value_type=str)

    return LaunchDescription([
        DeclareLaunchArgument(
            'model', default_value=PathJoinSubstitution([share, 'urdf', 'vehicle.urdf.xacro'])),
        DeclareLaunchArgument('rviz', default_value='false', choices=['true', 'false']),
        DeclareLaunchArgument('use_sim_time', default_value='false', choices=['true', 'false']),
        Node(
            package='robot_state_publisher', executable='robot_state_publisher',
            name='robot_state_publisher', output='screen',
            parameters=[{'robot_description': robot_description,
                         'use_sim_time': use_sim_time}],
        ),
        Node(
            package='rviz2', executable='rviz2', name='rviz2', output='screen',
            arguments=['-d', PathJoinSubstitution([share, 'rviz', 'vehicle.rviz'])],
            condition=IfCondition(LaunchConfiguration('rviz')),
        ),
    ])
