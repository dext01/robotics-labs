import pytest
from rclpy.qos import HistoryPolicy, ReliabilityPolicy

from course_bringup.pose_relay import SENSOR_QOS
from course_bringup.qos_listener import make_qos


def test_sensor_publisher_is_best_effort():
    assert SENSOR_QOS.reliability == ReliabilityPolicy.BEST_EFFORT
    assert SENSOR_QOS.history == HistoryPolicy.KEEP_LAST
    assert SENSOR_QOS.depth == 10


@pytest.mark.parametrize('name, policy', [
    ('reliable', ReliabilityPolicy.RELIABLE),
    ('best_effort', ReliabilityPolicy.BEST_EFFORT),
    (' BEST_EFFORT ', ReliabilityPolicy.BEST_EFFORT),
])
def test_make_qos(name, policy):
    assert make_qos(name).reliability == policy


def test_make_qos_rejects_unknown():
    with pytest.raises(ValueError):
        make_qos('sometimes')
