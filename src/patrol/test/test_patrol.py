from patrol.patrol_node import phase_command


def test_forward_phase():
    assert phase_command(0.5, 2.0, 1.0, 1.0, 1.5) == (1.0, 0.0)


def test_turn_phase():
    assert phase_command(2.5, 2.0, 1.0, 1.0, 1.5) == (0.0, 1.5)


def test_phase_repeats():
    assert phase_command(3.5, 2.0, 1.0, 1.0, 1.5) == (1.0, 0.0)
