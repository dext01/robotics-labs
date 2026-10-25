#!/usr/bin/env bash
# PR05: QoS before/after on the live stream and on the replay of ONE bag.
# Run from the repository root after `colcon build && source install/setup.bash`.
# turtlesim needs a display; on a headless machine: export QT_QPA_PLATFORM=offscreen
set -u
EV=evidence/pr05
BAG=$EV/bag
TOPIC=/robot_a/sensor_pose
mkdir -p "$EV"
rm -rf "$BAG"

stop() { kill -INT "$1" 2>/dev/null; wait "$1" 2>/dev/null; }

echo ">>> 1/3 live, subscriber_reliability:=reliable (defect)"
ros2 launch course_bringup patrol.launch.py \
  namespace:=robot_a subscriber_reliability:=reliable record:=false \
  > "$EV/launch-before.log" 2>&1 &
L=$!
sleep 6
{
  echo "## live: ros2 topic list"
  ros2 topic list
  echo "## live: ros2 topic info $TOPIC --verbose"
  ros2 topic info "$TOPIC" --verbose
  echo "## live: timeout 3s ros2 topic echo $TOPIC --qos-reliability reliable --once"
  timeout 3s ros2 topic echo "$TOPIC" --qos-reliability reliable --once
  echo "exit=$?  (124 = timeout: topic is visible, but no message arrives)"
  echo "## live: qos_listener log"
  grep -E 'qos_listener' "$EV/launch-before.log" | tail -n 5
} > "$EV/qos-before.txt" 2>&1
stop $L

echo ">>> 2/3 live, subscriber_reliability:=best_effort (fixed) + MCAP recording"
ros2 launch course_bringup patrol.launch.py \
  namespace:=robot_a subscriber_reliability:=best_effort \
  record:=true bag_dir:="$BAG" \
  > "$EV/launch-after.log" 2>&1 &
L=$!
sleep 6
{
  echo "## live: ros2 topic info $TOPIC --verbose"
  ros2 topic info "$TOPIC" --verbose
  echo "## live: timeout 3s ros2 topic echo $TOPIC --qos-reliability best_effort --once"
  timeout 3s ros2 topic echo "$TOPIC" --qos-reliability best_effort --once
  echo "exit=$?"
  echo "## live: qos_listener log"
  grep -E 'qos_listener' "$EV/launch-after.log" | tail -n 3
} > "$EV/qos-after.txt" 2>&1
sleep 10   # record ~16 s in total
stop $L

echo ">>> 3/3 replay of the same bag with config/qos-overrides.yaml"
ros2 bag play "$BAG" --loop --qos-profile-overrides-path config/qos-overrides.yaml \
  > "$EV/replay.log" 2>&1 &
P=$!
sleep 3
{
  echo "## replay: timeout 3s ros2 topic echo $TOPIC --qos-reliability reliable --once"
  timeout 3s ros2 topic echo "$TOPIC" --qos-reliability reliable --once
  echo "exit=$?"
} >> "$EV/qos-before.txt" 2>&1
{
  echo "## replay: timeout 3s ros2 topic echo $TOPIC --qos-reliability best_effort --once"
  timeout 3s ros2 topic echo "$TOPIC" --qos-reliability best_effort --once
  echo "exit=$?"
} >> "$EV/qos-after.txt" 2>&1
stop $P

{
  echo "## ros2 bag info $BAG"
  ros2 bag info "$BAG"
} >> "$EV/qos-after.txt" 2>&1
cp "$BAG/metadata.yaml" "$EV/bag-metadata.yaml"
echo ">>> done: see $EV/qos-before.txt and $EV/qos-after.txt"
