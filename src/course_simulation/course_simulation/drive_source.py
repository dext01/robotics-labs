"""drive_source: test command source for /drive/safe with a fresh sim-time stamp.

  ros2 run course_simulation drive_source --ros-args -p use_sim_time:=true \
      -p speed:=0.5 -p steering_angle:=0.2
Set speed:=0.0 (or stop the node) to stop the vehicle.
"""
import rclpy
from ackermann_msgs.msg import AckermannDriveStamped
from rclpy.node import Node


class DriveSource(Node):

    def __init__(self):
        super().__init__('drive_source')
        self.declare_parameter('speed', 0.5)
        self.declare_parameter('steering_angle', 0.0)
        self.declare_parameter('rate', 20.0)
        self._pub = self.create_publisher(AckermannDriveStamped, '/drive/safe', 10)
        self.create_timer(1.0 / float(self.get_parameter('rate').value), self._tick)

    def _tick(self):
        now = self.get_clock().now()
        if now.nanoseconds == 0:
            return  # /clock not received yet
        msg = AckermannDriveStamped()
        msg.header.stamp = now.to_msg()
        msg.header.frame_id = 'base_link'
        msg.drive.speed = float(self.get_parameter('speed').value)
        msg.drive.steering_angle = float(self.get_parameter('steering_angle').value)
        self._pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = DriveSource()
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
