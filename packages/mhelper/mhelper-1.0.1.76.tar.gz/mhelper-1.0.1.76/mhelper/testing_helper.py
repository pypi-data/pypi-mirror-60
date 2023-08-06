"""
Deprecated - too specific.
"""
import argparse
import inspect
import pydoc
import shutil
from typing import Dict, Union, Tuple, Callable, List


class SimpleTestCollection:
    skip_readability = False
    
    
    def __init__( self ):
        self.tests: List[Tuple[str, Callable[[], None]]] = []
        self.current = None
    
    
    def __call__( self, fn ):
        """
        !DECORATOR
        
        Registers a function with this test suite. 
        """
        import mhelper.file_helper
        f = inspect.stack()[1].filename
        m = mhelper.file_helper.get_filename_without_extension( f ) + "/" + fn.__qualname__
        m = m.replace( "_tests", "" )
        m = m.replace( "test_", "" )
        self.tests.append( (m, fn) )
        return fn
    
    
    def list( self ) -> List[str]:
        """
        Returns test names.
        """
        return [name for name, _ in self.tests]
    
    
    def execute( self, args: Union[None, str, list, tuple, Dict[str, object]] = None ):
        """
        Executes the test suite.
        
        :param args:    Arguments.
                        The default, `None`, uses arguments from `sys.argv`.
                        A `str`, `tuple`, `list` or preparsed `dict` is also accepted.
                        The accepted arguments can be described by passing `"--help"`
        """
        tests = self.tests
        
        if not isinstance( args, dict ):
            if isinstance( args, str ):
                import shlex
                args = shlex.split( args )
            
            p = argparse.ArgumentParser( description = "Executes the test suite." )
            p.add_argument( "--unattended", "-u", action = "store_true", help = "Does not prompt the user the user to check test output. Suck tests are automatically passed but their output is still written to the terminal." )
            p.add_argument( "--list", "-l", action = "store_true", help = "Lists, but does not exact, the tests." )
            p.add_argument( "--list-prefixes", "-p", action = "store_true", help = "Lists test prefixes." )
            p.add_argument( "--continue", "-c", action = "store_true", help = "Continues running other tests after failing a test." )
            p.add_argument( "prefix", nargs = "?", help = "Only exacts the tests with the specified prefix." )
            args = p.parse_args( args ).__dict__
        
        self.skip_readability = args["unattended"]
        
        if self.skip_readability:
            print( "Note: Passing readability tests without prompting user." )
        
        if args["prefix"]:
            prefix = args["prefix"] + "/"
            tests = [(name, function) for name, function in self.tests if name.startswith( prefix )]
        
        if args["list_prefixes"]:
            prefixes = { name.split( "/", 1 )[0] for name, _ in self.tests }
            
            for prefix in sorted( prefixes ):
                print( prefix )
            
            return
        
        if args["list"]:
            for name, _ in tests:
                print( name )
            
            return
        
        for name, function in tests:
            print( "EXECUTE {}".format( name ) )
            
            self.current = function
            
            try:
                function()
            except Exception as ex:
                from mhelper import ansi_format_helper
                ansi_format_helper.print_traceback( ex, message = "a SimpleTestCollection test raised an error" )
                
                if not args["continue"]:
                    return
            finally:
                self.current = None
    
    
    def testing( self, value ) -> "Testing":
        """
        Returns a `Testing` object for this suite, on the specified `value`.
        """
        return Testing( self, value )


class Testing:
    """
    Testing helpers for a specified `value`.
    """
    __slots__ = "collection", "value"
    
    
    def __init__( self, c: SimpleTestCollection, value ):
        self.collection = c
        self.value = value
    
    
    def __repr__( self ):
        return ""
    
    
    def IS_INSTANCE( self, expected_type ):
        actual = self.value
        
        assert isinstance( actual, expected_type )
    
    
    def SET_EQUALS( self, expected ):
        assert_equals( set( self.value ), set( expected ) )
    
    
    def IS_TRUE( self ):
        assert_equals( self.value, True )
    
    
    def IS_FALSE( self ):
        assert_equals( self.value, False )
    
    
    def EQUALS( self, expected ):
        assert_equals( self.value, expected )
    
    
    def ERRORS( self, t = Exception ):
        try:
            self.value()
        except t:
            pass
        else:
            assert False, "Expected error"
    
    
    def IS_READABLE( self, comment ):
        from mhelper import ansi, ansi_helper
        
        r = []
        
        w, h = shutil.get_terminal_size()
        s = ansi.FORE_YELLOW + ansi.BACK_BLACK
        e = ansi.RESET
        l = s + ("=" * w) + e
        ls = s + (" " * w) + e
        
        r.append( l )
        r.append( s + "Readability test, please check.".ljust( w ) + e )
        r.append( s + ansi_helper.ljust( f"{ansi.DIM} - {self.collection.current.__module__}::{ansi.ITALIC}{self.collection.current.__qualname__}{ansi.ITALIC_OFF}{ansi.DIM_OFF} ({comment})", w ) + e )
        r.append( l )
        r.append( str( self.value ) )
        r.append( l )
        
        if self.collection.skip_readability:
            print( "\n".join( r ) )
        else:
            for _ in range( h ):
                r.append( ls )
            
            pydoc.pager( "\n".join( r ) )


def assert_equals( actual : object, expected : object ) -> None:
    """
    Root test predicate.
    """
    if expected is None or expected is True or expected is False:
        assert actual is expected
    assert actual == expected
