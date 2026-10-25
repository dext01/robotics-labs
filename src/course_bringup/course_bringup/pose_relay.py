"""pose_relay: reads ``pose`` (remapped to /turtle1/pose) and republishes it as
``sensor_pose`` with a best-effort "sensor" QoS profile.

Topic names are relative, so the launch namespace decides the full name
(``/robot_a/sensor_pose``).
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy, DurabilityPolicy

from course_bringup.pose_types import Pose

SENSOR_QOS = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE,
    history=HistoryPolicy.KEEP_LAST,
    depth=10,
)


class PoseRelay(Node):

    def __init__(self):
        super().__init__('pose_relay')
        self._pub = self.create_publisher(Pose, 'sensor_pose', SENSOR_QOS)
        self._sub = self.create_subscription(Pose, 'pose', self._on_pose, 10)
        self._count = 0
        self.get_logger().info(
            f'relaying {self._sub.topic_name} -> {self._pub.topic_name} (best_effort)')

    def _on_pose(self, msg):
        self._pub.publish(msg)
        self._count += 1
        if self._count % 200 == 0:
            self.get_logger().info(f'relayed {self._count} poses')


def main(args=None):
    rclpy.init(args=args)
    node = PoseRelay()
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
