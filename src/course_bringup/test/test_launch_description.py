"""Static checks of patrol.launch.py (no processes are started)."""
import importlib.util
from pathlib import Path

from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition

LAUNCH = Path(__file__).resolve().parents[1] / 'launch' / 'patrol.launch.py'


def _load():
    spec = importlib.util.spec_from_file_location('patrol_launch', LAUNCH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.generate_launch_description()


def test_declares_required_arguments():
    names = {a.name for a in _load().entities if isinstance(a, DeclareLaunchArgument)}
    assert {'namespace', 'record', 'bag_dir', 'subscriber_reliability'} <= names


def test_recorder_is_conditional():
    recorders = [e for e in _load().entities if isinstance(e, ExecuteProcess)]
    assert len(recorders) == 1
    assert isinstance(recorders[0].condition, IfCondition)


def test_launch_uses_relative_topic_names_in_nodes():
    text = LAUNCH.read_text()
    assert "('cmd_vel', '/turtle1/cmd_vel')" in text
    assert "('pose', '/turtle1/pose')" in text
    assert "'-s', 'mcap'" in text
