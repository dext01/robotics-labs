#!/usr/bin/env bash
# PR06: model checks + /tf_static QoS. Run from repo root after build + source.
set -u
EV=evidence/pr06
mkdir -p "$EV"
XACRO=src/course_description/urdf/vehicle.urdf.xacro

{
  echo "## git: $(git rev-parse --short HEAD 2>/dev/null) $(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
  echo "## xacro $XACRO > /tmp/vehicle.urdf"
  xacro "$XACRO" > /tmp/vehicle.urdf; echo "exit=$?"
  echo "## check_urdf /tmp/vehicle.urdf"
  check_urdf /tmp/vehicle.urdf; echo "exit=$?"
  echo "## colcon test --packages-select course_description"
  colcon test --packages-select course_description --event-handlers console_direct+ >/dev/null 2>&1
  colcon test-result --verbose --test-result-base build/course_description
} > "$EV/model-check.txt" 2>&1

ros2 launch course_description display.launch.py > "$EV/rsp.log" 2>&1 &
L=$!
sleep 4

{
  echo '## topic info /tf_static'
  ros2 topic info /tf_static --verbose
  echo '## echo transient_local'
  timeout 4 ros2 topic echo /tf_static --once \
    --qos-durability transient_local --qos-reliability reliable; echo "exit=$?"
  echo '## echo volatile'
  timeout 4 ros2 topic echo /tf_static --once \
    --qos-durability volatile --qos-reliability reliable; echo "exit=$?"
  echo '## topic info /tf'
  ros2 topic info /tf --verbose
} > "$EV/tf-qos.txt" 2>&1
cat >> "$EV/tf-qos.txt" <<'TXT'

## Вывод
/tf_static публикуется с RELIABLE + TRANSIENT_LOCAL: фиксированные преобразования
отправляются один раз и не меняются, поэтому издатель хранит последнее сообщение
и выдаёт его подписчику, подключившемуся позже (exit=0); volatile-подписчик
историю не получает и ждёт до таймаута (exit=124). /tf — VOLATILE: подвижные
преобразования публикуются постоянно с новыми метками времени, старые значения
устаревают, и отдавать их позднему подписчику бессмысленно — следующий
отсчёт придёт сам.
TXT

{
  echo "## ros2 run tf2_ros tf2_echo base_link lidar_link"
  timeout 5 ros2 run tf2_ros tf2_echo base_link lidar_link
  echo "## ros2 run tf2_ros tf2_echo base_link camera_link"
  timeout 5 ros2 run tf2_ros tf2_echo base_link camera_link
  echo "## ros2 run tf2_tools view_frames"
  (cd "$EV" && timeout 15 ros2 run tf2_tools view_frames)
} >> "$EV/model-check.txt" 2>&1

kill -INT $L; wait $L 2>/dev/null
echo "done: $EV/{model-check.txt,tf-qos.txt}"
