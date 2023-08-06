from mhelper import debug_helper as d, ansi_format_helper
from ._test_base import test, testing


class Foo:
    """
    Documentation goes here.
    """
    pass


class Bar:
    """
    Documentation goes here.
    """
    __slots__ = "x", "y"
    
    
    def __init__( self ):
        self.x = 1
        self.y = "y"


class Baz:
    """
    Documentation goes here.
    """
    
    
    def __init__( self ):
        self.x = Foo()
        self.y = Bar()
    
    
    def baz_function( self ):
        """
        My baz function is here.
        :return: 
        """
        pass
    
    
    def another_baz_function( self ):
        pass


def my_fun( x: Bar, y: Baz = 2, z = 3 ) -> str:
    """
    Documentation goes here.
    :param x:   This is X 
    :param y:   This is Y 
    :param z:   This is Z 
    :return:    This is the return value 
    """
    return str( [x, y, z] )


@test
def documentation_tests():
    view = d.ObjectViewer( print = d.ObjectViewer.PRINT_TO_NONE )
    testing( view( 1 ) ).IS_READABLE( f"Documentation for `1`" )
    testing( view( Foo() ) ).IS_READABLE( f"Documentation for `Foo()`" )
    testing( view( Foo ) ).IS_READABLE( f"Documentation for `Foo`" )
    testing( view( Bar() ) ).IS_READABLE( f"Documentation for `Bar()`" )
    testing( view( Baz() ) ).IS_READABLE( f"Documentation for `Baz()`" )
    testing( view( Baz ) ).IS_READABLE( f"Documentation for `Baz`" )
    testing( view( my_fun ) ).IS_READABLE( f"Documentation for `my_fun`" )
    testing( view( None ) ).IS_READABLE( f"Documentation for `None`" )
