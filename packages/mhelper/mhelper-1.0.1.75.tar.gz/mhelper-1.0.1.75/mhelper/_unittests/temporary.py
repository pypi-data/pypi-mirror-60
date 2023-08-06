from mhelper import io_helper
from ._test_base import test, testing
from ..utf_table import TextTable


@test
def temp():
    r = TextTable( (10, 30) )
    
    lst = sorted( io_helper.open_write_opts.items(), key = lambda x: x[0] )
    
    key, value = lst[0]
    r.add_wrapped( (key,  value.__doc__) )
    
    print( r.to_string() )


if __name__ == "__main__":
    test.execute()
