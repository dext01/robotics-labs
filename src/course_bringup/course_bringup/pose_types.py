"""turtlesim Pose lives in turtlesim/msg in Jazzy and in turtlesim_msgs/msg in Lyrical."""
try:
    from turtlesim_msgs.msg import Pose  # Lyrical and newer
except ImportError:  # pragma: no cover - depends on the ROS distro
    from turtlesim.msg import Pose  # Jazzy

__all__ = ['Pose']
