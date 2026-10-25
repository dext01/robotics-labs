"""qos_listener: subscribes to ``sensor_pose`` with a configurable reliability.

Parameter ``reliability`` = ``reliable`` | ``best_effort``. With ``reliable``
against the best-effort pose_relay the topic is visible but no message
arrives; the node logs the "incompatible QoS" event and a periodic counter.
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy

try:
    from rclpy.event_handler import SubscriptionEventCallbacks
except ImportError:  # pragma: no cover - older rclpy
    from rclpy.qos_event import SubscriptionEventCallbacks

from course_bringup.pose_types import Pose

_RELIABILITY = {
    'reliable': ReliabilityPolicy.RELIABLE,
    'best_effort': ReliabilityPolicy.BEST_EFFORT,
}


def make_qos(reliability, depth=10):
    """Build the subscriber profile; raises ValueError on an unknown name."""
    key = str(reliability).strip().lower()
    if key not in _RELIABILITY:
        raise ValueError(
            f'reliability must be one of {sorted(_RELIABILITY)}, got {reliability!r}')
    return QoSProfile(
        reliability=_RELIABILITY[key],
        history=HistoryPolicy.KEEP_LAST,
        depth=depth,
    )


class QosListener(Node):

    def __init__(self):
        super().__init__('qos_listener')
        self.declare_parameter('reliability', 'reliable')
        self.declare_parameter('report_period', 2.0)
        reliability = self.get_parameter('reliability').value
        qos = make_qos(reliability)
        callbacks = SubscriptionEventCallbacks(incompatible_qos=self._on_incompatible)
        self._sub = self.create_subscription(
            Pose, 'sensor_pose', self._on_msg, qos, event_callbacks=callbacks)
        self._count = 0
        self.get_logger().info(
            f'subscribed to {self._sub.topic_name} with reliability={reliability}')
        self.create_timer(float(self.get_parameter('report_period').value), self._report)

    def _on_msg(self, _msg):
        self._count += 1

    def _on_incompatible(self, event):
        self.get_logger().warn(
            f'incompatible QoS with publisher: total={event.total_count}, '
            f'last_policy_kind={event.last_policy_kind}')

    def _report(self):
        self.get_logger().info(f'received {self._count} messages so far')


def main(args=None):
    rclpy.init(args=args)
    node = QosListener()
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
