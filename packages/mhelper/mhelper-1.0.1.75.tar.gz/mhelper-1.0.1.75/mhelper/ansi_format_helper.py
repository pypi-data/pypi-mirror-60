"""
Contains functions for printing error tracebacks to an ANSI terminal using
colour highlighting, as well as a function to replace the default Python handler
with a colour version.
"""
import os
import shutil
import sys
import warnings
from typing import Union

from mhelper import ansi, exception_helper


def print_traceback( ex = None, *, file = None, alt_screen: bool = False, **kwargs ) -> None:
    """
    `print`s the result of `format_traceback_ex`. 
    """
    file = file if file is not None else sys.stderr
    
    if alt_screen:
        print( ansi.ALTERNATE_SCREEN_OFF )
    
    try:
        print( format_traceback_ex( ex, **kwargs ), file = file )
    except Exception as ex:
        print( str( ex ), file = file )
    finally:
        if alt_screen:
            input( "An error has occurred. Press return to continue . . . " )
            print( ansi.ALTERNATE_SCREEN )


def install_error_hook( *, pause = False, simple_warnings = False, original = True, file = None, jupyter: bool = False, alt_screen = False ):
    """
    Adds `print_traceback` to the system exception hook.
    """
    my_error_hook = __my_error_hook( sys.excepthook if original else None, pause = pause, file = file, wordwrap = 120 if jupyter else 0, alt_screen = alt_screen )
    
    sys.excepthook = my_error_hook
    warnings.showwarning = __my_warning_hook( original = warnings.showwarning if original and not simple_warnings else None,
                                              pause = pause,
                                              simple = simple_warnings,
                                              file = file,
                                              alt_screen = alt_screen )
    
    if jupyter:
        def ___my_jupyter_error_hook( *_, **__ ):
            my_error_hook( *sys.exc_info() )


        # noinspection PyPackageRequirements
        import IPython
        IPython.InteractiveShell.showtraceback = ___my_jupyter_error_hook


def format_traceback_ex( exception: Union[BaseException, str] = None,
                         *,
                         wordwrap: int = 0,
                         warning: bool = False,
                         style: str = None,
                         message: str = None ) -> str:
    """
    Pretty formats a traceback using ANSI escape codes.
    
    :param exception:       Exception to print the traceback for. 
    :param wordwrap:        Length of wrapping for lines. 0 assumes a default.
    :param style:           Error style ("information", "warning", "error" or the first letter thereof) 
    :param warning:         Deprecated. Use `style`. 
    :param message:         Optional message to include at the end of the traceback. 
    :return: The formatted traceback, as a `str`.
    """
    
    from mhelper.string_helper import highlight_quotes
    
    if warning:
        style = "w"
    elif not style:
        style = "e"
    else:
        style = style[0]
    
    p = _Palette( wordwrap, style )
    
    tb_co = exception_helper.get_traceback_ex( exception )
    
    # Format: Traceback
    for tb_ex in tb_co.exceptions:
        # Format: Title...
        if tb_ex.index == 0:
            p.write_tbar()
        else:
            p.write_hbar()
        p.write_message( message = p.title_bold_colour + tb_ex.type + p.title_colour + ": " + tb_ex.message,
                         colour = p.title_colour )
        p.write_hbar()
        # ...end
        
        for tb_fr in tb_ex.frames:
            # Format: Location...
            if "site-packages" in tb_fr.file_name or "lib/" in tb_fr.file_name:
                fc = p.outside_file_colour
                fbc = p.outside_file_bold_colour
            else:
                fc = p.file_colour
                fbc = p.file_bold_colour
            # File "/home/mjr/work/mhelper/mhelper/string_helper.py", line 792, in wrap
            p.write_message( message = "E{exception} F{frame} File \"{file}\", line {line} in {function}" \
                             .format( exception = tb_ex.index,
                                      frame = tb_fr.index,
                                      file = fbc + tb_fr.file_name + fc,
                                      line = fbc + str( tb_fr.line_no ) + fc,
                                      function = fbc + tb_fr.function + fc ),
                             colour = fc )
            # ...end
            
            # Format: Context
            p.write_message( message = (tb_fr.code_context.replace( tb_fr.next_function,
                                                                    p.code_bold_colour + tb_fr.next_function + p.code_colour )
                                        if tb_fr.next_function
                                        else tb_fr.code_context),
                             colour = p.code_colour )
            
            # Format: Locals
            for lo in tb_fr.locals:
                p.write_message( message = ">{name} = {value}".format( name = p.locals_bold_colour + lo.name + p.locals_colour,
                                                                       value = lo.repr ),
                                 colour = p.code_colour,
                                 colour2 = p.locals_colour,
                                 justify = 1 )
    
    p.write_hbar()
    
    # Format: Exception text
    for tb_ex in tb_co.exceptions:
        # "caused by"
        if tb_ex.index != 0:
            p.write_message( message = ansi.DIM + ansi.ITALIC + "caused by",
                             colour = p.error_colour,
                             justify = 0 )
        
        # Type
        p.write_message( message = ansi.UNDERLINE + tb_ex.type,
                         colour = p.error_colour,
                         justify = -1 )
        
        # Message
        p.write_message( message = highlight_quotes( tb_ex.message, "«", "»", p.error_bold_colour, p.error_colour ),
                         colour = p.error_colour,
                         justify = -1 )
    
    # Format caller message if present
    if message is not None:
        p.write_hbar()
        
        if message and message[-1].isalnum():
            message += "."
        
        p.write_message( message = "This {} trace has been printed because {}".format( "stack/information" if style == "i" else
                                                                                       "exception" if style == "e" else
                                                                                       "stack/warning",
                                                                                       message ),
                         colour = p.error_colour + ansi.ITALIC,
                         justify = -1 )
    
    p.write_bbar()
    
    return p.get_output()


class __my_error_hook:
    """
    Custom error hook installed by `install_error_hook`.
    """
    __slots__ = ("original", "pause", "file", "reenterant", "wordwrap", "alt_screen")
    
    
    def __init__( self, original, pause, file, wordwrap, alt_screen ):
        self.original = original
        self.pause = pause
        self.file = file
        self.reenterant = False
        self.wordwrap = wordwrap
        self.alt_screen = alt_screen
    
    
    def __call__( self, exctype, value, traceback ):
        if self.reenterant:
            return
        
        self.reenterant = True
        
        try:
            stream = self.file if self.file is not None else sys.stderr
            
            print_traceback( value,
                             wordwrap = self.wordwrap,
                             message = "the global error hook, __my_error_hook, was notified about the exception. "
                                       "The original handler will now be called.",
                             file = stream,
                             alt_screen = self.alt_screen )
            
            if self.pause:
                print( "Press enter to continue . . . ", end = "", file = stream )
                input()
            
            if self.original is not None:
                self.original( exctype, value, traceback )
        finally:
            self.reenterant = False


class __my_warning_hook:
    """
    Custom warning hook installed by `install_error_hook`.
    """
    __slots__ = "original", "pause", "simple", "file", "alt_screen"
    
    
    def __init__( self, original, pause, simple, file, alt_screen ):
        self.original = original
        self.pause = pause
        self.simple = simple
        self.file = file
        self.alt_screen = alt_screen
    
    
    def __call__( self, message, category, filename, lineno, file = None, line = None ):
        stream = self.file if self.file is not None else sys.stderr
        
        if self.simple:
            for i, l in enumerate( str( message ).split( "\n" ) ):
                l = l.ljust( 120 )
                if i == 0:
                    print( f"{ansi.FORE_BLACK}{ansi.BACK_YELLOW}◢◤{ansi.FORE_YELLOW}{ansi.BACK_BLACK} {l}{ansi.RESET}", file = stream )
                else:
                    print( f"{ansi.FORE_BLACK}{ansi.BACK_YELLOW}  {ansi.FORE_YELLOW}{ansi.BACK_BLACK} {l}{ansi.RESET}", file = stream )
        else:
            print_traceback( message,
                             warning = True,
                             message = "the global warning hook, __my_warning_hook, was notified about the exception. "
                                       "The original handler will now be called. "
                                       "Extra data follows: {}".format( dict( category = category, filename = filename, lineno = lineno, file = file, line = line ) ),
                             file = stream,
                             alt_screen = self.alt_screen )
        if self.pause:
            print( "Press enter to continue . . . ", end = "", file = stream )
            input()
        
        if self.original is not None:
            self.original( message, category, filename, lineno, file, line )


class _Palette:
    __slots__ = ("style",
                 "output",
                 "wordwrap",
                 "fwidth",
                 "width",
                 "reset_colour",
                 "vbar",
                 "tl_bar",
                 "hbar",
                 "tr_bar",
                 "vl_bar",
                 "vr_bar",
                 "bl_bar",
                 "br_bar",
                 "error_colour",
                 "error_bold_colour",
                 "locals_colour",
                 "locals_bold_colour",
                 "border_colour",
                 "code_colour",
                 "code_bold_colour",
                 "file_colour",
                 "file_bold_colour",
                 "outside_file_colour",
                 "outside_file_bold_colour",
                 "title_colour",
                 "title_bold_colour",
                 "left_margin",
                 "right_margin")
    
    
    def __init__( self, wordwrap, style ):
        if style == "e":
            NORMAL = ansi.BACK_WHITE + ansi.FORE_RED
            INVERTED = ansi.BACK_RED + ansi.FORE_WHITE
            BOLD = ansi.BACK_RED + ansi.FORE_YELLOW
        elif style == "w":
            NORMAL = ansi.BACK_BLACK + ansi.FORE_YELLOW
            INVERTED = ansi.BACK_YELLOW + ansi.FORE_BLACK
            BOLD = ansi.BACK_YELLOW + ansi.FORE_RED
        else:
            NORMAL = ansi.BACK_BLACK + ansi.FORE_CYAN
            INVERTED = ansi.BACK_BLUE + ansi.FORE_WHITE
            BOLD = ansi.BACK_BLUE + ansi.FORE_WHITE
        
        self.style = style
        self.output = []
        self.wordwrap = wordwrap or shutil.get_terminal_size( (140, 0) ).columns  # Total size of box
        self.fwidth = self.wordwrap - 2  # Size of box without borders
        self.width = self.wordwrap - 4  # Size of box without borders and margins
        self.reset_colour = ansi.RESET
        self.vbar, self.tl_bar, self.hbar, self.tr_bar, self.vl_bar, self.vr_bar, self.bl_bar, self.br_bar = "        "  # "│┌─┐├┤└┘"
        self.error_colour = ansi.RESET + NORMAL  # Error text colour
        self.error_bold_colour = ansi.RESET + ansi.BACK_WHITE + ansi.FORE_BLACK + ansi.ITALIC  # Error text quotes
        self.locals_colour = ansi.RESET + ansi.BACK_BRIGHT_BLACK + ansi.FORE_BLACK  # Locals colour
        self.locals_bold_colour = ansi.RESET + ansi.BACK_BRIGHT_BLACK + ansi.FORE_YELLOW  # Locals colour
        self.border_colour = ansi.RESET + INVERTED  # Border colour
        self.code_colour = ansi.RESET + ansi.BACK_BLUE + ansi.FORE_WHITE  # Code extracts
        self.code_bold_colour = ansi.RESET + ansi.BACK_BLUE + ansi.FORE_YELLOW  # Function name
        self.file_colour = ansi.RESET + ansi.BACK_BRIGHT_YELLOW + ansi.FORE_BLACK + ansi.DIM  # File lines
        self.file_bold_colour = ansi.RESET + ansi.BACK_BRIGHT_YELLOW + ansi.FORE_BLUE + ansi.BOLD  # File names, line numbers
        self.outside_file_colour = ansi.RESET + ansi.BACK_CYAN + ansi.FORE_BLACK + ansi.DIM  # File lines
        self.outside_file_bold_colour = ansi.RESET + ansi.BACK_CYAN + ansi.FORE_BLUE + ansi.BOLD  # File names, line numbers
        self.title_colour = ansi.RESET + INVERTED
        self.title_bold_colour = ansi.RESET + BOLD
        
        self.left_margin = self.border_colour + self.vbar
        self.right_margin = self.border_colour + self.vbar + ansi.RESET
    
    
    def write_hbar( self ):
        self.output.append( self.border_colour + self.vl_bar + self.hbar * self.fwidth + self.vr_bar + self.reset_colour )
    
    
    def write_tbar( self ):
        self.output.append( self.border_colour + self.tl_bar + self.hbar * self.fwidth + self.tr_bar + self.reset_colour )
    
    
    def write_bbar( self ):
        self.output.append( self.border_colour + self.bl_bar + self.hbar * self.fwidth + self.br_bar + self.reset_colour )
    
    
    def write_message( self, *, message, colour, justify = -1, colour2 = "" ):
        from mhelper.ansi_helper import wrap
        
        message += colour
        
        for l in wrap( message, self.width, justify = justify ):
            self.output.append( self.left_margin + colour + " " + colour2 + l + colour + " " + self.right_margin )
    
    
    def get_output( self ):
        return "\n".join( self.output ) + ("\a" if self.style == "e" else "")


def highlight_filename( fn ):
    a, b = os.path.split( fn )
    return a + os.path.sep + ansi.BOLD + b + ansi.RESET
