import math

import pytest
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry

from course_simulation.odom_logic import normalize, to_transform


def _odom():
    m = Odometry()
    m.header.frame_id = 'course_ackermann/odom'
    m.child_frame_id = 'course_ackermann/base_link'
    m.header.stamp.sec = 42
    m.header.stamp.nanosec = 123456789
    m.pose.pose.position.x = 1.5
    m.pose.pose.position.y = -0.25
    m.pose.pose.orientation.z = math.sin(0.1)
    m.pose.pose.orientation.w = math.cos(0.1)
    m.twist.twist.linear.x = 0.7
    m.twist.twist.angular.z = 0.3
    m.pose.covariance = [float(i) for i in range(36)]
    m.twist.covariance = [float(i) / 10 for i in range(36)]
    return m


def test_frames_renamed_and_data_preserved():
    src = _odom()
    out, reason = normalize(src)
    assert reason is None
    assert out.header.frame_id == 'odom'
    assert out.child_frame_id == 'base_link'
    assert out.header.stamp == src.header.stamp
    assert out.pose == src.pose
    assert out.twist == src.twist
    assert list(out.pose.covariance) == list(src.pose.covariance)
    assert list(out.twist.covariance) == list(src.twist.covariance)


def test_source_message_not_modified():
    src = _odom()
    normalize(src)
    assert src.header.frame_id == 'course_ackermann/odom'


def test_transform_keeps_stamp():
    out, _ = normalize(_odom())
    t = to_transform(out, TransformStamped)
    assert t.header.stamp.sec == 42 and t.header.stamp.nanosec == 123456789
    assert (t.header.frame_id, t.child_frame_id) == ('odom', 'base_link')
    assert t.transform.translation.x == pytest.approx(1.5)
    assert t.transform.rotation == out.pose.pose.orientation


@pytest.mark.parametrize('frame, child', [
    ('odom', 'course_ackermann/base_link'),
    ('course_ackermann/odom', 'base_footprint'),
    ('', ''),
])
def test_unexpected_frames_rejected(frame, child):
    m = _odom()
    m.header.frame_id, m.child_frame_id = frame, child
    out, reason = normalize(m)
    assert out is None and 'unexpected frames' in reason


def test_non_finite_rejected():
    m = _odom()
    m.pose.pose.position.x = math.nan
    out, reason = normalize(m)
    assert out is None and 'non-finite' in reason
