"""Structural and geometric checks of vehicle.urdf.xacro.

check_urdf only proves the URDF is a tree; these tests also pin the expected
parent and offset of every sensor frame, the SI-plausible inertias and the
Ackermann geometry.
"""
import math
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import xacro

XACRO = Path(__file__).resolve().parents[1] / 'urdf' / 'vehicle.urdf.xacro'

WHEELBASE = 0.8
TRACK = 0.5
WHEEL_RADIUS = 0.1
MAX_STEER = 0.45

# child -> (expected parent, expected xyz)  — see evidence/pr06/frames.md
SENSORS = {
    'camera_link': ('base_link', (0.47, 0.0, 0.225)),
    'lidar_link': ('base_link', (0.15, 0.0, 0.225)),
    'imu_link': ('base_link', (0.0, 0.0, 0.1)),
}


@pytest.fixture(scope='module')
def urdf_xml():
    return xacro.process_file(str(XACRO)).toxml()


@pytest.fixture(scope='module')
def robot(urdf_xml):
    return ET.fromstring(urdf_xml)


def _vec(text):
    return tuple(float(v) for v in (text or '0 0 0').split())


def _joints(robot):
    out = {}
    for j in robot.findall('joint'):
        origin = j.find('origin')
        out[j.get('name')] = {
            'type': j.get('type'),
            'parent': j.find('parent').get('link'),
            'child': j.find('child').get('link'),
            'xyz': _vec(origin.get('xyz') if origin is not None else None),
            'rpy': _vec(origin.get('rpy') if origin is not None else None),
            'axis': _vec(j.find('axis').get('xyz')) if j.find('axis') is not None else None,
            'limit': j.find('limit'),
        }
    return out


def _parent_of(robot):
    return {j['child']: j for j in _joints(robot).values()}


def _position_in_base(robot, link):
    """Sum of joint offsets from base_link (all joint rpy are zero)."""
    parents = _parent_of(robot)
    x = y = z = 0.0
    while link != 'base_link':
        j = parents[link]
        assert j['rpy'] == (0.0, 0.0, 0.0)
        x, y, z = x + j['xyz'][0], y + j['xyz'][1], z + j['xyz'][2]
        link = j['parent']
    return x, y, z


def test_tree_is_connected_and_acyclic(robot):
    links = {link.get('name') for link in robot.findall('link')}
    joints = _joints(robot)
    children = [j['child'] for j in joints.values()]
    assert len(children) == len(set(children)), 'a link has two parents'
    roots = links - set(children)
    assert roots == {'base_link'}
    assert len(joints) == len(links) - 1
    parents = _parent_of(robot)
    for link in links:
        seen = set()
        while link != 'base_link':
            assert link not in seen, f'cycle through {link}'
            seen.add(link)
            link = parents[link]['parent']


@pytest.mark.parametrize('child', sorted(SENSORS))
def test_sensor_expected_parent(robot, child):
    parent, _ = SENSORS[child]
    j = _parent_of(robot)[child]
    assert j['type'] == 'fixed'
    assert j['parent'] == parent, f'{child} must hang on {parent}, got {j["parent"]}'


@pytest.mark.parametrize('child', sorted(SENSORS))
def test_sensor_position_in_base_link(robot, child):
    _, xyz = SENSORS[child]
    assert _position_in_base(robot, child) == pytest.approx(xyz, abs=1e-6)


def test_wheel_geometry(robot):
    fl = _position_in_base(robot, 'front_left_wheel_link')
    rl = _position_in_base(robot, 'rear_left_wheel_link')
    fr = _position_in_base(robot, 'front_right_wheel_link')
    assert fl[0] - rl[0] == pytest.approx(WHEELBASE)
    assert fl[1] - fr[1] == pytest.approx(TRACK)
    for link in robot.findall('link'):
        if link.get('name').endswith('_wheel_link'):
            cyl = link.find('visual/geometry/cylinder')
            assert float(cyl.get('radius')) == pytest.approx(WHEEL_RADIUS)


def test_joint_types_and_axes(robot):
    for name, j in _joints(robot).items():
        if name.endswith('_wheel_joint'):
            assert j['type'] == 'continuous'
            assert j['axis'] == (0.0, 1.0, 0.0)
        elif name.endswith('_steering_joint'):
            assert j['type'] == 'revolute'
            assert j['axis'] == (0.0, 0.0, 1.0)
            assert float(j['limit'].get('lower')) == pytest.approx(-MAX_STEER)
            assert float(j['limit'].get('upper')) == pytest.approx(MAX_STEER)


def test_inertia_is_physical(robot):
    for link in robot.findall('link'):
        inertial = link.find('inertial')
        assert inertial is not None, f'{link.get("name")} has no inertial'
        assert float(inertial.find('mass').get('value')) > 0
        i = inertial.find('inertia')
        ixx, iyy, izz = (float(i.get(k)) for k in ('ixx', 'iyy', 'izz'))
        assert min(ixx, iyy, izz) > 0
        # triangle inequality for principal moments
        assert ixx + iyy >= izz and iyy + izz >= ixx and ixx + izz >= iyy


def test_visual_and_collision_defined_separately(robot):
    for link in robot.findall('link'):
        if link.get('name').endswith('_steering_link'):
            continue  # knuckle: inertia only
        assert link.find('visual') is not None, link.get('name')
        assert link.find('collision') is not None, link.get('name')


def test_total_mass_is_plausible(robot):
    total = sum(float(link.find('inertial/mass').get('value'))
                for link in robot.findall('link'))
    assert 5.0 < total < 50.0
    assert not math.isnan(total)


@pytest.mark.skipif(shutil.which('check_urdf') is None, reason='check_urdf not installed')
def test_check_urdf(urdf_xml, tmp_path):
    path = tmp_path / 'vehicle.urdf'
    path.write_text(urdf_xml)
    result = subprocess.run(['check_urdf', str(path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'root Link: base_link' in result.stdout
