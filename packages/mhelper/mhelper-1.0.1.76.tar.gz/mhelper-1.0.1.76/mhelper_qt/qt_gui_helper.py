import functools
from typing import Optional, Dict, Union

import sys
from PyQt5.QtWidgets import QLineEdit, QFileDialog, QComboBox

from mhelper import string_helper, exception_helper, html_helper
from mhelper.exception_helper import SwitchError, ImplementationError
from mhelper.generics_helper import DECORATOR_FUNCTION, DECORATOR, DECORATED

__author__ = "Martin Rusilowicz"

# DLG_OPTS = QFileDialog.DontUseNativeDialog
DLG_OPTS = None

TTextBox = Union[QLineEdit, QComboBox]


def exceptToGui() -> DECORATOR_FUNCTION:
    """
    DECORATOR
    
    Same as `exqtSlot` but without the `pyqtSlot` bit.
    """
    
    
    def true_decorator( fn ) -> DECORATOR:
        @functools.wraps( fn )
        def fn_wrapper( *args, **kwargs ) -> DECORATED:
            try:
                return fn( *args, **kwargs )
            except Exception as ex:
                show_exception( args[0], "Error", ex )
        
        
        # noinspection PyTypeChecker
        return fn_wrapper
    
    
    return true_decorator


def exqtSlot( *decorator_args ) -> DECORATOR_FUNCTION:
    """
    DECORATOR
    
    `pyqtSlot` is problematic in that if an exception occurs the application will silently exit.
    This decorator replaces `pyqtSlot` by adding not only the decorator, but a simple error handler. 
    """
    
    
    def true_decorator( fn ) -> DECORATOR:
        from PyQt5.QtCore import pyqtSlot
        return pyqtSlot( *decorator_args )( exceptToGui()( fn ) )
    
    
    return true_decorator


def browse_dir_on_textbox( textbox: TTextBox ) -> bool:
    """
    Opens a file browser, using a textbox to retrieve and store the filename.
    """
    owner = textbox.window()
    
    if isinstance( textbox, QLineEdit ):
        text = textbox.text()
    elif isinstance( textbox, QComboBox ):
        text = textbox.currentText()
    else:
        raise SwitchError( "textbox", textbox, instance = True )
    
    dir_name = str( QFileDialog.getExistingDirectory( owner, "Select directory", text, **__dlg_opts() ) )
    
    if not dir_name:
        return False
    
    set_user_text( textbox, dir_name )
    
    return True


def __dlg_opts():
    return { "options": DLG_OPTS } if DLG_OPTS is not None else { }


def browse_dir( owner, existing = None ):
    return str( QFileDialog.getExistingDirectory( owner, "Select directory", existing, **__dlg_opts() ) )


def get_user_text( textbox: TTextBox ) -> str:
    if isinstance( textbox, QLineEdit ):
        return textbox.text()
    elif isinstance( textbox, QComboBox ):
        return textbox.currentText()
    else:
        raise SwitchError( "textbox", textbox, instance = True )


def set_user_text( textbox: TTextBox, text: str ) -> None:
    if isinstance( textbox, QLineEdit ):
        textbox.setText( text )
    elif isinstance( textbox, QComboBox ):
        textbox.setCurrentText( text )
    else:
        raise SwitchError( "textbox", textbox, instance = True )


def browse_open_on_textbox( textbox: TTextBox ) -> bool:
    """
    Opens a file browser, using a textbox to retrieve and store the filename.
    """
    from mhelper import file_helper
    
    owner = textbox.window()
    directory = file_helper.get_directory( get_user_text( textbox ) )
    
    sel_file, sel_filter = QFileDialog.getOpenFileName( owner, "Select file", directory )
    
    if not sel_file:
        return False
    
    set_user_text( textbox, sel_file )
    
    return True


def browse_save_on_textbox( textbox: QLineEdit, filter ) -> bool:
    """
    Opens a file browser, using a textbox to retrieve and store the filename.
    """
    from mhelper import file_helper
    
    owner = textbox.window()
    directory = file_helper.get_directory( textbox.text() )
    
    dir_name = str( QFileDialog.getSaveFileName( owner, "Select file", directory, filter, **__dlg_opts() ) )
    
    if not dir_name:
        return False
    
    textbox.setText( dir_name )
    
    return True


def browse_save( parent, filter ):
    from mhelper import file_helper
    
    file_name, file_filter = QFileDialog.getSaveFileName( parent, "Save", "", filter, **__dlg_opts() )
    
    if file_name:
        if not file_helper.get_extension( file_name ):
            file_filter = get_extension_from_filter( file_filter )
            
            file_name += file_filter
    
    return file_name or None


def browse_open( parent, filter ):
    file_name, file_filter = QFileDialog.getOpenFileName( parent, "Open", "", filter, **__dlg_opts() )
    
    return file_name or None


def get_extension_from_filter( file_filter ):
    """
    Gets the first extension from a filter of the form
    
    Data ( *.txt ) --> .txt
    Data (*.txt) --> .txt
    Data (*.txt, *.csv) --> .txt
    Data (*.txt *.csv) --> .txt
    etc.
    """
    file_filter = file_filter.split( "(", 1 )[1].strip( " *" )
    
    for x in " ,)":
        if x in file_filter:
            file_filter = file_filter.split( x, 1 )[0]
    return file_filter


# noinspection PyUnusedLocal
def show_exception( owner, message = None, exception = None, traceback_ = None ) -> None:
    if not traceback_:
        traceback_ = exception_helper.get_traceback()
    
    if isinstance( message, BaseException ):
        exception = message
        message = "Error"
    
    from PyQt5.QtWidgets import QMessageBox
    msg = QMessageBox()
    msg.setIcon( QMessageBox.Critical )
    msg.setText( str( message ) )
    
    if isinstance( exception, BaseException ):
        print( "{}: {}".format( type( exception ).__name__, exception ), file = sys.stderr )
        from mhelper import ansi_format_helper
        print( ansi_format_helper.format_traceback_ex( exception ), file = sys.stderr )
        msg.setInformativeText( str( exception ) )
        msg.setDetailedText( traceback_ )
        
        msg.exec_()


def to_check_state( value ):
    from PyQt5.QtCore import Qt
    if value is None:
        return Qt.PartiallyChecked
    elif value:
        return Qt.Checked
    else:
        return Qt.Unchecked


def from_check_state( value ):
    from PyQt5.QtCore import Qt
    if value == Qt.PartiallyChecked:
        return None
    elif value == Qt.Checked:
        return True
    elif value == Qt.Unchecked:
        return False
    else:
        from mhelper.exception_helper import SwitchError
        raise SwitchError( "from_check_state.value", value )


def move_treeview_items( source, destination, only_selected = True ):
    from PyQt5.QtWidgets import QTreeWidget
    assert isinstance( source, QTreeWidget )
    assert isinstance( destination, QTreeWidget )
    
    if only_selected:
        selected_items = source.selectedItems()
    else:
        selected_items = []
        
        for index in range( source.topLevelItemCount() ):
            selected_items.append( source.topLevelItem( index ) )
    
    for item in selected_items:
        index = source.indexOfTopLevelItem( item )
        source.takeTopLevelItem( index )
        destination.addTopLevelItem( item )







class QtMutex:
    """
    A `QMutex` wrapped in Python.
    
    This is a `QMutex` and requires QT.
    - It is only for the GUI!
    - - Plugins should *not* use this!
    
    Usage:

        ```
        m = QtMutex()
        
        with m:
           . . .
           
        ```
           
    """
    
    
    def __init__( self ):
        from PyQt5.QtCore import QMutex
        self._mutex = QMutex()
    
    
    def __enter__( self ):
        self._mutex.lock()
        return self
    
    
    def __exit__( self, exc_type, exc_val, exc_tb ):
        self._mutex.unlock()


def suppress_debugging():
    # Disable PyQT logging to console since we use console for other stuff, plus, it's irritating
    # noinspection PyUnusedLocal
    def __message_handler( msg_type, msg_log_context, msg_string ):
        pass
    
    
    from PyQt5 import QtCore
    QtCore.qInstallMessageHandler( __message_handler )



#region deprecated

AnsiHtmlLine = html_helper.AnsiHtmlLine
AnsiHtmlScheme = html_helper.AnsiHtmlLine
ansi_scheme_dark = html_helper.ansi_scheme_dark
ansi_scheme_light = html_helper.ansi_scheme_light
ansi_to_html = html_helper.ansi_to_html
_AnsiCodeIndex = html_helper._AnsiCodeIndex

#endregion