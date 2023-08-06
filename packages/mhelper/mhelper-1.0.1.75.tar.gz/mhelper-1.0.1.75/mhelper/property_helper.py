"""
Various property related helpers:

* Indexable properties
* Frozen classes
* Class properties 
"""
from typing import Type, TypeVar, Union, Callable


T = TypeVar( "T" )


def itemproperty( f ):
    """
    Like the `@property` decorator, but creates an indexable property.
    
    Note that the _setter_ is called `itemsetter` and not `setter`.
    (This is to avoid PyLint or IDEs being confused as they make certain assumptions about `.setter` decorators.)
    
    ```
    class MyClass:
        @itemproperty
        def eggs( item ):
            return self._eggs[item]
            
        @eggs.itemsetter
        def eggs( item, value ):
           self._eggs[item] = value 
    
    m = MyClass()
    m.eggs["spam"] = "beans"
    print( m.eggs["spam"] )
    ``` 
    """
    return _ItemPropertyClass( f )


class _ItemPropertyClass:
    def __init__( self, getter ):
        self._getter = getter
        self._setter = None
    
    
    def __get__( self, instance, owner ):
        return _BoundItemPropertyClass( instance, self )
    
    
    def itemsetter( self, setter ):
        self._setter = setter
        return self


class _BoundItemPropertyClass:
    def __init__( self, self2, class_: _ItemPropertyClass ):
        self.__self2 = self2
        self.__class = class_
    
    
    def __getitem__( self, item ):
        return self.__class._getter( self.__self2, item )
    
    
    def __setitem__( self, key, value ):
        return self.__class._setter( self.__self2, key, value )


class FrozenAttributes:
    """
    Prevents adding attributes to the class after __init__ has been called.
    """
    __KEY = "_FrozenAttributes__lock"
    
    
    def __init__( self ):
        setattr( self, FrozenAttributes.__KEY, None )
    
    
    def __setattr__( self, key: str, value: object ) -> None:
        """
        Prohibits new attributes being set on this class.
        This guards against functionless legacy setup.  
        """
        if hasattr( self, FrozenAttributes.__KEY ) and not hasattr( self, key ):
            raise TypeError( "Unrecognised attribute on «{}»".format( type( self ) ) )
        
        object.__setattr__( self, key, value )


class FrozenValues:
    """
    Prevents changing attributes or their values on the object after __init__ has been called.
    """
    __KEY = "_FrozenValues__lock"
    
    
    def __init__( self ):
        setattr( self, FrozenValues.__KEY, None )
    
    
    def __setattr__( self, key: str, value: object ) -> None:
        """
        Prohibits new attributes being set on this class.
        This guards against functionless legacy setup.  
        """
        if hasattr( self, FrozenValues.__KEY ):
            raise TypeError( "Cannot change attributes on this object after it has been intiailsied. «{}»".format( type( self ) ) )
        
        object.__setattr__( self, key, value )


def coalesce( object_, *fields, type: Type[T] = object ) -> T:
    for field in fields:
        if object_ is None:
            return None
        
        object_ = getattr( object_, field )
    
    return object_


class read_only_class_property( object ):
    """
    Defines a read-only-class-property
    
    Usage:
    
        @read_only_class_property
        def fn( cls ):
            pass
            
    OR:

        @read_only_class_property
        @classmethod
        def fn( cls ):
            pass
        
    OR:

        @classmethod    
        def _fn( cls )
            pass
            
        fn = read_only_class_property( _fn )
        
    Method 1 may issue a linter warning because the method isn't seen as a class
    method and so `cls` should be named `self`. Method 2 may issue a warning
    because "This decorator will not receive a callable it may expect". Method
    3 issues no warning but is more verbose. Renaming `cls` to `self` in method
    1 also works, but can be confusing.
    """
    __slots__ = ["fn"]
    
    
    def __init__( self, fn : Union[Callable, classmethod] ):
        """
        :param fn:  The function to decorate.
                    If this is alreafdy decorated with `classmethod`, it is 
                    unwrapped.  
        """
        if isinstance( fn, classmethod ):
            fn = fn.__func__
        
        self.fn = fn
    
    
    def __get__( self, obj, owner ):
        return self.fn( owner )
