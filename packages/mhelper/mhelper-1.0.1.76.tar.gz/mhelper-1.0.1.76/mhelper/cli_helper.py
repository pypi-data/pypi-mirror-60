import sys
from mhelper import ansi


class __EPrint:
    __slots__ = "enabled",
    
    
    def __init__( self ):
        self.enabled = True
    
    
    def __call__( self, x, end = "\n" ):
        """
        Writes to standard error (with highlighting).
        """
        if self.enabled:
            print( ansi.FORE_GREEN + str( x ) + ansi.RESET, end = end, file = sys.stderr )


class __OPrint:
    __slots__ = "enabled", "output_terminated"
    
    
    def __init__( self ):
        self.enabled = True
        self.output_terminated = False
    
    
    def __call__( self, x, end = "\n" ):
        """
        Writes to standard error (with highlighting).
        """
        if self.output_terminated:
            return False
        
        if not self.enabled:
            return True
        
        try:
            print( x, end = end, file = sys.stdout )
            return True
        except BrokenPipeError:
            eprint( "Discarding future stream." )
            __output_terminated = True
            return False


eprint = __EPrint()
oprint = __OPrint()
