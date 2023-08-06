"""
Convenience functions for reading and writing files of different types: text,
pickle, json, etc.
"""
import json
import os
import sys
import platform
import tempfile
import time
import warnings
from typing import Dict, Optional, TextIO, Type, TypeVar, Union, cast, BinaryIO, List, Tuple, Sequence, Iterable
from itertools import count, chain

from mhelper import file_helper
from mhelper.comment_helper import abstract, override, virtual
from mhelper.special_types import NOT_PROVIDED
from mhelper.exception_helper import SwitchError


T = TypeVar( "T" )
U = TypeVar( "U" )
TIniSection = Dict[str, str]
TIniData = Dict[str, TIniSection]


def read_all_text( file_name: str, default: Optional[str] = NOT_PROVIDED, *, details: str = None ) -> Optional[str]:
    """
    Reads all the text from a file, returning None if there is no file
    
    :param file_name: Path to file to read
    :param default:   Default value if file does not exist.
                      If `NOT_PROVIDED` then a `FileNotFoundError` is raised.
    :param details:   Appended to `FileNotFoundError` error message.
    :except FileNotFoundError: File does not exist. 
    """
    if not os.path.isfile( file_name ):
        if default is NOT_PROVIDED:
            raise FileNotFoundError( "Cannot read_all_text from file because the file doesn't exist: «{}».{}".format( file_name, (" Description of file: {}.".format( details )) if details else "" ) )
        
        return default
    
    with open( file_name, "r" ) as file:
        return file.read()


def read_all_lines( file_name: str ) -> List[str]:
    """
    Reads all the text from a file.
    
    :except FileNotFoundError: File not found
    """
    
    if not os.path.isfile( file_name ):
        raise FileNotFoundError( "The file «{}» does not exist.".format( file_name ) )
    
    with open( file_name, "r" ) as file:
        return list( x.rstrip( "\n" ) for x in file )


def write_tsv( file_name: str, matrix: Iterable[Iterable[object]] ) -> None:
    """
    Writes a TSV file.
    """
    with open( file_name, "w" ) as fout:
        for row in matrix:
            for col, cell in enumerate( row ):
                if col != 0:
                    fout.write( "\t" )
                
                fout.write( str( cell ) )
            
            fout.write( "\n" )


def write_all_text( file_name: object, text: Union[Sequence[str], str], newline: bool = False, join: str = "\n" ) -> None:
    """
    Writes all text to a file, overwriting the existing content
    
    .. note::
    
        Alternative:
         
            pathlib.Path( file_name ).write_text( text )
    
    :param file_name:       Target 
    :param text:            Text, or a sequence of lines 
    :param newline:         Adds a newline at the end of the text (if a sequence
                            is provided). 
    :param join:            Character used to join lines (if a sequence is 
                            provided).
    """
    from mhelper import array_helper
    
    if array_helper.is_simple_iterable( text ):
        text = join.join( text )
        
        if newline:
            text += "\n"
    
    with open( str( file_name ), "w" ) as file:
        file.write( text )


def load_npy( file_name ):
    """
    Loads an NPY file. If it is an NPZ this extracts the `data` value automatically.
    Requires the :library:`numpy`.
    """
    # noinspection PyPackageRequirements
    import numpy
    result = numpy.load( file_name, allow_pickle = False, fix_imports = False )
    
    if file_name.upper().endswith( ".NPZ" ):
        result = result["data"]
    
    return result


def load_npz( file_name ):
    """
    Loads an NPZ file and returns the `data` value.
    Requires the :library:`numpy`.
    """
    
    # noinspection PyPackageRequirements
    import numpy
    result = numpy.load( file_name, allow_pickle = False, fix_imports = False )
    result = result["data"]
    
    return result


def save_bitarray( file_name: str, value ) -> None:
    """
    Saves a bit array.
    Requires the :library:`bitarray`.
    
    :type value: bitarray
    
    :param file_name: File name
    :param value: Value to save
    """
    try:
        # noinspection PyPackageRequirements
        from bitarray import bitarray
    except ImportError as ex:
        raise ImportError( "save_bitarray requires the bitarray package." ) from ex
    
    from mhelper import exception_helper, file_helper
    
    exception_helper.assert_instance( "save_bitarray::value", value, bitarray )
    assert isinstance( value, bitarray )
    
    try:
        with open( file_name, "wb" ) as file_out:
            value.tofile( file_out )
    except TypeError:
        # Stupid "open file expected" error on OSX (due to bug writing large files - fallback to manual implementation)
        _save_bytes_manually( file_name, value.tobytes() )
    except Exception as ex:
        raise ValueError( "Failed to write bitarray of length {} to «{}».".format( len( value ), file_name ) ) from ex
    
    size = float( file_helper.file_size( file_name ) )
    expected = len( value )
    
    if size < expected / 8.0:
        raise ValueError( "Saved file is shorter ({} bytes or {} bits) than the originating bitarray ({} bytes or {} bits).".format( size, size * 8, expected / 8, expected ) )


def _save_bytes_manually( file_name: str, value: bytes ):
    """
    Fallback function used by :func:`save_bitarray`.
    """
    warnings.warn( "Save bitarray failed. This is probably due to an error in your `bitarray` library. The file will be saved incrementally but this will take longer.", UserWarning )
    BATCH_SIZE = 100000
    cursor = 0
    length = len( value )
    
    with open( file_name, "wb" ) as file_out:  # note that writing large arrays on OSX is probably the problem, we can't just dump the bytes
        while cursor < length:
            next = min( cursor + BATCH_SIZE, length )
            slice = value[cursor:next]
            file_out.write( slice )
            cursor = next


def _read_bytes_manually( file_name: str ) -> bytes:
    BATCH_SIZE = 100000
    b = bytearray()
    
    with open( file_name, "rb" ) as file_in:
        while True:
            buf = file_in.read( BATCH_SIZE )
            
            if len( buf ) == 0:
                break
            
            b.extend( buf )
    
    return bytes( b )


def load_bitarray( file_name: str ):
    """
    Loads a bitarray
    :param file_name: File to read 
    :return: bitarray. Note this may be padded with missing bits. 
    """
    try:
        # noinspection PyPackageRequirements
        from bitarray import bitarray
    except ImportError as ex:
        raise ImportError( "save_bitarray requires the bitarray package." ) from ex
    
    result = bitarray()
    
    try:
        with open( file_name, 'rb' ) as file_in:
            result.fromfile( file_in )
    except SystemError:  # OSX error
        result = bitarray()
        result.frombytes( _read_bytes_manually( file_name ) )
        assert len( result ) != 0
    
    return result


def save_npy( file_name, value ):
    # noinspection PyPackageRequirements
    import numpy
    
    numpy.save( file_name, value, allow_pickle = False, fix_imports = False )


def save_npz( file_name, value ):
    # noinspection PyPackageRequirements
    import numpy
    
    numpy.savez_compressed( file_name, data = value )


def load_binary( file_name: str,
                 *,
                 type_: Optional[Union[Type[T], Sequence]] = None,
                 default: U = NOT_PROVIDED,
                 delete_on_fail = False,
                 values: int = 0,
                 lock: bool = False,
                 warn: bool = False ) -> Union[T, U]:
    """
    Loads a binary file
    
    :param delete_on_fail:  Show a warning and recycle the file if *any* value
                            cannot be retrieved.
    :param file_name:       Filename to load  
    :param type_:           Type or sequence of type(s) to expect (if `None`
                            then no check is performed).
    :param default:         Default or defaults to use.
                            `NOT_PROVIDED` causes an error to be raised if this
                            value is missing. 
    :param values:          Number of values to deserialise. If this is non-zero
                            then the result will be a list. This does not need
                            to be specified if `type_` is a sequence.
    :param lock:            Lock the file for read/write during the loading.
                            
    :return: Loaded data, or a sequence of loaded data. 
    """
    
    if isinstance( type_, list ) or isinstance( type_, tuple ):
        types = type_
        
        if values == 0:
            values = len( types )
        
        one = False
    elif values:
        types = [type_] * values
        one = False
    else:
        values = 1
        types = [type_]
        one = True
    
    assert values == len( types )
    
    if not isinstance( default, list ) and not isinstance( default, tuple ):
        default = [default] * values
    
    import pickle
    
    result = []
    
    delete_ex = None
    
    try:
        with with_lock( open( file_name, "rb" ), _enabled = lock ) as file:
            for item_index, item_type, item_default in zip( count(), types, default ):
                try:
                    item_value = pickle.load( file, fix_imports = False )
                    
                    if item_type is not None:
                        assert isinstance( item_type, type )
                        
                        if not isinstance( item_value, item_type ):
                            raise ValueError( "Deserialised object #{} from file «{}» was expected to be of type «{}» but it's not, its of type «{}» with a value of «{}».".format( item_index, file_name, item_type, type( result ), result ) )
                except Exception as ex:
                    if warn:
                        warnings.warn( f"Deserialisation error: {ex}.", UserWarning )
                    
                    if delete_on_fail:
                        delete_ex = ex
                    
                    if item_default is NOT_PROVIDED:
                        raise
                    
                    item_value = item_default
                
                result.append( item_value )
            if one:
                result = next( iter( result ) )
            
            return result
    except Exception as ex:
        if delete_on_fail:
            delete_ex = ex
        
        if one:
            r = next( iter( default ) )
            if r is NOT_PROVIDED:
                raise
            return r
        else:
            if any( x is NOT_PROVIDED for x in default ):
                raise
            
            return default
    finally:
        if delete_ex is not None:
            file_helper.recycle_file( file_name )
            warnings.warn( "\n"
                           "************************************************************\n"
                           "* Failed to load binary file due to an error:              *\n"
                           "************************************************************\n"
                           "* This is probably due to a version incompatibility        *\n"
                           "* You may need to recreate this file.                      *\n"
                           "* The problematic file has been sent to the recycle bin.   *\n"
                           "* If it is important, please retrieve it now.              *\n"
                           "************************************************************\n"
                           "* Error: {} : {}\n"
                           "* File : {}\n"
                           .format( type( delete_ex ).__name__, delete_ex, file_name ), UserWarning )


def save_binary( file_name: Optional[str], value = None, *, values = None, lock = False ) -> Optional[bytes]:
    """
    Saves a binary file.
        
    :param file_name:       Target file. If this is `None` the bytes are returned instead of being
                            saved.
    :param value:           Value to store 
    :param values:          Alternative to `value` that. This should be a list or tuple indicating 
                            a series of values to store sequentially. 
    :param lock:            Lock the file for read/write during the save.
    :return:                Bytes if `file_name` is `None`, else `None`.
    """
    import pickle
    
    if values is None:
        values = [value]
    elif value is not None:
        raise ValueError( "Cannot specify both `value` and `values`." )
    
    if file_name is None:
        try:
            return pickle.dumps( value, protocol = -1, fix_imports = False )
        except Exception as ex:
            raise IOError( "Error saving data to bytes. Data = «{}».".format( value ) ) from ex
    
    with with_lock( open( file_name, "wb" ), _enabled = lock ) as file:
        for value in values:
            try:
                pickle.dump( value, file, protocol = -1, fix_imports = False )
            except Exception as ex:
                raise IOError( "Error saving data to binary file. Filename = «{}». Data = «{}».".format( file_name, value ) ) from ex
    
    return None


def with_lock( handle, _enabled = True ):
    from mhelper.disposal_helper import ManagedWith
    
    if _enabled:
        return ManagedWith( handle, on_enter = lambda _: _lock( handle ), on_exit = lambda _: _unlock( handle ) )
    else:
        return ManagedWith( handle )


_lock_warning = True


def _lock( handle ):
    import fcntl, errno
    
    while True:
        try:
            fcntl.flock( handle, fcntl.LOCK_EX | fcntl.LOCK_NB )
            break
        except IOError as e:
            # raise on unrelated IOErrors
            if e.errno != errno.EAGAIN:
                raise
            else:
                global _lock_warning
                
                if _lock_warning:
                    warnings.warn( "Failed to obtain file lock '{}'. Trying again in 0.1s.".format( handle.name ), UserWarning )
                    _lock_warning = False
                
                time.sleep( 0.1 )


def _unlock( handle ):
    import fcntl
    fcntl.flock( handle, fcntl.LOCK_UN )


def load_json_data( file_name ):
    import json
    
    with open( file_name, "r" ) as file_in:
        return json.load( file_in )


def save_json_data( file_name, value, pretty = False ):
    import json
    
    with open( file_name, "w" ) as file_out:
        if pretty:
            return json.dump( value, file_out, indent = 4 )
        else:
            return json.dump( value, file_out, separators = (',', ':') )


def load_json_pickle( file_name, keys = True, default = NOT_PROVIDED ):
    from mhelper.file_helper import read_all_text
    import jsonpickle
    
    if default is not NOT_PROVIDED and not os.path.isfile( file_name ):
        return default
    
    text = read_all_text( file_name )
    
    return jsonpickle.decode( text, keys = keys )


def save_json_pickle( file_name, value, keys = True ):
    from mhelper.file_helper import write_all_text
    import jsonpickle
    
    write_all_text( file_name, jsonpickle.encode( value, keys = keys ) )


def default_values( target: T, default: Optional[Union[T, type]] = None ) -> T:
    if default is None:
        if target is None:
            raise ValueError( "Cannot set the defaults for the value because both the value and the defaults are `None`, so neither can be inferred." )
        
        default = type( target )
    
    if isinstance( default, type ):
        default = default()
    
    if target is None:
        return default
    
    if isinstance( target, list ):
        # noinspection PyTypeChecker
        return cast( T, target )
    
    if type( target ) is not type( default ):
        raise ValueError( "Attempting to set the defaults for the value «{}», of type «{}», but the value provided, «{}», of type «{}», is not compatible with this.".format( target, type( target ), default, type( default ) ) )
    
    added = []
    replaced = []
    removed = []
    
    for k, v in default.__dict__.items():
        if k.startswith( "_" ):
            continue
        
        if k not in target.__dict__:
            added.append( k )
            target.__dict__[k] = v
        elif type( target.__dict__[k] ) != type( v ):
            replaced.append( k )
            target.__dict__[k] = v
    
    to_delete = []
    
    for k in target.__dict__.keys():
        if k not in default.__dict__:
            to_delete.append( k )
    
    for k in to_delete:
        removed.append( k )
        del target.__dict__[k]
    
    return target


def open_write_doc( map = None, wrap = 78, allow_files: bool = True, allow_blank: bool = True, *, metavar: str = "TARGET" ):
    warnings.warn( "Deprecated - use output_helper.TargetWriter.document", DeprecationWarning )
    from mhelper import output_helper
    return output_helper.TargetWriter( map = map, wrap = wrap, allow_files = allow_files, allow_blank = allow_blank, metavar = metavar ).document()


def open_write( file_name: str,
                extension: str = "",
                mode: type = str,
                map = None,
                create: bool = True,
                intermediate: bool = True,
                allow_files: bool = True,
                allow_blank: bool = True ):
    warnings.warn( "Deprecated - use output_helper.TargetWriter.open", DeprecationWarning )
    from mhelper import output_helper
    return output_helper.TargetWriter( map = map, create = create, use_intermediate = intermediate, allow_files = allow_files, allow_blank = allow_blank ).open( file_name = file_name, extension = extension, mode = mode )


def load_ini( file_name: str, comments: str = (";", "#", "//"), stop: Tuple[str, str] = None ) -> Dict[str, Dict[str, str]]:
    """
    Loads an INI file.
    
    :param stop:            When this section and key are encountered, reading the INI stops with
                            whatever has been loaded so far.
    :param file_name:       File to load 
    :param comments:        Comment lines 
    :return:                INI data:
                                str - Section name ("" contains the data from any untitled section or sections with no name `[]`)
                                dict - Section data:
                                    str - Field key
                                    str - field value
    """
    
    with open( file_name, "r" ) as fin:
        return load_ini_str( fin,
                             comments,
                             stop )


def load_ini_str( fin: Union[str, Iterable[str]], comments: str = (";", "#", "//"), stop: Tuple[str, str] = None ) -> Dict[str, Dict[str, str]]:
    if isinstance( fin, str ):
        fin = fin.split( "\n" )
    
    r = { }
    unsectioned = { }
    section = unsectioned
    section_name = ""
    
    for line in fin:
        line = line.strip()
        
        if any( line.startswith( x ) for x in comments ):
            continue
        
        if line.startswith( "[" ) and line.endswith( "]" ):
            section = { }
            section_name = line[1:-1]
            r[section_name] = section
        elif "=" in line:
            k, v = line.split( "=", 1 )
            section[k.strip()] = v.strip()
            
            if stop is not None and stop[0] == section_name and stop[1] == k:
                break
    
    if unsectioned:
        if "" in r:
            unsectioned.update( r[""] )
        
        r[""] = unsectioned
    
    return r


def save_ini( file_name: str, data: Dict[str, Dict[str, str]] ) -> None:
    with open( file_name, "w" ) as file:
        if "" in data:
            __write_ini_section( data[""], file )
        
        for section, fields in data.items():
            if section:
                file.write( "[{}]\n".format( section ) )
                __write_ini_section( fields, file )


def __write_ini_section( fields, file ):
    for name, value in fields.items():
        file.write( "{}={}\n".format( name, value ) )
    file.write( "\n" )


class queue_delete:
    """
    The file will be deleted when the program closes.
    
    If the program force-closes then the file is not deleted.
    
    :remarks:           Class masquerading as function.
                        
                        Example usage:
                            ```
                            queue_delete( "c:\my_temporary_file.txt" )
                            ```    
    
    :cvar queued:       Gets the list of files to be deleted.
                        Acts to keep the references alive until the program closes.
    :ivar file_name:    Name of the file
    """
    
    queued = []
    
    
    def __init__( self, file_name: str ) -> None:
        """
        CONSTRUCTOR
        Automatically adds the reference to the queue, keeping it alive
        until the program closes.
        
        :param file_name: Name of the file
        """
        self.file_name = file_name
        self.queued.append( self )
    
    
    def __del__( self ) -> None:
        """
        !OVERRIDE
        On deletion, removes the file.
        """
        os.remove( self.file_name )


class with_temporary:
    """
    The file will be deleted when the with block ends
    """
    
    
    def __init__( self, file_name: str = None, *, condition: bool = True ):
        """
        Names a file that is deleted when the with block ends.
        
        :param file_name:   A filename (not starting `.`), an extension of a new temporary file (starting `.`), or `None`, for an extension-less temporary file. 
        """
        if not file_name or file_name.startswith( "." ):
            file_name = tempfile.NamedTemporaryFile( "w", delete = False, suffix = file_name ).name
        
        self.file_name = file_name
        self.condition = condition
    
    
    def __enter__( self ):
        """
        `with` returns the filename.
        """
        return self.file_name
    
    
    def __exit__( self, exc_type, exc_val, exc_tb ):
        """
        End of `with` deletes the file.
        """
        if self.condition:
            try:
                os.remove( self.file_name )
            except FileNotFoundError as ex:
                raise FileNotFoundError( "Failed to delete file '{}'.".format( self.file_name ) ) from ex


with_delete = with_temporary


class ESystem:
    UNKNOWN = 0
    WINDOWS = 1
    MAC = 2
    LINUX = 3


def get_system():
    s = platform.system()
    if s == "Windows":
        return ESystem.WINDOWS
    elif s == "Darwin":
        return ESystem.MAC
    elif s == "Linux":
        return ESystem.LINUX
    else:
        return ESystem.UNKNOWN


def system_open( file_name: str ):
    """
    Opens the file with the default editor.
    (Only works on Windows, Mac and GUI GNU/Linuxes)
    """
    s = platform.system()
    if s == "Windows":
        os.system( file_name )
    elif s == "Darwin":
        os.system( "open \"" + file_name + "\"" )
    elif s == "Linux":
        os.system( "xdg-open \"" + file_name + "\"" )
    else:
        warnings.warn( "I don't know how to open files with the default editor on your platform '{}'.".format( s ) )


def system_select( file_name: str ):
    """
    Selects the file with the default file explorer.
    (Only works on Windows, Mac and GUI Linuxes)
    """
    s = platform.system()
    if s == "Windows":
        os.system( "explorer.exe /select,\"{}\"".format( file_name ) )
    elif s == "Darwin":
        os.system( "open -R \"{}\"".format( file_name ) )
    elif s == "Linux":
        # Just open the parent directory on Linux
        file_name = os.path.split( file_name )[0]
        os.system( "xdg-open \"{}\"".format( file_name ) )
    else:
        warnings.warn( "I don't know how to open files with the default editor on your platform '{}'.".format( s ) )


def hash_file( file_name: str, algorithm = "sha256" ) -> str:
    import hashlib
    sha1 = getattr( hashlib, algorithm )()
    BUF_SIZE = 10000
    
    with open( file_name, 'rb' ) as f:
        while True:
            data = f.read( BUF_SIZE )
            if not data:
                break
            sha1.update( data )
    
    return sha1.hexdigest()


def system_cls():
    """
    Clears the terminal display.
    
    .. note::
    
        The proper way is to send the correct ANSI sequence, however in practice this produces odd results.
        So we just use the specific system commands.
        Note that we send two ``clear``s for Unix - once doesn't fully clear the display. 
    """
    if sys.platform.lower() == "windows":
        os.system( "cls" )
    else:
        os.system( "clear ; clear" )


def ungzip( in_file_name, out_file_name = None ):
    """
    Un-Gzips a file.
    
    :param in_file_name:    Input file. This is not deleted. 
    :param out_file_name:   Output file. If `None` then `in_file_name` is used, minus its `.gz` extension. 
    :return:                Output file name. 
    """
    if out_file_name is None:
        if file_helper.get_extension( in_file_name ).lower() != ".gz":
            raise ValueError( "Cannot generate the out_file_name from an in_file_name ('{}') not ending in '.gz'.".format( in_file_name ) )
        
        out_file_name = file_helper.get_full_filename_without_extension( in_file_name )
    
    import gzip
    import shutil
    with gzip.open( in_file_name, "rb" ) as f_in:
        with open( out_file_name, "wb" ) as f_out:
            shutil.copyfileobj( f_in, f_out )
    
    return out_file_name


class EnumJsonEncoder( json.JSONEncoder ):
    """
    Json encoder supporting enums (written as strings)::
    
        "EnumName::EnumValue"
    
    Note that, during decoding, strings that look like enums will be converted
    into enums, that is::
    
        "EnumName::*"
        
    For any ``EnumName`` in the `supported_enums`.
    If ``*`` cannot be found in the values of that enum, an error is raised. 
    """
    
    
    def __init__( self, *args, supported_enums, **kwargs ):
        super().__init__( *args, **kwargs )
        self.supported = set( supported_enums )
    
    
    def default( self, o ):
        if type( o ) in self.supported:
            return f"{type( o ).__name__}::{o.name}"
        
        return super().default( o )


class EnumJsonDecoder( json.JSONDecoder ):
    """
    Counterpart of `EnumJsonEncoder`.
    """
    
    
    def __init__( self, *args, supported_enums, **kwargs ):
        super().__init__( *args, object_hook = self.__object_hook, **kwargs )
        self.supported = { klass.__name__: klass for klass in supported_enums }
    
    
    def __object_hook( self, s ):
        u = { }
        
        for k, v in s.items():
            if isinstance( v, str ) and "::" in v:
                klass_n, name = v.split( "::", 1 )
                klass = self.supported.get( klass_n )
                
                if klass is not None:
                    u[k] = klass[name]
        
        s.update( u )
        
        return s


# region Deprecated

def load_json( file_name, keys = True, default = NOT_PROVIDED ):
    warnings.warn( "Ambiguous - use load_json_data or `load_json_pickle`", DeprecationWarning )
    return load_json_pickle( file_name, keys = keys, default = default )


def save_json( file_name, value, keys = True ):
    warnings.warn( "Ambiguous - use save_json_data or `save_json_pickle`", DeprecationWarning )
    return save_json_pickle( file_name, value, keys = keys )


# endregion

def iter_file_lines( fin ):
    """
    Like `iter(FileIO)` (i.e. `FileIO.__next__`), but doesn't disable 
    `FileIO.tell`.
    """
    while True:
        line = fin.readline()
        
        if not line:
            break
        
        yield line


def get_temporary_file( extension = ".tmp" ):
    file = tempfile.NamedTemporaryFile( "w", delete = False, suffix = extension )
    file.close()
    name = file.name
    queue_delete( name )
    return name


class write_intermediate:
    """
    Opens a temporary file for writing.
    When closed, the temporary file is renamed to the target.
    This avoids the problem where a program closes before it completes its
    output, leaving the user (or another program) unsure if the output file
    is complete or partial.
    
    Usage is the same as `open` (though note that writing through an
    intermediate implicitly prevents read/append modes).
    
    Unlike `open`, instances of this class enforce enter/exit semantics.
    """
    __slots__ = "__file_name", "__mode", "__i_file_name", "__handle", "__stage"
    
    
    def __init__( self, file_name, mode = "w" ):
        self.__file_name = file_name
        self.__mode = mode
        self.__i_file_name = self.__file_name + ".~intermediate"
        self.__handle = None
        self.__stage = 0
    
    
    def __enter__( self ):
        assert self.__stage == 0
        self.__stage = 1
        self.__handle = open( self.__i_file_name, self.__mode )
        return self.__handle.__enter__()
    
    
    def __exit__( self, exc_type, exc_val, exc_tb ):
        assert self.__stage == 1
        self.__handle.__exit__( exc_type, exc_val, exc_tb )
        os.rename( self.__i_file_name, self.__file_name )
        self.__stage = 2
