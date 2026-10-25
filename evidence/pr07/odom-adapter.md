# PR07 — адаптер одометрии

Код: `src/course_simulation/course_simulation/odom_adapter.py` (нода),
`odom_logic.py` (чистая логика), тесты `src/course_simulation/test/test_odom_logic.py`.

## Путь данных

```
AckermannSteering (Gazebo) --/model/course_ackermann/odometry--> ros_gz_bridge
  --/vehicle/odom_gz--> odom_adapter --/vehicle/odom--> потребители
                                     \--/tf (odom -> base_link)
```

## Frames

| | header.frame_id | child_frame_id |
|---|---|---|
| исходные (Gazebo, `/vehicle/odom_gz`) | `course_ackermann/odom` | `course_ackermann/base_link` |
| нормализованные (`/vehicle/odom`, `/tf`) | `odom` | `base_link` |

Нормализация выполняется ровно один раз — в odom_adapter. Сохраняются без
изменений: `header.stamp`, `pose`, `twist`, `pose.covariance`, `twist.covariance`.
Сообщения с другими исходными frames или с NaN/∞ отклоняются (warn в лог, ничего
не публикуется).

## Владельцы tf

| Ребро | Канал | Владелец |
|---|---|---|
| odom → base_link | /tf | odom_adapter (единственный; `/model/course_ackermann/tf` из Gazebo в ROS не мостится) |
| base_link → camera_link, lidar_link, imu_link | /tf_static | robot_state_publisher (URDF из ПР06) |
| base_link → колёса / рулевые кулаки | /tf | robot_state_publisher по `/vehicle/joint_states` из Gazebo |

## Тест сохранения метки времени

`test_odom_logic.py::test_frames_renamed_and_data_preserved` — stamp, pose, twist
и обе covariance равны исходным; `test_transform_keeps_stamp` — у
`TransformStamped` odom→base_link тот же stamp (sec=42, nanosec=123456789).
Отклонение: `test_unexpected_frames_rejected`, `test_non_finite_rejected`.

Живая проверка (из `scripts/pr07_collect.sh`, вывод в `evidence/pr07/checks.txt`):
`ros2 topic echo /vehicle/odom --once` и `tf2_echo odom base_link` показывают
одно и то же положение.
