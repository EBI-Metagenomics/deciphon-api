from deciphon_api.core.logging import LoggingLevel


def test_logging_level():

    critical = LoggingLevel("critical")
    assert critical.level == 50

    error = LoggingLevel("error")
    assert error.level == 40

    warning = LoggingLevel("warning")
    assert warning.level == 30

    info = LoggingLevel("info")
    assert info.level == 20

    debug = LoggingLevel("debug")
    assert debug.level == 10

    notset = LoggingLevel("notset")
    assert notset.level == 0
