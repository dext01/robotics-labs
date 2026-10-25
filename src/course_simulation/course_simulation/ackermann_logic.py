"""Pure Ackermann -> Twist conversion (no ROS imports, unit-tested).

Contract (PR07):
  v = clamp(speed, 0.0, 1.2)            -> linear.x  [m/s]
  d = clamp(angle, -0.45, 0.45)         -> angular.z = v * tan(d) / L  [rad/s]
  NaN/inf in any field or stamp age > 0.25 s -> zero Twist + reason.
"""
import math
from typing import NamedTuple, Optional

WHEELBASE = 0.8
MAX_SPEED = 1.2
MIN_SPEED = 0.0
MAX_STEER = 0.45
MAX_AGE = 0.25


class Command(NamedTuple):
    linear_x: float
    angular_z: float
    reason: Optional[str]  # None = valid command, otherwise why it was zeroed


ZERO = (0.0, 0.0)


def clamp(value, low, high):
    return max(low, min(high, value))


def convert(speed, steering_angle, age, *, wheelbase=WHEELBASE, max_age=MAX_AGE):
    """Convert one AckermannDrive command; ``age`` = now - header.stamp in seconds."""
    for name, value in (('speed', speed), ('steering_angle', steering_angle), ('age', age)):
        if not math.isfinite(value):
            return Command(*ZERO, f'non-finite {name}={value}')
    if age > max_age:
        return Command(*ZERO, f'stale command: age={age:.3f} s > {max_age} s')
    v = clamp(speed, MIN_SPEED, MAX_SPEED)
    delta = clamp(steering_angle, -MAX_STEER, MAX_STEER)
    omega = v * math.tan(delta) / wheelbase
    return Command(v, omega, None)
