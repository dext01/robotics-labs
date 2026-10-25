"""PR07: Gazebo server (+ optional GUI), robot_state_publisher, ONE ros_gz bridge,
ackermann_adapter and odom_adapter. Stays alive until Ctrl+C.

  ros2 launch course_simulation simulation.launch.py \
      world:=$PWD/src/course_simulation/worlds/mcity-minimal.sdf \
      bridge_config:=$PWD/src/course_simulation/config/bridge.yaml headless:=true
"""
from launch import LaunchDescription
from launch.actions import (AppendEnvironmentVariable, DeclareLaunchArgument,
                            ExecuteProcess, GroupAction, LogInfo)
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node, PushRosNamespace
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    sim_share = FindPackageShare('course_simulation')
    desc_share = FindPackageShare('course_description')

    world = LaunchConfiguration('world')
    bridge_config = LaunchConfiguration('bridge_config')
    bridge_qos = LaunchConfiguration('bridge_qos')
    headless = LaunchConfiguration('headless')
    namespace = LaunchConfiguration('namespace')
    sim = {'use_sim_time': True}

    robot_description = ParameterValue(
        Command(['xacro ', PathJoinSubstitution([desc_share, 'urdf', 'vehicle.urdf.xacro'])]),
        value_type=str)

    args = [
        DeclareLaunchArgument(
            'world', default_value=PathJoinSubstitution([sim_share, 'worlds', 'mcity-minimal.sdf'])),
        DeclareLaunchArgument(
            'bridge_config', default_value=PathJoinSubstitution([sim_share, 'config', 'bridge.yaml'])),
        DeclareLaunchArgument(
            'bridge_qos', default_value=PathJoinSubstitution([sim_share, 'config', 'bridge_qos.yaml'])),
        DeclareLaunchArgument('headless', default_value='true', choices=['true', 'false']),
        DeclareLaunchArgument('namespace', default_value='sim',
                              description='Namespace of ROS nodes; contract topics stay absolute'),
        DeclareLaunchArgument('test_drive', default_value='false', choices=['true', 'false'],
                              description='Start drive_source publishing /drive/safe'),
        DeclareLaunchArgument('drive_speed', default_value='0.5'),
        DeclareLaunchArgument('drive_steering', default_value='0.0'),
    ]

    gazebo = [
        # Models installed with the package; the user's own export is kept.
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH',
                                  PathJoinSubstitution([sim_share, 'models'])),
        # -s: server only; --headless-rendering: OGRE2/EGL for camera and gpu_lidar
        ExecuteProcess(cmd=['gz', 'sim', '-s', '-r', '--headless-rendering', world],
                       output='screen', condition=IfCondition(headless)),
        ExecuteProcess(cmd=['gz', 'sim', '-r', world],
                       output='screen', condition=UnlessCondition(headless)),
    ]

    ros_nodes = GroupAction([
        PushRosNamespace(namespace),
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             name='robot_state_publisher', output='screen',
             parameters=[{'robot_description': robot_description}, sim],
             remappings=[('joint_states', '/vehicle/joint_states')]),
        Node(package='ros_gz_bridge', executable='parameter_bridge',
             name='ros_gz_bridge', output='screen',
             parameters=[{'config_file': bridge_config}, bridge_qos]),
        Node(package='course_simulation', executable='ackermann_adapter',
             name='ackermann_adapter', output='screen', parameters=[sim]),
        Node(package='course_simulation', executable='odom_adapter',
             name='odom_adapter', output='screen', parameters=[sim]),
        Node(package='course_simulation', executable='drive_source',
             name='drive_source', output='screen',
             parameters=[sim, {'speed': ParameterValue(LaunchConfiguration('drive_speed'), value_type=float),
                               'steering_angle': ParameterValue(LaunchConfiguration('drive_steering'), value_type=float)}],
             condition=IfCondition(LaunchConfiguration('test_drive'))),
    ])

    return LaunchDescription(args + gazebo + [
        LogInfo(msg=['world=', world, ' bridge_config=', bridge_config, ' headless=', headless]),
        ros_nodes,
    ])
