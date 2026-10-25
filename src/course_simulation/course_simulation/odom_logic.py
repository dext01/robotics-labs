"""Pure odometry frame normalisation (unit-tested).

course_ackermann/odom -> odom, course_ackermann/base_link -> base_link.
stamp, pose, twist and both covariances are kept unchanged. Messages with other
source frames or non-finite values are rejected.
"""
import copy
import math

SOURCE_FRAME = 'course_ackermann/odom'
SOURCE_CHILD = 'course_ackermann/base_link'
TARGET_FRAME = 'odom'
TARGET_CHILD = 'base_link'


def _numbers(msg):
    p, q = msg.pose.pose.position, msg.pose.pose.orientation
    lin, ang = msg.twist.twist.linear, msg.twist.twist.angular
    yield from (p.x, p.y, p.z, q.x, q.y, q.z, q.w)
    yield from (lin.x, lin.y, lin.z, ang.x, ang.y, ang.z)
    yield from msg.pose.covariance
    yield from msg.twist.covariance


def normalize(msg):
    """Return (normalised copy, None) or (None, reason)."""
    if msg.header.frame_id != SOURCE_FRAME or msg.child_frame_id != SOURCE_CHILD:
        return None, (f'unexpected frames {msg.header.frame_id!r} -> '
                      f'{msg.child_frame_id!r}')
    if not all(math.isfinite(v) for v in _numbers(msg)):
        return None, 'non-finite value in odometry'
    out = copy.deepcopy(msg)
    out.header.frame_id = TARGET_FRAME
    out.child_frame_id = TARGET_CHILD
    return out, None


def to_transform(odom, transform_cls):
    """Build odom->base_link TransformStamped with the same stamp as ``odom``."""
    t = transform_cls()
    t.header.stamp = odom.header.stamp
    t.header.frame_id = odom.header.frame_id
    t.child_frame_id = odom.child_frame_id
    p = odom.pose.pose.position
    t.transform.translation.x, t.transform.translation.y, t.transform.translation.z = p.x, p.y, p.z
    t.transform.rotation = odom.pose.pose.orientation
    return t
