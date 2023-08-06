from mhelper import ansi_format_helper
from ._test_base import test, testing


@test
def test_ansi_format_helper():
    try:
        raise ValueError( "Something didn't actually go wrong." )
    except Exception as ex:
        testing( ansi_format_helper.format_traceback_ex( ex ) ).IS_READABLE( "Formatted exception trace (not a real error)" )


if __name__ == "__main__":
    test_ansi_format_helper()
