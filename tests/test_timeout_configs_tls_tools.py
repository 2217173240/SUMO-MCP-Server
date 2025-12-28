def test_timeout_configs_include_tls_tools() -> None:
    from utils.timeout import calculate_adaptive_timeout

    assert calculate_adaptive_timeout("tlsCycleAdaptation") == 120
    assert calculate_adaptive_timeout("tlsCoordinator") == 120

