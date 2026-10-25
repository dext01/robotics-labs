"""Patrol: drive along a square by alternating 'forward' and 'turn' phases.

The node publishes to the *relative* topic ``cmd_vel``; the launch file
remaps it to ``/turtle1/cmd_vel``.
"""
import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


def phase_command(t, side_duration, turn_duration, linear_speed, angular_speed):
    """Return (linear, angular) for time ``t`` since the start of patrol."""
    period = side_duration + turn_duration
    phase = math.fmod(t, period)
    if phase < side_duration:
        return linear_speed, 0.0
    return 0.0, angular_speed


class Patrol(Node):

    def __init__(self):
        super().__init__('patrol')
        self.declare_parameter('linear_speed', 1.0)
        self.declare_parameter('angular_speed', math.pi / 2)
        self.declare_parameter('side_duration', 2.0)
        self.declare_parameter('turn_duration', 1.0)
        self.declare_parameter('rate', 10.0)

        self._pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self._start = self.get_clock().now()
        rate = float(self.get_parameter('rate').value)
        self.create_timer(1.0 / rate, self._tick)
        self.get_logger().info(
            f'patrol started, publishing to {self._pub.topic_name}')

    def _tick(self):
        t = (self.get_clock().now() - self._start).nanoseconds * 1e-9
        linear, angular = phase_command(
            t,
            float(self.get_parameter('side_duration').value),
            float(self.get_parameter('turn_duration').value),
            float(self.get_parameter('linear_speed').value),
            float(self.get_parameter('angular_speed').value),
        )
        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular
        self._pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = Patrol()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
