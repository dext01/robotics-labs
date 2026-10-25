"""ackermann_adapter: /drive/safe (AckermannDriveStamped) -> /vehicle/gz_cmd_vel (Twist).

Uses sim time (use_sim_time:=true). An invalid or stale command produces one
zero Twist and a diagnostic reason; the last valid command is never repeated.
A watchdog also sends zero once if no fresh command arrives for 0.25 s, because
Gazebo AckermannSteering keeps the last velocity forever.
"""
import rclpy
from ackermann_msgs.msg import AckermannDriveStamped
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.time import Time
from std_msgs.msg import String

from course_simulation.ackermann_logic import MAX_AGE, convert


class AckermannAdapter(Node):

    def __init__(self):
        super().__init__('ackermann_adapter')
        self.declare_parameter('wheelbase', 0.8)
        self.declare_parameter('max_age', MAX_AGE)
        self._pub = self.create_publisher(Twist, '/vehicle/gz_cmd_vel', 10)
        self._diag = self.create_publisher(String, '/vehicle/ackermann_adapter/reason', 10)
        self.create_subscription(AckermannDriveStamped, '/drive/safe', self._on_cmd, 10)
        self._last_valid = None
        self._moving = False
        self.create_timer(0.05, self._watchdog)

    def _max_age(self):
        return float(self.get_parameter('max_age').value)

    def _on_cmd(self, msg):
        now = self.get_clock().now()
        age = (now - Time.from_msg(msg.header.stamp)).nanoseconds * 1e-9
        cmd = convert(msg.drive.speed, msg.drive.steering_angle, age,
                      wheelbase=float(self.get_parameter('wheelbase').value),
                      max_age=self._max_age())
        if cmd.reason is None:
            self._last_valid = now
        self._send(cmd.linear_x, cmd.angular_z, cmd.reason)

    def _watchdog(self):
        if not self._moving or self._last_valid is None:
            return
        idle = (self.get_clock().now() - self._last_valid).nanoseconds * 1e-9
        if idle > self._max_age():
            self._send(0.0, 0.0, f'no fresh command for {idle:.3f} s')

    def _send(self, linear_x, angular_z, reason):
        out = Twist()
        out.linear.x = float(linear_x)
        out.angular.z = float(angular_z)
        self._pub.publish(out)
        self._moving = linear_x != 0.0 or angular_z != 0.0
        if reason is not None:
            self.get_logger().warn(f'zero command: {reason}', throttle_duration_sec=1.0)
            self._diag.publish(String(data=reason))


def main(args=None):
    rclpy.init(args=args)
    node = AckermannAdapter()
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
