from . import _test_base


def __load():
    from . import test_ansi                  
    from . import test_ansi_format_helper    
    from . import test_cache_helper          
    from . import test_debug                 
    from . import test_documentation         
    from . import test_io_helper             
    from . import test_mannotation
    from . import test_string_helper
    
__load()
_test_base.test.execute()
