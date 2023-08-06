"""
Contains the TargetWriter class, for writing to arbitrary streams, usually specified by a (text) CLI parameter.
"""
import os
import sys
import tempfile
from itertools import chain
from typing import Dict, Type, Union, List, BinaryIO, TextIO, Callable

from mhelper import file_helper, io_helper
from mhelper.exception_helper import SwitchError


TBStr = Union[str, bytes]


class WriterBase:
    """
    Base class for writers.
    
    The derived class should implement:
        * (optional) A constructor
        * (optional) on_close
        * (optional) write
        * on_describe
        
    !ABSTRACT
        
    :ivar extension: Extension of the file.
    :ivar closed:    `True` once the file has been closed.
    """
    __slots__ = "extension", "type", "closed"
    
    
    def __init__( self, *, extension = None, mode = str ):
        """
        CONSTRUCTOR
        The derived class should pass any and all `**kwargs` to the base class.
        Other `**kwargs` may be added later.
        `*args` are not used and may be passed or not.
        :param extension: Extension of the file
        """
        self.extension = extension
        self.type = mode
        self.closed = False
    
    
    def __enter__( self ):
        return self
    
    
    def __exit__( self, exc_type, exc_val, exc_tb ):
        self.close()
    
    
    def close( self ) -> None:
        if self.closed:
            return
        
        self.on_close()
        
        self.closed = True
    
    
    def write( self, text: TBStr ) -> None:
        self.on_write( text )
    
    
    def on_close( self ):
        """
        !VIRTUAL 
        """
        pass
    
    
    def on_write( self, text: TBStr ) -> None:
        """
        !VIRTUAL
        """
        pass


class BufferedWriter( WriterBase ):
    """
    Buffers all the output data to `self.lines` (currently just in memory).
    
    The derived class should commit the data when `on_close` is called.
    
    !ABSTRACT
    """
    
    
    def __init__( self, *args, **kwargs ) -> None:
        super().__init__( *args, **kwargs )
        self.lines: List[TBStr] = []
    
    
    def on_write( self, text: TBStr ) -> None:
        if self.closed:
            raise ValueError( "The virtual stream has already been closed." )
        
        self.lines.append( text )
    
    
    def __repr__( self ):
        return self.__class__.__name__
    
    
    def set_extension( self, value: TBStr ) -> None:
        pass


class StreamWriter( BufferedWriter ):
    """
    Dumps all the data to std-out (`sys.__stdout__`) when the stream is closed.
    
    Note that only string data is written. Binary data is ignored.
    """
    
    
    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        
        if self.type is not str:
            raise ValueError( "The `{}` only supports `str` output (not `{}`).".format( type( self ).__name__, type( self.type ).__name__ ) )
        
        self.stream = self.get_stream()
    
    
    def get_stream( self ):
        return sys.__stdout__
    
    
    def on_close( self ):
        assert self.type is str
        
        for line in self.lines:
            self.stream.write( line )


class StdOutWriter( StreamWriter ):
    """
    Writes to stdout.
    Ignores any Python-specific redirects.
    Ignores binary data.
    """
    
    
    def get_stream( self ):
        return sys.__stdout__


class StdErrWriter( StreamWriter ):
    """
    Writes to stderr.
    Ignores any Python-specific redirects.
    Ignores binary data.
    """
    
    
    def get_stream( self ):
        return sys.__stderr__


orig_stdout = sys.stdout


class TerminalWriter( StreamWriter ):
    """
    Dumps all the data to the terminal.
    This is typically `sys.stdout`, but any Python-specific redirects are followed.
    Ignores binary data.
    """
    
    
    def get_stream( self ):
        return sys.stdout


class OpeningWriter( WriterBase ):
    """
    Writes all data to a temporary file.
    Opens the file in the default GUI when the stream is closed..
    The file itself is queued for delete when the program closes.
    Supports both text and binary data.
    """
    
    
    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        
        if self.type is bytes:
            mode = "wb"
        else:
            mode = "w"
        
        self.file = tempfile.NamedTemporaryFile( mode, delete = False, suffix = self.extension )
        self.name = self.file.name
        io_helper.queue_delete( self.name )
    
    
    def on_write( self, text: str ):
        self.file.write( text )
    
    
    def on_close( self ):
        self.file.close()
        io_helper.system_open( self.name )


class MemoryWriter( BufferedWriter ):
    """
    Writes to RAM.
    For programmatic use only.
    Data can be retrieved via :method:`mhelper.io_helper.MemoryWriter.retrieve`
    Does not support multiple threads.
    Supports both text and binary data.
    """
    __LAST = None
    
    
    @classmethod
    def retrieve( cls ):
        if cls.__LAST is None:
            raise ValueError( "Nothing to retrieve." )
        
        r = "\n".join( cls.__LAST )
        cls.__LAST = None
        return r
    
    
    def on_close( self ):
        type( self ).__LAST = self.lines


class ClipboardWriter( BufferedWriter ):
    """
    Dumps all the data to the clipboard when the stream is closed.
    Supports both text and binary data.
    """
    
    
    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        
        # Test now
        try:
            import pyperclip
        except ImportError as ex:
            raise ValueError( "Cannot use ClipboardWriter without first installing the `pyperclip` package." ) from ex
    
    
    def on_close( self ):
        try:
            import pyperclip
        except ImportError as ex:
            raise ValueError( "Cannot use ClipboardWriter without first installing the `pyperclip` package." ) from ex
        
        if self.type is str:
            pyperclip.copy( "".join( self.lines ) )
        else:
            pyperclip.copy( b"".join( self.lines ) )


class NowhereWriter( WriterBase ):
    """
    Doesn't write anything.
    """


class TargetWriter:
    """
    Opens a file for writing. As opposed to :func:`open`:
        
        * accepts special paths for stdout, the clipboard, etc. (optional)
        * writes through an intermediate file (optional)
        * creates missing directories (optional)
    
    Open the file using `open` and document the mapping using `document`.
    """
    TWriterFactory = Union[Type[WriterBase], Callable[..., WriterBase]]
    TOpenWriteOpts = Dict[str, TWriterFactory]
    
    __fmt = "{}://".format
    default_map: TOpenWriteOpts = { __fmt( "stdout" ): StdOutWriter,
                                    __fmt( "stderr" ): StdErrWriter,
                                    __fmt( "term" )  : TerminalWriter,
                                    __fmt( "clip" )  : ClipboardWriter,
                                    __fmt( "null" )  : NowhereWriter,
                                    __fmt( "open" )  : OpeningWriter,
                                    __fmt( "memory" ): MemoryWriter,
                                    ""               : TerminalWriter }
    
    
    def __init__( self,
                  map: TOpenWriteOpts = None,
                  create: bool = True,
                  use_intermediate: bool = True,
                  allow_files: bool = True,
                  allow_blank: bool = True,
                  metavar: str = "TARGET",
                  wrap: int = 78,
                  no_intermediate_prefix: str = "direct://",
                  intermediate_prefix: str = "indirect://" ):
        """
        :param map:                     Mapping from name to writer factory (see `file_name`:arg:).
                                        If this is `None` then `default_map`:data: is used.
                                        
                                        The name can be any string and is not case sensitive.
                                        An empty name is used if no filename is specified.
                                        
                                        The factory should take parameters matching `WriterBase.__init__`.
                                        
                                        When `unmap`\ping or displaying documentation, the first name in the `dict` for a factory is used as the displayed name.
                                        For this reason, the empty name, if present,. should be specified last.
                                        
        :param create:                  If the directories to this file do not exist, they will
                                        be created if this flag is enabled, otherwise an
                                        error will be raised.
                                        
        :param use_intermediate:        Uses `write_intermediate` instead of `open` when this flag is set.
                                        
        :param allow_files:             Allow regular files to be specified.
        :param allow_blank:             Allow the file name to be blank (the '' item of the map will be used)
        :param metavar:                 Name of the metavariable in the documentation (typically matches the `metavar` of `argparse.ArgumentParser.add_argument`)
        :param wrap:                    Wrapping for the documentation. The default of 78 is the same as `argparse.ArgumentParser`.  
        :param no_intermediate_prefix:  Prefix which can be specified to turn `intermediate` off on a per-file basis (if `intemediate` is `True`).
                                        Blank or `None` disables this feature.
        :param intermediate_prefix:     Prefix which can be specified to turn `intermediate` on on a per-file basis (if `intemediate` is `False`).
                                        Blank or `None` disables this feature.
        """
        if map is None:
            map = self.default_map
        
        self.map = map
        self.create = create
        self.use_intermediate = use_intermediate
        self.allow_files = allow_files
        self.allow_blank = allow_blank
        self.metavar = metavar
        self.wrap = wrap
        self.no_intermediate_prefix = no_intermediate_prefix
        self.intermediate_prefix = intermediate_prefix
    
    
    @property
    def unmap( self ) -> Dict[TWriterFactory,str]:
        """
        `unpap[factory]` unmaps a factory function to its mapping name.
        
        If a factory has multiple names, the *first* item in the `dict` is used
        (assuming `dict`\s are ordered as in CPython).
        """
        return { v: k for k, v in reversed( tuple( self.map.items() ) ) }
    
    
    def open( self, file_name: str, extension: str = "", mode: type = str ) -> Union[WriterBase, TextIO, BinaryIO]:
        """
        Opens a file - see class documentation for details.
        
        :param file_name:     Name of the file *or* one of the special handlers listed
                              in `map`:arg:.
                              `None` is treated the same as `""`.
                              
                              .. note::
                                  
                                  If the name of the file is the same as the the 
                                  handler name (for instance if you have a handler
                                  named "clipboard" but wish to write to a file named
                                  "clipboard" then make sure to include the path of
                                  the file (for instance use './clipboard' instead of
                                  'clipboard'). 
                              
        :param extension:     Extension (file-type) of the file. 
                              This is used by some special handlers, in particular
                              "open", so that the correct application is used to
                              open the file on Windows and modern-Unixes.
                              
        :param mode:          Mode of operation.
                              This should be either `str` or `bytes`.
                            
        
                              
        :return:              A file object (`IO`:class:) *or* a file-like object 
                              (`WriterBase`:class:), which will have the following 
                              methods:
                                  * write
                                  * __enter__, __exit__, close
                                
        :raises ConnectionRefusedError: If a special handler is specified and it cannot be 
                                        initialised due to an error, this error is raised.
        """
        if file_name is None:
            file_name_lower = ""
        else:
            file_name_lower = file_name.lower()
        
        if not self.allow_blank and not file_name:
            raise ValueError( "The file_name cannot be blank." )
        
        mapped: Type[WriterBase] = self.map.get( file_name_lower )
        
        if mapped is not None:
            try:
                return mapped( extension = extension, mode = mode )
            except Exception as ex:
                msg = f"An exception was raised by the writer's constructor for the {file_name!r} ({mapped!r}) writer."
                raise ConnectionRefusedError( msg ) from ex
        
        if not self.allow_files:
            raise ValueError( "The provided file name must denote one of the handlers." )
        
        intermediate = self.use_intermediate
        
        if self.no_intermediate_prefix and file_name.startswith( self.no_intermediate_prefix ):
            intermediate = False
            file_name = file_name[len( self.no_intermediate_prefix ):]
        elif self.intermediate_prefix and file_name.startswith( self.intermediate_prefix ):
            intermediate = True
            file_name = file_name[len( self.intermediate_prefix ):]
        
        file_name = os.path.expanduser( file_name )
        file_name = os.path.abspath( file_name )
        directory_name = file_helper.get_directory( file_name )
        assert directory_name, file_name
        
        if self.create:
            file_helper.create_directory( directory_name )
        
        if intermediate:
            open_fn = io_helper.write_intermediate
        else:
            open_fn = open
        
        if mode is str:
            return open_fn( file_name, "w" )
        elif mode is bytes:
            return open_fn( file_name, "wb" )
        else:
            raise SwitchError( "type_", mode )
    
    
    def document( self ):
        """
        Generates documentation for the `open_write` options.
        """
        from mhelper.utf_table import TextTable, BoxChars
        from mhelper import string_helper, documentation_helper
        
        
        key_prefix = ""
        px = (self.no_intermediate_prefix if self.use_intermediate else self.intermediate_prefix) or ""
        px = (px + "x" if px else "")
        max_key = max( len( x ) + len( key_prefix ) for x in chain( self.map, [px] ) )
        box = BoxChars.BLANK
        cw = (max_key,
              self.wrap - max_key - box.width( 2 ))
        r = TextTable( cw, box = box )
        default = None
        default_key = None
        has_documented = { }
        place_last = []
        
        for name, factory in self.map.items():
            if not name:
                if self.allow_blank:
                    default = factory
                continue
            
            txt = key_prefix + name
            
            if factory in has_documented:
                place_last.append( (txt, f"Alias for {has_documented[factory]}.") )
            else:
                r.add_wrapped( (txt, documentation_helper.get_basic_documentation( factory )) )
            
            has_documented[factory] = name
        
        msg = "When writing to a file an intermediate {} used to avoid the problem of half-written data if the program is terminated during a write. The intermediate is then moved to the intended location when the data is complete. However, this process doesn't work if the target is a special device file, such as /dev/stdout. Specifying this prefix (e.g. {}/dev/stdout) {}."
        
        if self.use_intermediate:
            if self.no_intermediate_prefix:
                r.add_wrapped( (key_prefix + self.no_intermediate_prefix + "x", msg.format( "is", self.no_intermediate_prefix, "writes directly to the specified file (x) instead of using an intermediate" )) )
        else:
            if self.intermediate_prefix:
                r.add_wrapped( (key_prefix + self.no_intermediate_prefix + "x", msg.format( "can be", self.intermediate_prefix, "writes to an intermediate and then moves the file to the final destination after the writing is complete." )) )
        
        for item in place_last:
            r.add_wrapped( item )
        
        if default:
            for name, factory in self.map.items():
                if name and factory == default:
                    default_key = name
                    break
        
        basic = string_helper.wrap( (f"Any filename may be specified as a {self.metavar}. "
                                     "Missing directories are automatically created. "
                                     "Additionally, any of the following may be used:"
                                     if self.allow_files else f"Any of the following may be used as a {self.metavar}:") +
                                    (f" (default={default_key!r})." if default_key else "")
                                    ,
                                    width = self.wrap )
        
        return "\n".join( chain( basic, "\n", r.to_lines() ) )
