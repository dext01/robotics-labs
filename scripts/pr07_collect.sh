#!/usr/bin/env bash
# PR07: headless run, checks, rates, recording. Run from repo root.
#   ./scripts/pr07_collect.sh            # normal config
#   ./scripts/pr07_collect.sh defect     # broken bridge copy -> evidence/pr07/defect.txt
set -u
MODE=${1:-normal}
EV=evidence/pr07
mkdir -p "$EV" fixtures
export GZ_SIM_RESOURCE_PATH="$PWD/src/course_simulation/models${GZ_SIM_RESOURCE_PATH:+:$GZ_SIM_RESOURCE_PATH}"
WORLD=$PWD/src/course_simulation/worlds/mcity-minimal.sdf
if [ "$MODE" = defect ]; then BRIDGE=$PWD/$EV/bridge-broken.yaml; OUT=$EV/defect.txt
else BRIDGE=$PWD/src/course_simulation/config/bridge.yaml; OUT=$EV/checks.txt; fi

gz sdf -k src/course_simulation/models/course_ackermann/model.sdf > "$EV/gz-sdf-check.txt" 2>&1

ros2 launch course_simulation simulation.launch.py world:="$WORLD" \
  bridge_config:="$BRIDGE" headless:=true > >(tee "$EV/headless-$MODE.log") 2>&1 &
L=$!
sleep 15

{
  echo "## mode=$MODE bridge=$BRIDGE"
  echo "## ros2 topic echo /clock --once"; timeout 5 ros2 topic echo /clock --once
  for t in /vehicle/gz_cmd_vel /vehicle/imu /vehicle/scan /vehicle/camera/image_raw /vehicle/odom_gz /vehicle/odom /tf_static; do
    echo "## ros2 topic info -v $t"; ros2 topic info -v "$t"
  done
  echo "## gz topic -i -t /model/course_ackermann/cmd_vel"; gz topic -i -t /model/course_ackermann/cmd_vel
  echo "## gz topic -i -t /model/course_ackermann/imu"; gz topic -i -t /model/course_ackermann/imu
  echo "## timeout 3 ros2 topic echo /vehicle/imu --once (bridge side)"
  timeout 3 ros2 topic echo /vehicle/imu --once --qos-reliability best_effort | head -n 20; echo "exit=${PIPESTATUS[0]}"
  echo "## timeout 3 gz topic -e -t /model/course_ackermann/imu -n 1"
  timeout 3 gz topic -e -t /model/course_ackermann/imu -n 1 | head -n 20

  echo "## odom before command"; timeout 5 ros2 topic echo /vehicle/odom --once --field pose.pose.position
  ros2 run course_simulation drive_source --ros-args -p use_sim_time:=true -p speed:=0.6 -p steering_angle:=0.2 &
  D=$!
  sleep 4
  echo "## ros2 topic echo /vehicle/gz_cmd_vel --once"; timeout 5 ros2 topic echo /vehicle/gz_cmd_vel --once
  echo "## timeout 3s gz topic -e -t /model/course_ackermann/cmd_vel"; timeout 3s gz topic -e -t /model/course_ackermann/cmd_vel | head -n 20
  sleep 4
  echo "## odom after 8 s of command"; timeout 5 ros2 topic echo /vehicle/odom --once
  echo "## tf2_echo odom base_link"
  timeout 5 ros2 run tf2_ros tf2_echo odom base_link --ros-args -p use_sim_time:=true
  echo "## gz dynamic_pose (body + wheels)"
  timeout 3 gz topic -e -t /world/mcity_minimal/dynamic_pose/info -n 1 | head -n 80
  kill -INT $D; wait $D 2>/dev/null
  # drive_source stopped -> ackermann_adapter watchdog sends one zero Twist after 0.25 s
  echo "## gz stats (RTF)"; timeout 3 gz topic -e -t /stats -n 1
} > "$OUT" 2>&1

if [ "$MODE" = normal ]; then
  {
    for t in /vehicle/camera/image_raw /vehicle/scan /vehicle/imu /vehicle/odom /clock; do
      echo "## ros2 topic hz $t (10 s)"; timeout --signal=INT 10 ros2 topic hz "$t" | tail -n 5
    done
  } > "$EV/rates.txt" 2>&1

  # record with the vehicle moving
  ros2 run course_simulation drive_source --ros-args -p use_sim_time:=true -p speed:=0.5 -p steering_angle:=0.15 &
  D=$!
  B=fixtures/pr07-sensors
  [ -e "$B" ] && B=fixtures/pr07-sensors-$(date +%H%M%S)
  timeout --preserve-status --signal=INT --kill-after=5s 40s \
    ros2 bag record --storage mcap --use-sim-time -o "$B" \
    --topics /vehicle/camera/image_raw /vehicle/scan /vehicle/imu /vehicle/odom \
    /tf /tf_static /clock
  kill -INT $D; wait $D 2>/dev/null
  ros2 bag info "$B" | tee "$EV/bag-info.txt"
fi

kill -INT $L; wait $L 2>/dev/null
[ "$MODE" = normal ] && cp "$EV/headless-normal.log" "$EV/headless.txt"
echo "done: $OUT"
