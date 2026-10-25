"""PR05 bringup: one turtlesim (global) + patrol/pose_relay/qos_listener in a namespace.

Arguments:
  namespace               namespace for the robot nodes (default robot_a)
  subscriber_reliability  reliable | best_effort for qos_listener
  record                  true -> start ros2 bag record (MCAP) of <ns>/sensor_pose
  bag_dir                 output directory of the recording
  log_level               log level of all nodes
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, GroupAction, LogInfo
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace


def generate_launch_description():
    namespace = LaunchConfiguration('namespace')
    reliability = LaunchConfiguration('subscriber_reliability')
    record = LaunchConfiguration('record')
    bag_dir = LaunchConfiguration('bag_dir')
    log_level = LaunchConfiguration('log_level')
    ros_args = ['--ros-args', '--log-level', log_level]

    args = [
        DeclareLaunchArgument('namespace', default_value='robot_a',
                              description='Namespace of the robot nodes'),
        DeclareLaunchArgument('subscriber_reliability', default_value='best_effort',
                              choices=['reliable', 'best_effort'],
                              description='Reliability of qos_listener subscription'),
        DeclareLaunchArgument('record', default_value='false',
                              choices=['true', 'false'],
                              description='Record <namespace>/sensor_pose to MCAP'),
        DeclareLaunchArgument('bag_dir', default_value='evidence/pr05/bag',
                              description='Output directory for ros2 bag record'),
        DeclareLaunchArgument('log_level', default_value='info'),
    ]

    # One global turtlesim: its topics stay /turtle1/*.
    turtlesim = Node(
        package='turtlesim', executable='turtlesim_node', name='turtlesim',
        output='screen', arguments=ros_args,
    )

    robot = GroupAction([
        PushRosNamespace(namespace),
        Node(
            package='patrol', executable='patrol_node', name='patrol',
            output='screen', arguments=ros_args,
            remappings=[('cmd_vel', '/turtle1/cmd_vel')],
        ),
        Node(
            package='course_bringup', executable='pose_relay', name='pose_relay',
            output='screen', arguments=ros_args,
            remappings=[('pose', '/turtle1/pose')],
        ),
        Node(
            package='course_bringup', executable='qos_listener', name='qos_listener',
            output='screen', arguments=ros_args,
            parameters=[{'reliability': reliability}],
        ),
    ])

    recorder = ExecuteProcess(
        cmd=['ros2', 'bag', 'record', '-s', 'mcap', '-o', bag_dir,
             '--topics', ['/', namespace, '/sensor_pose']],
        output='screen',
        condition=IfCondition(record),
    )

    return LaunchDescription(args + [
        LogInfo(msg=['namespace=/', namespace,
                     ' subscriber_reliability=', reliability,
                     ' record=', record, ' bag_dir=', bag_dir]),
        turtlesim,
        robot,
        recorder,
    ])
