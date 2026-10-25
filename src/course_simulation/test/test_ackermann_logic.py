import math

import pytest

from course_simulation.ackermann_logic import convert


def test_straight():
    cmd = convert(0.8, 0.0, 0.01)
    assert cmd.reason is None
    assert cmd.linear_x == pytest.approx(0.8)
    assert cmd.angular_z == pytest.approx(0.0)


def test_turn_left():
    cmd = convert(1.0, 0.3, 0.0)
    assert cmd.reason is None
    assert cmd.angular_z == pytest.approx(1.0 * math.tan(0.3) / 0.8)
    assert cmd.angular_z > 0


def test_turn_right():
    assert convert(1.0, -0.3, 0.0).angular_z < 0


def test_zero_speed_gives_no_rotation():
    cmd = convert(0.0, 0.45, 0.0)
    assert (cmd.linear_x, cmd.angular_z) == (0.0, 0.0)
    assert cmd.reason is None


def test_clamp_speed_and_steering():
    cmd = convert(5.0, 1.0, 0.0)
    assert cmd.linear_x == pytest.approx(1.2)
    assert cmd.angular_z == pytest.approx(1.2 * math.tan(0.45) / 0.8)


def test_negative_speed_clamped_to_zero():
    cmd = convert(-1.0, 0.2, 0.0)
    assert (cmd.linear_x, cmd.angular_z) == (0.0, 0.0)


def test_stale_command():
    cmd = convert(1.0, 0.1, 0.26)
    assert (cmd.linear_x, cmd.angular_z) == (0.0, 0.0)
    assert 'stale' in cmd.reason


def test_age_at_limit_is_accepted():
    assert convert(1.0, 0.0, 0.25).reason is None


@pytest.mark.parametrize('speed, angle', [
    (math.nan, 0.0), (0.5, math.nan), (math.inf, 0.0), (0.5, -math.inf),
])
def test_non_finite_command(speed, angle):
    cmd = convert(speed, angle, 0.0)
    assert (cmd.linear_x, cmd.angular_z) == (0.0, 0.0)
    assert 'non-finite' in cmd.reason
