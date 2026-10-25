# PR06 — системы координат course_ackermann

Единицы СИ, оси REP-103 (x вперёд, y влево, z вверх). `base_link` — центр колёсной
базы на высоте осей колёс. Источник: `src/course_description/urdf/vehicle.urdf.xacro`.

Параметры: wheelbase = 0.8 м, track_width = 0.5 м, wheel_radius = 0.1 м,
max_steer = 0.45 рад, chassis_z = 0.1 м, chassis_height = 0.15 м
(верх корпуса chassis_top = 0.175 м).

| Родитель | Потомок | Тип joint | Ожидаемое преобразование (xyz, м; rpy = 0) | Канал | Владелец публикации |
|---|---|---|---|---|---|
| base_link | camera_link | fixed | (0.47, 0, 0.225) | /tf_static | robot_state_publisher |
| base_link | lidar_link | fixed | (0.15, 0, 0.225) | /tf_static | robot_state_publisher |
| base_link | imu_link | fixed | (0, 0, 0.1) | /tf_static | robot_state_publisher |
| base_link | rear_left_wheel_link | continuous, ось y | (-0.4, 0.25, 0) + вращение | /tf | robot_state_publisher (только при наличии /joint_states) |
| base_link | rear_right_wheel_link | continuous, ось y | (-0.4, -0.25, 0) + вращение | /tf | robot_state_publisher (только при /joint_states) |
| base_link | front_left_steering_link | revolute, ось z, ±0.45 | (0.4, 0.25, 0) + руль | /tf | robot_state_publisher (только при /joint_states) |
| base_link | front_right_steering_link | revolute, ось z, ±0.45 | (0.4, -0.25, 0) + руль | /tf | robot_state_publisher (только при /joint_states) |
| front_left_steering_link | front_left_wheel_link | continuous, ось y | (0, 0, 0) + вращение | /tf | robot_state_publisher (только при /joint_states) |
| front_right_steering_link | front_right_wheel_link | continuous, ось y | (0, 0, 0) + вращение | /tf | robot_state_publisher (только при /joint_states) |

Не публикуются в ПР06: `map`, `odom` (→ `odom → base_link` появится в ПР07, владелец —
адаптер одометрии). Fixed Frame в RViz = `base_link`.

Правило: у каждого ребра ровно один владелец. Перед повторным запуском прежний
launch с robot_state_publisher останавливается, иначе два издателя /tf_static.

## Дефект (ветка `pr06-defect-lidar-parent`)

Родитель `lidar_link` заменён на `camera_link`, offset (0.15, 0, 0.225) сохранён.
Ожидаемое ошибочное положение лидара в base_link: (0.47 + 0.15, 0, 0.225 + 0.225) =
**(0.62, 0, 0.45)** — лидар «улетает» вперёд и вверх за камеру. `check_urdf` такое
дерево принимает (оно по-прежнему связное и ацикличное); падают тесты
`test_sensor_expected_parent[lidar_link]` и `test_sensor_position_in_base_link[lidar_link]`.
Исправление — вернуть `parent="base_link"` (revert-коммит в той же ветке).
