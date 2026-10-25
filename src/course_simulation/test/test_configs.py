"""Static checks of bridge.yaml, model.sdf and the world (no Gazebo needed)."""
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import yaml

PKG = Path(__file__).resolve().parents[1]
BRIDGE = PKG / 'config' / 'bridge.yaml'
MODEL = PKG / 'models' / 'course_ackermann' / 'model.sdf'
WORLD = PKG / 'worlds' / 'mcity-minimal.sdf'


@pytest.fixture(scope='module')
def bridge():
    return {e['ros_topic_name']: e for e in yaml.safe_load(BRIDGE.read_text())}


def test_bridge_topics_unique():
    entries = yaml.safe_load(BRIDGE.read_text())
    ros = [e['ros_topic_name'] for e in entries]
    gz = [e['gz_topic_name'] for e in entries]
    assert len(ros) == len(set(ros)) and len(gz) == len(set(gz))


def test_command_goes_ros_to_gz(bridge):
    e = bridge['/vehicle/gz_cmd_vel']
    assert e['direction'] == 'ROS_TO_GZ'
    assert e['gz_topic_name'] == '/model/course_ackermann/cmd_vel'
    assert e['ros_type_name'] == 'geometry_msgs/msg/Twist'


def test_raw_drive_is_not_bridged(bridge):
    assert '/drive/raw' not in bridge and '/drive/safe' not in bridge


@pytest.mark.parametrize('topic', [
    '/clock', '/vehicle/odom_gz', '/vehicle/camera/image_raw', '/vehicle/scan', '/vehicle/imu',
])
def test_sensors_go_gz_to_ros(bridge, topic):
    assert bridge[topic]['direction'] == 'GZ_TO_ROS'


def test_raw_odometry_renamed(bridge):
    assert '/vehicle/odom' not in bridge  # published only by odom_adapter


def _sensors():
    root = ET.parse(MODEL).getroot()
    return {s.get('name'): s for s in root.iter('sensor')}


@pytest.mark.parametrize('name, frame, rate', [
    ('camera', 'camera_link', 15.0),   # changed from 20 Hz
    ('lidar', 'lidar_link', 10.0),
    ('imu', 'imu_link', 100.0),
])
def test_sensor_frames_and_rates(name, frame, rate):
    s = _sensors()[name]
    assert s.find('gz_frame_id').text == frame
    assert float(s.find('update_rate').text) == rate


def test_sensor_topics_match_bridge(bridge):
    gz_topics = {e['gz_topic_name'] for e in bridge.values()}
    for s in _sensors().values():
        assert s.find('topic').text in gz_topics


def test_controller_matches_contract():
    root = ET.parse(MODEL).getroot()
    plugin = next(p for p in root.iter('plugin') if 'AckermannSteering' in p.get('name'))
    assert float(plugin.find('wheel_base').text) == pytest.approx(0.8)
    assert float(plugin.find('steering_limit').text) == pytest.approx(0.45)
    assert plugin.find('frame_id').text == 'course_ackermann/odom'
    assert plugin.find('child_frame_id').text == 'course_ackermann/base_link'
    assert plugin.find('topic').text == '/model/course_ackermann/cmd_vel'


def test_world_includes_robot_once():
    root = ET.parse(WORLD).getroot()
    world = root.find('world')
    assert world.get('name') == 'mcity_minimal'
    uris = [i.find('uri').text for i in world.iter('include')]
    assert uris == ['model://course_ackermann']


def test_sdf_matches_urdf_geometry():
    """Shared geometry of URDF (PR06) and SDF must agree."""
    xacro = pytest.importorskip('xacro')
    urdf = PKG.parent / 'course_description' / 'urdf' / 'vehicle.urdf.xacro'
    robot = ET.fromstring(xacro.process_file(str(urdf)).toxml())
    urdf_xyz = {j.find('child').get('link'): j.find('origin').get('xyz')
                for j in robot.findall('joint')}
    sdf = ET.parse(MODEL).getroot()
    for link in sdf.iter('link'):
        pose = link.find('pose')
        if pose is not None and pose.get('relative_to') == 'base_link':
            name = link.get('name')
            sdf_xyz = [float(v) for v in pose.text.split()[:3]]
            assert sdf_xyz == pytest.approx([float(v) for v in urdf_xyz[name].split()]), name
