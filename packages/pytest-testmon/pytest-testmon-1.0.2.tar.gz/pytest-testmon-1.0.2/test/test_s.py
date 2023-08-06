import pytest

pytest_plugins = ("pytester",)


@pytest.mark.skip
def test_speed(testdir):
    testdir.makepyfile(
        test_a="""
        import pytest
        @pytest.mark.parametrize("test_input", range(500))
        def test_1(test_input):
            pass
    """
    )
    testdir.runpytest_inprocess("--testmon-dev")
