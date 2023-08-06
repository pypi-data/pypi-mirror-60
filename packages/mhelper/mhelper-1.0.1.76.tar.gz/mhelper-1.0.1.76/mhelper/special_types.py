"""
Defines a Sentinel class, as well as a typical `NOT_PROVIDED` sentinel value.
"""
from enum import Enum, EnumMeta, Flag
from typing import TypeVar, Optional, Iterable, Type


T = TypeVar( "T" )
TTristate = Optional[bool]


def ignore( *_, **__ ):
    pass


class Sentinel:
    """
    Type used for sentinel objects (things that don't do anything but whose presence indicates something).
    The Sentinel also has a `str` method equal to its name, so is appropriate for user feedback. 
    """
    
    
    def __init__( self, name: str ):
        """
        :param name:    Name, for debugging or display. 
        """
        self.__name = name
    
    
    def __str__( self ) -> str:
        return self.__name
    
    
    def __repr__( self ):
        return "Sentinel({})".format( repr( self.__name ) )


NOT_PROVIDED = Sentinel( "(Not provided)" )
"""
NOT_PROVIDED is used to distinguish between a value of `None` and a value that that isn't even provided.
"""


# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# ▒ ENUMS ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒


class MEnum( Enum ):
    """
    An enum class that presents a less verbose string function
    """
    
    
    def __str__( self ):
        return self.name


class MFlagMeta( EnumMeta ):
    """
    Type of `MFlag`.
    """
    
    
    def __getitem__( cls, item ):
        return cls.from_string( item )
    
    
    def from_string( cls, text, delimiter = "|" ):
        elements = text.split( delimiter )
        r = super().__getitem__( elements[0] )
        for it in elements[1:]:
            r |= super().__getitem__( it )
        return r


class MFlag( Flag, metaclass = MFlagMeta ):
    """
    A flag class that presents a less verbose string function
    """
    
    
    def __str__( self ):
        return self.to_string()
    
    
    def to_string( self, delimiter = "|" ):
        text = super().__str__().replace( "{}.".format( type( self ).__name__ ), "" )
        its = text.split( "|" )
        return delimiter.join( reversed( its ) )


_default_filename_path = None


class ArgsKwargs:
    EMPTY: "ArgsKwargs" = None
    
    
    def __init__( self, *args, **kwargs ) -> None:
        self.args = args
        self.kwargs = kwargs
    
    
    def __bool__( self ):
        return bool( self.args ) or bool( self.kwargs )
    
    
    def __getitem__( self, item ):
        r = self.get( item[0], item[1] )
        
        if r is NOT_PROVIDED:
            raise KeyError( item )
        
        return r
    
    
    def get( self, index, name, default = NOT_PROVIDED ):
        if 0 <= index < len( self.args ):
            return self.args[index]
        
        if name:
            return self.kwargs.get( name, default )
        
        return default
    
    
    def __repr__( self ):
        r = []
        
        for x in self.args:
            r.append( "{}".format( x ) )
        
        for k, x in self.kwargs.items():
            r.append( "{} = {}".format( k, x ) )
        
        return ", ".join( r )


class Booly:
    """
    Annotated boolean-like value.
    """
    __slots__ = "value",
    predicate = None
    TRUE: Type["Booly"] = None
    FALSE: Type["Booly"] = None
    
    
    def __init__( self, value ):
        self.value = value
    
    
    def __repr__( self ):
        return "Boolean({}, {})".format( repr(self.predicate), repr( self.value ) )
    
    
    def __bool__( self ):
        return self.predicate


class Truthy( Booly ):
    __slots__ = ()
    predicate = True


class Falsy( Booly ):
    __slots__ = ()
    predicate = False


Booly.TRUE = Truthy
Booly.FALSE = Falsy


class NamespaceDict( dict ):
    def __getattr__( self, item ):
        return self[item]
    
    
    def __dir__( self ) -> Iterable[str]:
        return tuple( frozenset( super().__dir__() ).union( frozenset( self.keys() ) ) )


ArgsKwargs.EMPTY = ArgsKwargs()
