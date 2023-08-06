import argparse
import sys
from enum import Enum
from typing import List, Callable, TypeVar, Sequence, Generic
from mhelper import string_helper


T = TypeVar( "T" )


class _HelpTopicAction( argparse.Action ):
    
    def __init__( self, option_strings,
                  dest = argparse.SUPPRESS,
                  default = argparse.SUPPRESS,
                  help = None,
                  content = None,
                  topics = None ):
        super().__init__(
                option_strings,
                dest = dest,
                default = default,
                nargs = "?",
                help = help,
                metavar = "TOPIC" )
        self.content = content
        self.topics = { k.lower(): v for k, v in topics.items() }
    
    
    def __call__( self, parser: "ArgumentParser", namespace, values, option_string = None ):
        if not values:
            parser.print_help()
        else:
            print( self.topics[values.lower()](), file = sys.stderr )
        
        parser.exit()


def create_parser( module_name, description_ex = "", *, topics = None, **kwargs ) -> "ArgumentParser":
    import mhelper.string_helper
    module = sys.modules[module_name]
    version = getattr( module, "__version__", None )
    
    MAIN_SCRIPT = ".__main__"
    
    if version is None and module_name.endswith( MAIN_SCRIPT ):
        module_2_name = module_name[:-len( MAIN_SCRIPT )]
        module_2 = sys.modules[module_2_name]
        version = getattr( module_2, "__version__", None )
    
    if description_ex:
        description_ex = "\n\n" + description_ex
    
    p = ArgumentParser( description = mhelper.string_helper.strip_lines_to_first( module.__doc__ ) + description_ex,
                        **kwargs )
    
    if not topics:
        p.add_argument( "--help", "-?", action = 'help', default = argparse.SUPPRESS, help = "Show this help message and exit." )
    else:
        p.add_argument( "--help", "-?", action = _HelpTopicAction, help = f"Shows a help topic, or this message if no topic is specified. Available topics: {', '.join( f'`{x}`' for x in topics )}.", topics = topics )
    
    if version:
        p.add_argument( '--version', action = 'version', version = f"%(prog)s {version}" )
    
    return p


def args_to_function( fn: Callable[..., T], args = None, inverse = "" ) -> T: 
    from mhelper.documentation_helper import Documentation
    d = Documentation( fn.__doc__ )
    pdoc = d["param"]
    import inspect
    sig = inspect.signature( fn )
    
    p = ArgumentParser( description = d[""][""] )
    p.add_argument( "--help", "-?", action = 'help', default = argparse.SUPPRESS, help = "Show this help message and exit." )
    
    for index, param in enumerate( sig.parameters.values() ):  # type: inspect.Parameter
        k = param.name
        a = param.annotation
        d = param.default
        doc = pdoc.get( k, "" )
        
        if index == 0 and param.kind != inspect.Parameter.KEYWORD_ONLY:
            fk = f"{k}"
            kwargs = { }
        else:
            fk = f"--{k}"
            kwargs = dict( required = d is inspect.Parameter.empty )
        
        if not doc.endswith( "." ):
            doc += "."
        
        doc = f"{doc} Type: {string_helper.type_name( type = a )}."
        
        if getattr( a, "_name", None ) == "Sequence":
            p.add_argument( fk, action = "store", nargs = "*", type = a.__args__[0], help = doc, default = d, **kwargs )
        elif isinstance( a, type ) and issubclass( a, Enum ):
            p.add_argument( fk, action = "store", nargs = "*", type = a.__getitem__, help = doc, default = d, **kwargs )
        elif a is bool:
            if d is True:
                p.add_argument( f"--{k}", action = "store_true", help = doc )
            elif inverse:
                nk = inverse.format( k )
                
                if d is False:
                    p.add_argument( f"--{nk}", dest = k, action = "store_false", help = doc )
                else:
                    group = p.add_mutually_exclusive_group( required = True )
                    group.add_argument( f"--{k}", dest = k, action = "store_true", help = doc )
                    group.add_argument( f"--{nk}", dest = k, action = "store_false", help = "Converse of --{k}." )
            else:
                p.add_argument( fk, action = "store", type = a, help = doc, default = d, **kwargs )
        else:
            p.add_argument( fk, action = "store", type = a, help = doc, default = d, **kwargs )
    
    kwargs = p.parse_args( args ).__dict__
    
    fn( **kwargs )


class ParsedArgs:
    def __init__( self, data: dict ):
        self.data = data
    
    
    def __getitem__( self, *args, **kwargs ):
        return self.data.__getitem__( *args, **kwargs )
    
    
    def get( self, *args, **kwargs ):
        return self.data.get( *args, **kwargs )


class ArgWrapper:
    def __init__( self, owner: "ArgumentParser", key: str ):
        self.owner = owner
        self.key = key
    
    
    def read( self ):
        return self.owner._parsed[self.key]


class ArgumentParser( argparse.ArgumentParser ):
    def __init__( self, *args, topics = None, **kwargs ):
        super().__init__( *args,
                          formatter_class = argparse.RawDescriptionHelpFormatter,
                          add_help = False,
                          **kwargs )
        self._parsed = None
        self.topics = topics
    
    
    def format_usage( self ):
        return self.format_help() + "\n~~> "
    
    
    def parse( self, *args, **kwargs ) -> ParsedArgs:
        ns = super().parse_args( *args, **kwargs )
        self._parsed = ParsedArgs( ns.__dict__ )
        return self._parsed
    
    
    def add( self, *args, **kwargs ) -> ArgWrapper:
        if "help" in kwargs and "default" in kwargs:
            d = kwargs['default']
            
            if any( isinstance( d, x ) for x in (int, str, float, bool) ) and d != argparse.SUPPRESS:
                if not kwargs["help"].endswith( "." ):
                    kwargs["help"] += "."
                
                kwargs["help"] += f" Default = {d!r}."
        
        action = super().add_argument( *args, **kwargs )
        return ArgWrapper( self, action.dest )
