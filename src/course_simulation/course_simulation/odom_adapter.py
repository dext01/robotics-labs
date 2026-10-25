"""odom_adapter: /vehicle/odom_gz -> /vehicle/odom + the only dynamic tf odom->base_link."""
import rclpy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from tf2_ros import TransformBroadcaster

from course_simulation.odom_logic import normalize, to_transform


class OdomAdapter(Node):

    def __init__(self):
        super().__init__('odom_adapter')
        self._pub = self.create_publisher(Odometry, '/vehicle/odom', 10)
        self._tf = TransformBroadcaster(self)
        self.create_subscription(Odometry, '/vehicle/odom_gz', self._on_odom, 10)

    def _on_odom(self, msg):
        out, reason = normalize(msg)
        if out is None:
            self.get_logger().warn(f'rejected odometry: {reason}', throttle_duration_sec=1.0)
            return
        self._pub.publish(out)
        self._tf.sendTransform(to_transform(out, TransformStamped))


def main(args=None):
    rclpy.init(args=args)
    node = OdomAdapter()
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
