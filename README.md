# Робототехника — ПР05–ПР07

ROS 2 workspace (baseline: Ubuntu 26.04, ROS 2 Lyrical, Gazebo Jetty; совместимо с Jazzy).

| Пакет | Работа | Что внутри |
|---|---|---|
| `src/patrol` | ПР04/ПР05 | нода патруля turtlesim, относительный `cmd_vel` |
| `src/course_bringup` | ПР05 | `pose_relay`, `qos_listener`, `launch/patrol.launch.py` |
| `src/course_description` | ПР06 | `urdf/vehicle.urdf.xacro`, `launch/display.launch.py`, RViz |
| `src/course_simulation` | ПР07 | модель/мир SDF, `config/bridge.yaml`, адаптеры, `launch/simulation.launch.py` |

Evidence: `evidence/pr05`, `evidence/pr06`, `evidence/pr07`; сбор — `scripts/prNN_collect.sh`.
Course kit кладётся в `.course-kit/v1/` (нужен для `check_practice.py`).

## Сборка и тесты

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --symlink-install
source install/setup.bash
colcon test && colcon test-result --verbose
```

## ПР05

```bash
ros2 launch course_bringup patrol.launch.py namespace:=robot_a subscriber_reliability:=reliable record:=false
./scripts/pr05_collect.sh            # qos-before/after, bag, replay, bag-metadata
python3 .course-kit/v1/tools/check_practice.py PR05 --submission .
```

## ПР06

```bash
ros2 launch course_description display.launch.py rviz:=true
./scripts/pr06_collect.sh            # model-check.txt, tf-qos.txt, view_frames
```
Дефект: ветка `pr06-defect-lidar-parent` (коммит с parent=camera_link и revert).

## ПР07

```bash
export GZ_SIM_RESOURCE_PATH="$PWD/src/course_simulation/models${GZ_SIM_RESOURCE_PATH:+:$GZ_SIM_RESOURCE_PATH}"
ros2 launch course_simulation simulation.launch.py \
  world:=$PWD/src/course_simulation/worlds/mcity-minimal.sdf \
  bridge_config:=$PWD/src/course_simulation/config/bridge.yaml headless:=true
./scripts/pr07_collect.sh            # checks, rates, bag 40 s -> fixtures/pr07-sensors
./scripts/pr07_collect.sh defect     # сломанный мост evidence/pr07/bridge-broken.yaml
```

## report.json

```bash
python3 scripts/fill_report.py PR05 --commit <sha-реализации> --true public_tests_passed defect_reproduced defect_fixed replay_verified
```
