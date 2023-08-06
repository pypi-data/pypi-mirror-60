"""
Logging helpers.

Includes:

* A logging handler that formats for the terminal, including thread and process information.
* A logger which highlights variadic values, contains helpers for dealing with progress bars, iteration, enumeration and timing.
* A function to iterate information on existing loggers.
"""
import pickle
import logging.handlers
import socketserver
import json
import socket, struct
import logging.handlers
import logging.config
import warnings

from mhelper import exception_helper
import functools
import logging
import os
import sys
import time
import threading
from typing import Union, Iterable, TypeVar, Iterator, List, Optional, Callable
from mhelper import ansi, string_helper, progress_helper, disposal_helper


T = TypeVar( "T" )


class ConsoleHandler( logging.Handler ):
    """
    A logging handler that formats for the terminal and displays thread and
    process information.
    
    There are several class variables which control behaviour. These may also
    be set at instance scope.
    
    :cvar show_name:        Include logger name
    :cvar show_processes:   Include logger process
    :cvar show_threads:     Include logger threads
    :cvar target:           Where to write text to (any callable).
                            See `DefaultTarget` and `AltScreenTarget`. 
    """
    
    show_name: bool = True
    show_processes: bool = True
    show_threads: bool = True
    
    __FG_COLOURS = [ansi.FR,
                    ansi.FG,
                    ansi.FB,
                    ansi.FC,
                    ansi.FY,
                    ansi.FM,
                    ansi.FW,
                    ansi.FK,
                    ansi.FBR,
                    ansi.FBG,
                    ansi.FBB,
                    ansi.FBC,
                    ansi.FBY,
                    ansi.FBM,
                    ansi.FBW,
                    ansi.FBK]
    __BG_COLOURS = [ansi.BR,
                    ansi.BG,
                    ansi.BB,
                    ansi.BC,
                    ansi.BY,
                    ansi.BM,
                    ansi.BW,
                    ansi.BK,
                    ansi.BBR,
                    ansi.BBG,
                    ansi.BBB,
                    ansi.BBC,
                    ansi.BBY,
                    ansi.BBM,
                    ansi.BBW,
                    ansi.BBK]
    
    
    class DefaultTarget:
        """
        Writes to a function (target).
        By default this writes to stderr.
        """
        target: Callable[[str], None] = sys.stderr.write
        
        
        def __call__( self, x ):
            self.target( x )
    
    
    class AltScreenTarget:
        """
        A variation of `DefaultTarget` that is designed for logging when a
        alternate ANSI screen is visible.
        
        This works by switching to the primary ANSI screen to write output,
        then switching back to the alternate ANSI screen.
        
        Note::
        
            * This will cause some flickering on the alternate screen.
            * The target must be disengaged when resuming the regular screen.
            * Raw mode is assumed to be active, and carriage returns are
              inserted into the logs.
        """
        target: Callable[[str], None] = None
        
        
        def __call__( self, x ):
            x = x.replace( "\n", "\r\n" )
            x = f"{ansi.ALTERNATE_SCREEN_OFF}{x}{ansi.ALTERNATE_SCREEN}"
            self.target( x )
    
    
    default_target: Callable[[str], None] = DefaultTarget()
    AltScreenTarget.target = default_target
    target: Callable[[str], None] = default_target
    
    
    def __repr__( self ):
        return "{}('{}')".format( "log_helper.Handler", self.name )
    
    
    def __str__( self ):
        return self.name
    
    
    def __init__( self,
                  name,
                  *,
                  show_processes = None,
                  target = None,
                  show_threads = None,
                  show_name = None,
                  minimal = False ):
        """
        :param name:                Name of the log
        :param show_processes:      Show the process sidebar.
                                    Overrides the Handler cvar if provided. 
        :param target:              Where to send the output.
                                    Overrides the Handler cvar if provided.
        :param show_threads:        Show the thread sidebar.
                                    Overrides the Handler cvar if provided. 
        :param show_name:           Show the name sidebar.
                                    Overrides the Handler cvar if provided.
        :param minimal:             When `True`, overrides the Handler cvars `show_processes`, `show_threads` and `show_name`.
        """
        super().__init__()
        
        if isinstance( name, Logger ):
            self.logger = name
            name = name.name
        else:
            self.logger = None
        
        self.name = name
        
        if "." in name:
            name = ".".join( name.rsplit( ".", 2 )[-2:] )
        
        if minimal:
            self.show_processes = False
            self.show_threads = False
            self.show_name = False
        
        if show_name is not None:
            self.show_name = show_name
        
        if show_processes is not None:
            self.show_processes = show_processes
        
        if target is not None:
            self.target = target
        
        if show_threads is not None:
            self.show_threads = show_threads
        
        c1 = hash( name ) % len( self.__FG_COLOURS )
        c2 = hash( name * 2 ) % len( self.__BG_COLOURS )
        
        if c2 == c1:
            c2 = (c1 + 1) % len( self.__FG_COLOURS )
        
        sigil_1 = self.__FG_COLOURS[c1]
        sigil_2 = self.__BG_COLOURS[c2]
        self.sigil_n = sigil_1 + sigil_2 + " {} ".format( string_helper.fix_width( name, 15 ) ) + ansi.RESET + " " + ansi.FORE_CYAN + " "
        self.sigil_0 = sigil_1 + sigil_2 + " {} ".format( string_helper.fix_width( "''", 15 ) ) + ansi.RESET + " " + ansi.FORE_CYAN + " "
    
    
    def fake( self, level, message ):
        self.emit( logging.LogRecord( self.name, 30, "", level, message, (), None ) )
    
    
    def emit( self, record: logging.LogRecord ):
        if self.show_name:
            sigil_n = self.sigil_n
            sigil_0 = self.sigil_0
        else:
            sigil_n = ""
            sigil_0 = ""
        
        fw = string_helper.fix_width
        text = record.getMessage()
        text = string_helper.highlight_quotes( text, "«", "»", ansi.FORE_YELLOW, ansi.FORE_GREEN )
        thread_name = record.threadName
        
        #
        # Thread
        #
        if not self.show_threads:
            thread = ""
        elif thread_name == "MainThread":
            thread = ""
        elif thread_name.startswith( "Thread-" ) and thread_name[7:].isdigit():
            thread = ansi.BACK_BLUE + ansi.FORE_WHITE + " {} ".format( fw( thread_name[7:].strip(), 3 ) ) + ansi.RESET
        else:
            thread = ansi.BACK_BLUE + ansi.FORE_WHITE + " {} ".format( fw( thread_name, 15 ) ) + ansi.RESET
        
        #
        # Process
        #
        pid = record.process
        
        if self.show_processes:
            process = ansi.BACK_BLUE + ansi.FORE_BRIGHT_BLUE + " {} ".format( fw( str( pid ), 8 ) ) + ansi.RESET
        else:
            process = ""
        
        sigil = sigil_n
        
        text = text.split( "\n" )
        
        for tex in text:
            tex = ansi.FORE_GREEN + "{}{}{}{}\n".format( process, thread, sigil, tex ) + ansi.FORE_RESET
            self.target( tex )
            
            sigil = sigil_0
            process = process and ansi.BACK_BLUE + ansi.FORE_BRIGHT_BLUE + " {} ".format( fw( "''", 8 ) ) + ansi.RESET
            thread = thread and ansi.BACK_BLUE + ansi.FORE_WHITE + " {} ".format( fw( "'' ", 3 ) ) + ansi.RESET


class LogCollection:
    pending = []
    
    
    @staticmethod
    def start():
        LogConsole.start()
        LogServer.start()
    
    
    @staticmethod
    def register( condition: bool, handler: logging.Handler ) -> None:
        """
        Adds `handler` to any loggers with a `Logger.enabled_hint`.
        
        `Logger`\s created *after* this call will also have the handler added
        (see `register_pending`). 
              
        See `LogCollection.register`.
        
        :param condition:   Condition.  
        :param handler:     Handler to register. 
        """
        if not condition:
            return
        
        LogCollection.pending.append( handler )
        
        for mh_logger in LogCollection.list_enabled():
            assert isinstance( mh_logger, Logger )
            LogCollection.__register( handler, mh_logger )
        
        _primary_log( "Directing logging to {}", handler )
    
    
    @staticmethod
    def list_enabled() -> List["Logger"]:
        return [logger.mh_logger for logger in LogCollection.list_loggers() if logger.mh_logger is not None and logger.mh_logger.enabled_hint]
    
    
    @staticmethod
    def list_loggers() -> List["LoggerInfo"]:
        """
        Iterates all the loggers, returning a `LoggerInfo` for each one.
        """
        # The logging manager is here (it has no stub so use `getattr`)
        manager = getattr( logging.Logger, "manager" )
        
        r = []
        
        for name, logger in manager.loggerDict.items():
            if not isinstance( logger, logging.Logger ):
                # Ignore placeholders
                continue
            
            if isinstance( logger, logging.Logger ):
                registered = Logger.registered.get( name )
            else:
                registered = None
            
            r.append( LoggerInfo( name,
                                  logger,
                                  logging.getLevelName( logger.level ) if hasattr( logger, "level" ) else None,
                                  logger.level if hasattr( logger, "level" ) else None,
                                  logger.handlers if hasattr( logger, "handlers" ) else None,
                                  registered.comment if registered is not None else None,
                                  registered ) )
        
        return r
    
    
    @staticmethod
    def __register( handler, mh_logger: "Logger" ) -> None:
        assert isinstance( mh_logger, Logger )
        mh_logger.enabled = True
        mh_logger.logger.addHandler( handler )
    
    
    @staticmethod
    def register_pending( mh_logger: "Logger" ) -> None:
        """
        Ensures loggers added after `register` still have the handler added.
        """
        assert isinstance( mh_logger, Logger )
        
        if mh_logger.enabled_hint:
            for handler in LogCollection.pending:
                LogCollection.__register( handler, mh_logger )


class LogConsole( logging.Handler ):
    __slots__ = ["map"]
    
    
    def __repr__( self ):
        return "LogConsole()"
    
    
    @staticmethod
    def start( register = True ):
        """
        :param register:    Add handlers for any loggers with a `Logger.enabled_hint`.      
                            See `LogCollection.register`.
        """
        LogCollection.register( register, LogConsole() )
    
    
    def __init__( self ):
        super().__init__()
        
        self.map = { }
    
    
    def emit( self, record: logging.LogRecord ):
        handler = self.map.get( record.name )
        
        if not handler:
            handler = ConsoleHandler( record.name )
            self.map[record.name] = handler
        
        return handler.emit( record )


class Logger:
    """
    Logging simplified.
    
    This just wraps `logging.Logger`, but provides some nice features such as progress bars, timers,
    etc.
    
    Default logging preferences can also be specified, which are enacted if logging is enabled for
    a terminal, TCP client, etc.
    
    All messages are logged at the same level.
    
    Usage::
    
        log = Logger( "my logger", True )
        log( "hello {}", x )
        
    :cvar __k_indent_size:     Size of indentation for text formatting.
    :cvar level:               For simplicity, we use a fixed logger level. This is it.
    :cvar registered:          List of `Logger`\s that have been created, mapped by name.
    :ivar _true_logger:       Pointer to underlying logger.
    :ivar __indent:            Indentation level we are at.
    :ivar comment:             Comment describing what the logger is for.
    :ivar enabled_hint:        Our preference for being enabled.
                               This is a hint only and does not affect whether the logger is actually
                               enabled.
                               It can be used by a new listener collection, such as `LogServer` or
                               `LogConsole`, to decide which loggers should be handled by default.
    """
    __k_indent_size = 4
    level: int = logging.INFO
    registered = { }
    __slots__ = "logger", "__indent", "enabled_hint", "comment"
    
    
    def __init__( self,
                  name: str,
                  enabled: Union[bool, str] = False,
                  comment: str = "" ):
        """
        :param name:        Name of the underlying logger.  
        :param enabled:     See :ivar:`prefer_enabled`.  
        :param comment:     A description of the logger, for reference only. 
        """
        assert name
        Logger.registered[name] = self
        self.logger = logging.getLogger( name )
        self.__indent = 0
        self.comment = comment
        self.enabled_hint = enabled
        LogCollection.register_pending( self )
    
    
    @property
    def name( self ) -> str:
        """
        Name of the underlying logger.
        """
        return self.logger.name
    
    
    def __bool__( self ) -> bool:
        """
        Our boolean flag denotes if we are enabled (for our fixed level).
        """
        return self.enabled
    
    
    @property
    def enabled( self ) -> bool:
        """
        Gets or sets whether the underlying logger is enabled (for our fixed level).
        """
        return self.logger.isEnabledFor( self.level )
    
    
    @enabled.setter
    def enabled( self, value: bool ) -> None:
        if value:
            self.logger.setLevel( self.level )
        else:
            self.logger.setLevel( logging.NOTSET )
    
    
    def __call__( self, *args, **kwargs ) -> "Logger":
        """
        Logs text.
        """
        if self.enabled:
            self.print( self.format( *args, *kwargs ) )
        
        return self
    
    
    def format( self, *args, **kwargs ) -> str:
        """
        Formats text for output.
        """
        if len( args ) == 1:
            r = str( args[0] )
        elif len( args ) > 1:
            vals = list( args[1:] )
            for i in range( len( vals ) ):
                v = vals[i]
                
                if type( v ) in (set, list, tuple, frozenset):
                    v = string_helper.array_to_string( v, **kwargs )
                
                vals[i] = "«" + str( v ) + "»"
            
            r = args[0].format( *vals )
        else:
            r = ""
        
        indent = " " * (self.__indent * self.__k_indent_size)
        return indent + r.replace( "\n", "\n" + indent )
    
    
    class defer:
        """
        Allows a function passed via format to lazily load its string representation.
        """
        
        
        def __init__( self, fn ):
            self.fn = fn
        
        
        def __repr__( self ):
            return self.fn()
    
    
    def print( self, message: str ) -> None:
        """
        Directly sends `message` to the underlying logger.
        """
        self.logger.log( self.level, message )
    
    
    @property
    def indent( self ) -> int:
        return self.__indent
    
    
    @indent.setter
    def indent( self, level: int ) -> None:
        assert isinstance( level, int )
        self.__indent = level
    
    
    def __enter__( self ) -> None:
        """
        Indents the logger.
        
        Since `self` is returned from `__call__`, both `with log:` and
        `with log("spam"):` are permissible.
        """
        self.indent += 1
    
    
    def __exit__( self, exc_type, exc_val, exc_tb ) -> None:
        """
        Un-indents the logger.
        """
        self.indent -= 1
    
    
    def time( self, title, indent = True ):
        """
        Logs the time taken for the `with` block::
        
            with log.time():
                ...
        """
        return _Time( self, title, indent )
    
    
    def timed( self, old_fn: Callable ) -> Callable:
        @functools.wraps( old_fn )
        def new_fn( *args, **kwargs ):
            with self.time( old_fn.__name__ ):
                return old_fn( *args, **kwargs )
        
        
        return new_fn
    
    
    def attach( self, fn = None ):
        """
        Logs when a function is called.
        """
        
        
        def dec( fn ):
            def ret( *args, **kwargs ):
                self( "@{}", fn.__name__ )
                
                with self:
                    return fn( *args, **kwargs )
            
            
            return ret
        
        
        if fn:
            return dec( fn )
        else:
            return dec
    
    
    def enumerate( self, *args, **kwargs ):
        """
        Logs the iterations of an `enumerate`.
        See `iterate`.
        """
        return enumerate( self.iterate( *args, **kwargs ) )
    
    
    def action( self,
                title = None,
                total: Optional[int] = None,
                *,
                period: float = None,
                item: str = "record",
                text: Optional[str] = None ):
        """
        Designates a region as an activity, indenting the logger and providing
        optional progress reports.
        
        Usage::
        
            with logger.action(. . .) as action:
                action.xxx()
                . . . 
        
        :param title:   Passed to `ProgressMaker`. 
        :param total:   Passed to `ProgressMaker`.
        :param period:  Passed to `ProgressMaker`. 
        :param item:    Passed to `ProgressMaker`. 
        :param text:    Passed to `ProgressMaker`. 
        :return:        ``with`` block.
        """
        pm = progress_helper.ProgressMaker( title = title,
                                            total = total,
                                            issue = self.__action_iterate,
                                            period = period,
                                            item = item,
                                            text = text )
        
        return disposal_helper.ManagedWith( target = pm,
                                            on_exit = self.__action_exit,
                                            on_enter = self.__action_enter )
    
    
    def __action_iterate( self, x: progress_helper.Progress ):
        self( x )
    
    
    def __action_enter( self, action: progress_helper.ProgressMaker ):
        action.begin()
        self.indent += 1
    
    
    def __action_exit( self, action: progress_helper.ProgressMaker ):
        self.indent -= 1
        action.complete()
    
    
    def iterate( self,
                 records: Iterable[T],
                 count = None,
                 *,
                 title = None,
                 period: float = None,
                 item: str = "record",
                 text: Optional[str] = None ) -> Iterator[T]:
        """
        Logs the iterations.
        
        :param records:     Iterable. 
        :param count:       See `progress_helper.ProgressMaker`.
        :param title:       See `progress_helper.ProgressMaker`.
        :param period:      See `progress_helper.ProgressMaker`.
        :param item:        See `progress_helper.ProgressMaker`.
        :param text:        See `progress_helper.ProgressMaker`.
        :return:            Iterator over `records` that logs the iterator's progress. 
        """
        if not self:
            for record in records:
                yield record
        else:
            if count is None:
                try:
                    # noinspection PyTypeChecker
                    count = len( records )
                except Exception:
                    count = None
            
            with self.action( total = count,
                              title = title,
                              period = period,
                              item = item,
                              text = text ) as action:
                for current, record in enumerate( records ):
                    action.report( current )
                    yield record


class _Time:
    __slots__ = "logger", "name", "indent", "start"
    
    
    def __init__( self, logger, name, indent ):
        self.logger = logger
        self.name = name
        self.indent = indent
        self.start = None
    
    
    def __enter__( self ):
        self.start = time.perf_counter()
        if self.indent:
            self.logger( "{} - {}".format( self.name, "...please wait..." ) )
            self.logger.indent += 1
        return self
    
    
    @property
    def now( self ):
        if self.start is None:
            raise RuntimeError( "Timer not started." )
        
        return time.perf_counter() - self.start
    
    
    def __exit__( self, exc_type, exc_val, exc_tb ):
        elapsed = time.perf_counter() - self.start
        if self.indent:
            self.logger( "{} - ...completed in {{}}.".format( self.name ), string_helper.timedelta_to_string( elapsed, hz = True ) )
            self.logger.indent -= 1
        else:
            self.logger( "{} - completed in {{}}.".format( self.name ), string_helper.timedelta_to_string( elapsed, hz = True ) )


class LoggerInfo:
    __slots__ = "name", "logger", "level_name", "level", "handlers", "description", "mh_logger"
    
    
    def __init__( self, name, logger, level_name: Optional[str], level: Optional[int], handlers, description: Optional[str], mh_logger: Optional[Logger] ):
        self.name = name
        self.logger = logger
        self.level_name = level_name
        self.level = level
        self.handlers = handlers
        self.description = description
        self.mh_logger: Optional[Logger] = mh_logger
    
    
    def __str__( self ):
        return self.name


def iterate_loggers() -> List[LoggerInfo]:
    warnings.warn( "Deprecated - use LogCollection.list_loggers().", DeprecationWarning )
    return LogCollection.list_loggers()


class LogServer:
    """
    !STATIC
    
    Log server helper.
    
    Usage::
    
        LogServer.start( ... )
    """
    
    # delimiter for list config
    _k_list_delimiter = "\t"
    
    # permitted characters for list config
    _k_permitted = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_." + _k_list_delimiter
    _k_encoding = "utf8"
    
    # Default values
    _k_default_config_port = 9999
    _k_default_log_port = 19996
    _k_default_host = "localhost"
    
    # global variable indicating if we have started the logging server
    _logging_server_started = None
    
    
    class Commands:
        begin = "log"
        reset = "reset"
        available = "list"
        root = "root"
        echo = "echo"
    
    
    @staticmethod
    def start( accept = "list",
               host = None,
               log_port = None,
               config_port = None,
               register: bool = False ):
        """
        Starts a custom Python logging server.
        
        Repeated calls with the same parameters are ignored.
        Trying to change the parameters after the server has started causes a
        `RuntimeError` to be raised.
        
        :param accept:      Controls the type of configuration accepted.
                            
                            "dict":     The socket accepts *standard* log server configurations.
                                        Can be configured by any Python log client.
                                        
                            "list":     The socket only accepts lists of loggers to enable. 
                                        Must be configured by `LogClient`.
                        
        :param host:        Host. Config and logging.
        :param log_port:    Port, logging (serve). Only used if `register` is set.
        :param config_port: Port, config (listen).
        :param register:    Add handlers for any loggers with a `Logger.enabled_hint`.      
                            See `LogCollection.register`.
        """
        
        if host is None:
            host = LogServer._k_default_host
        
        if config_port is None:
            config_port = LogServer._k_default_config_port
        
        if log_port is None:
            log_port = LogServer._k_default_log_port
        
        args = dict( accept = accept, host = host, log_port = log_port, config_port = config_port, register = register )
        
        if LogServer._logging_server_started is not None:
            if LogServer._logging_server_started == args:
                return
            else:
                raise RuntimeError( f"Logging server has already been started with the arguments `{LogServer._logging_server_started}` but new arguments `{args}` are now being provided." )
        
        __logging_server_started = args
        
        if accept == "list":
            validation = LogServer.__decode
        elif accept == "dict":
            validation = None
        else:
            raise ValueError( f"Unknown `accept` parameter: {accept!r}" )
        
        t = logging.config.listen( config_port, validation )
        t.daemon = True
        t.start()
        
        socket_handler = logging.handlers.SocketHandler( host, log_port )
        
        LogCollection.register( register, socket_handler )
        
        # Always send a message to the broadcast log
        _broadcast_log.logger.addHandler( socket_handler )
        _broadcast_log.logger.setLevel( logging.DEBUG )
        _broadcast_log( "Logging server started." )
    
    
    @staticmethod
    def __decode( list_: bytes ) -> Optional[bytes]:
        """
        Verifier used by the `list` log server.
        
        Converts from and to bytes, using `__list_to_config` to translate `list`
        configurations into standard `dict` configurations.
        
        Counterpart of `LogClient.encode`.
        """
        text = list_.decode( LogServer._k_encoding )
        
        if not all( x in LogServer._k_permitted for x in text ):
            _broadcast_log( "Config received: UNRECOGNISED" )
            return None
        
        config = text.split( LogServer._k_list_delimiter )
        config = LogServer.__list_to_config( config )
        
        if config is None:
            return None
        
        json_ = json.dumps( config )
        print( json_ )
        return json_.encode( LogServer._k_encoding )
    
    
    @staticmethod
    def __list_to_config( list_: list, host = None, port = None ) -> Optional[dict]:
        """
        Used by the `list` log server's verifier.
        
        Translates the `list` configurations into standard `dict` configurations.
        """
        if host is None:
            host = LogServer._k_default_host
        
        if port is None:
            port = LogServer._k_default_log_port
        
        if list_ and list_[0].lower() == LogServer.Commands.begin:
            cmd = list_[1].lower() if len( list_ ) >= 2 else None
            _broadcast_log( "***** NEW COMMAND {}", repr( cmd ) )
            
            if cmd == LogServer.Commands.reset:
                _broadcast_log( "Config received: ALIAS {}", repr( cmd ) )
                list_ = [x.name for x in LogCollection.list_enabled()]
            elif cmd == LogServer.Commands.root:
                _broadcast_log( "Config received: ALIAS {}", repr( cmd ) )
                list_ = [""]
            elif cmd == LogServer.Commands.echo:
                _broadcast_log( "Config received: COMMAND {}", repr( cmd ) )
                
                _broadcast_log( "ECHO: {}", list_ )
                return None
            elif cmd == LogServer.Commands.available:
                _broadcast_log( "Config received: COMMAND {}", repr( cmd ) )
                
                for logger in LogCollection.list_loggers():
                    _broadcast_log( "{}".format( logger ) )
                
                return None
            else:
                _broadcast_log( "Config received: UNKNOWN COMMAND {}", repr( cmd ) )
                return None
        else:
            _broadcast_log( "Config received: LIST {}", list_ )
        
        # This is always enabled!
        list_.append( _broadcast_log.name )
        
        return {
            "version"                 : 1,
            "disable_existing_loggers": True,
            
            "handlers"                : {
                "socket": {
                    "class": "logging.handlers.SocketHandler",
                    "level": "DEBUG",
                    "host" : host,
                    "port" : port
                    }
                },
            
            "loggers"                 : {
                key: {
                    "level"   : "DEBUG",
                    "handlers": ["socket"]
                    } for key in list_
                },
            
            "formatters"              : { }
            }


class LogClient:
    """
    !STATIC
    
    Log client helper.
    Use against an application using `LogServer`.
    
    Usage::
    
        LogClient.send( <config>, ... )
        LogClient.receive( ... )
    """
    TConfig = Union[str, dict, bytes, list, tuple]
    
    
    @staticmethod
    def encode( config: TConfig ) -> bytes:
        """
        Converts an object into a set of bytes suitable for sending to the config server.

        Counterpart of `LogServer.__decode`.        
        
        dict      -> Converted to JSON text.
                     Only accepted for "dict" logging servers (see `start_server`).
        list      -> Converted to delimited text.
                     Only accepted for "list" logging servers (see `start_server`).
        str/bytes -> Returned directly (as text).
                     The bytes must represent a `dict` or `list` as above.
        """
        if isinstance( config, list ) or isinstance( config, tuple ):
            config = LogServer._k_list_delimiter.join( config )
        elif isinstance( config, dict ):
            config = json.dumps( config )
        
        if isinstance( config, str ):
            config = config.encode( LogServer._k_encoding )
        
        if not isinstance( config, bytes ):
            raise exception_helper.type_error( "config", config, LogClient.TConfig )
        
        return config
    
    
    @staticmethod
    def send( config: TConfig, host = None, port = None ) -> None:
        """
        Sends logging configuration to the server.
        
        :param config:      Logging configuration, in a format suitable for passing to `encode`. 
        :param host:        Server host name
        :param port:        Server config port 
        :return: 
        """
        if host is None:
            host = LogServer._k_default_host
        
        if port is None:
            port = LogServer._k_default_config_port
        
        config = LogClient.encode( config )
        s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        s.connect( (host, port) )
        s.send( struct.pack( '>L', len( config ) ) )
        s.send( config )
        s.close()
    
    
    class LogRecordStreamHandler( socketserver.StreamRequestHandler ):
        """Handler for a streaming logging request.
    
        This basically logs the record using whatever logging policy is
        configured locally.
        """
        
        
        def handle( self ):
            """
            Handle multiple requests - each expected to be a 4-byte length,
            followed by the LogRecord in pickle format. Logs the record
            according to whatever policy is configured locally.
            """
            try:
                while True:
                    chunk = self.connection.recv( 4 )
                        
                    if len( chunk ) < 4:
                        break
                        
                    slen = struct.unpack( '>L', chunk )[0]
                    chunk = self.connection.recv( slen )
                    while len( chunk ) < slen:
                        chunk = chunk + self.connection.recv( slen - len( chunk ) )
                    obj = self.unPickle( chunk )
                    record = logging.makeLogRecord( obj )
                    self.handleLogRecord( record )
            except socket.timeout:
                pass
        
        
        def unPickle( self, data ):
            return pickle.loads( data )
        
        
        def handleLogRecord( self, record ):
            # if a name is specified, we use the named logger rather than the one
            # implied by the record.
            logger = logging.getLogger( record.name )
            # N.B. EVERY record gets logged. This is because Logger.handle
            # is normally called AFTER logger-level filtering. If you want
            # to do filtering, do it at the client end to save wasting
            # cycles and network bandwidth!
            logger.handle( record )
    
    
    class LogRecordSocketReceiver( socketserver.ThreadingTCPServer ):
        """
        Simple TCP socket-based logging receiver suitable for testing.
        """
        
        allow_reuse_address = True
        
        
        def __init__( self, host = 'localhost',
                      port = LogServer._k_default_log_port,
                      handler = None ):
            if handler is None:
                handler = LogClient.LogRecordStreamHandler
            socketserver.ThreadingTCPServer.__init__( self, (host, port), handler )
            self.abort = 0
            self.timeout = 1
            self.logname = None
    
    
    class AsyncReceiver:
        def __init__( self, tcp_server: "LogClient.LogRecordSocketReceiver", thread ):
            self.tcp_server = tcp_server
            self.thread = thread
        
        
        def stop( self ):
            self.tcp_server.shutdown()
            self.thread.join()
    
    
    @staticmethod
    def receive() -> None:
        tcp_server = LogClient.__make_server()
        tcp_server.serve_forever()
    
    
    @staticmethod
    def __make_server() -> "LogClient.LogRecordSocketReceiver":
        for logger in LogCollection.list_loggers():
            logger.logger.handlers.clear()
        
        logging.getLogger( "" ).setLevel( logging.DEBUG )
        logging.getLogger( "" ).addHandler( LogConsole() )
        
        _primary_log( "Starting log receiver." )
        tcp_server = LogClient.LogRecordSocketReceiver()
        
        return tcp_server
    
    
    @staticmethod
    def receive_async() -> AsyncReceiver:
        tcp_server = LogClient.__make_server()
        thread = threading.Thread( target = tcp_server.serve_forever, name = "LogClient.async_receiver" )
        thread.start()
        return LogClient.AsyncReceiver( tcp_server, thread )


_primary_log = Logger( "log_helper.main", True, "Main logging initialisation messages." )
_broadcast_log = Logger( "log_helper.log_server", True, "Log server messages and config."
                                                        "A handler to this log is *always* added during `LogServer.start`, "
                                                        "even if no other logs are enabled (`register` = `False`). "
                                                        "This ensures the clients know the server is working. "
                                                        "Clients can disable this log thereafter by updating the config."
                                                        "Additionally, when using `list` config, "
                                                        "a handler is always added to the config received." )
