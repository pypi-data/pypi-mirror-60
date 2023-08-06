"""
Deprecated - too specific use case.
"""
from typing import Dict, Optional
from mhelper import string_helper


class AnsiHtmlLine:
    __slots__ = "code", "back", "fore", "style", "family"
    
    
    def __init__( self, code, back = None, fore = None, style = None, family = None ):
        """
        CONSTRUCTOR
        :param code:            ANSI code 
        :param back:            Back colour 
        :param fore:            Fore colour 
        :param style:           Font style 
        :param family:          Font family 
        """
        if isinstance( code, AnsiHtmlLine ):
            self.code = code.code
            self.back = code.back
            self.fore = code.fore
            self.style = code.style
            self.family = code.family
        else:
            self.code = code
            self.back = back
            self.fore = fore
            self.style = style
            self.family = family
    
    
    def to_style( self, background ):
        if background:
            return 'background:{}; color:{}; font-style:{}; font-family:{}'.format( self.back, self.fore, self.style, self.family )
        else:
            return 'color:{}; font-style:{}; font-family:{}'.format( self.fore, self.style, self.family )
    
    
    def copy( self ):
        return AnsiHtmlLine( self.code, self.back, self.fore, self.style, self.family )


class AnsiHtmlScheme:
    __slots__ = "values",
    
    
    def __init__( self, values ):
        values = [x if isinstance( x, AnsiHtmlLine ) else AnsiHtmlLine( *x ) for x in values]
        self.values: Dict[int, AnsiHtmlLine] = dict( (x.code, x) for x in values )
    
    
    def copy( self ) -> "AnsiHtmlScheme":
        return AnsiHtmlScheme( (x.copy() for x in self.values.values()) )
    
    
    def __getitem__( self, item: int ) -> AnsiHtmlLine:
        return self.values[item]
    
    
    def get_default( self ) -> AnsiHtmlLine:
        return self[_AnsiCodeIndex.CODE_INTERNAL_DEFAULT]


def ansi_scheme_dark( fg = "#FFFFFF", bg = "#000000", style = "normal", family = "sans-serif" ) -> AnsiHtmlScheme:
    """
    Creates a new ANSI scheme, defaulted to dark values.
    """
    return AnsiHtmlScheme( ((_AnsiCodeIndex.CODE_FORE_BLACK, "", "#000000", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_RED, "", "#FF0000", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_GREEN, "", "#00FF00", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_YELLOW, "", "#FFFF00", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_BLUE, "", "#0000FF", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_MAGENTA, "", "#FF00FF", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_CYAN, "", "#00FFFF", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_WHITE, "", "#FFFFFF", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_RESET, "", "*", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_LIGHT_BLACK, "", "#808080", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_LIGHT_RED, "", "#FF8080", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_LIGHT_GREEN, "", "#80FF80", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_LIGHT_YELLOW, "", "#FFFF80", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_LIGHT_BLUE, "", "#8080FF", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_LIGHT_MAGENTA, "", "#FF80FF", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_LIGHT_CYAN, "", "#80FFFF", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_LIGHT_WHITE, "", "#FFFFFF", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_BLACK, "#000000", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_RED, "#FF0000", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_GREEN, "#00FF00", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_YELLOW, "#FFFF00", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_BLUE, "#0000FF", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_MAGENTA, "#FF00FF", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_CYAN, "#00FFFF", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_WHITE, "#FFFFFF", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_RESET, "*", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_LIGHT_BLACK, "#808080", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_LIGHT_RED, "#FF8080", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_LIGHT_GREEN, "#80FF80", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_LIGHT_YELLOW, "#FFFF80", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_LIGHT_BLUE, "#8080FF", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_LIGHT_MAGENTA, "#FF80FF", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_LIGHT_CYAN, "#80FFFF", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_LIGHT_WHITE, "#FFFFFF", "", "", ""),
                            (_AnsiCodeIndex.CODE_STYLE_RESET_ALL, "*", "*", "*", ""),
                            (_AnsiCodeIndex.CODE_STYLE_BRIGHT, "", "", "bold", ""),
                            (_AnsiCodeIndex.CODE_STYLE_DIM, "", "", "italic", ""),
                            (_AnsiCodeIndex.CODE_STYLE_NORMAL, "", "", "normal", ""),
                            (_AnsiCodeIndex.CODE_INTERNAL_DEFAULT, bg, fg, style, family),
                            (_AnsiCodeIndex.CODE_INTERNAL_QUOTE_START, "", "#00C0FF", "", "monospace"),
                            (_AnsiCodeIndex.CODE_INTERNAL_QUOTE_END, "", "*", "", "*"),
                            (_AnsiCodeIndex.CODE_INTERNAL_TABLE_START, "", "", "", "monospace"),
                            (_AnsiCodeIndex.CODE_INTERNAL_TABLE_END, "", "", "", "*"),
                            ) )


def ansi_scheme_light( fg = "#000000", bg = "#FFFFFF", style = "normal", family = "sans-serif" ) -> AnsiHtmlScheme:
    """
    Creates a new ANSI scheme, defaulted to light values.
    """
    return AnsiHtmlScheme( ((_AnsiCodeIndex.CODE_FORE_BLACK, "", "#000000", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_RED, "", "#C00000", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_GREEN, "", "#00C000", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_YELLOW, "", "#C0C000", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_BLUE, "", "#0000C0", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_MAGENTA, "", "#C000C0", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_CYAN, "", "#00C0C0", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_WHITE, "", "#C0C0C0", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_RESET, "", "*", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_LIGHT_BLACK, "", "#C0C0C0", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_LIGHT_RED, "", "#FF0000", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_LIGHT_GREEN, "", "#00FF00", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_LIGHT_YELLOW, "", "#FFFF00", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_LIGHT_BLUE, "", "#0000FF", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_LIGHT_MAGENTA, "", "#FF00FF", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_LIGHT_CYAN, "", "#00FFFF", "", ""),
                            (_AnsiCodeIndex.CODE_FORE_LIGHT_WHITE, "", "#FFFFFF", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_BLACK, "#000000", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_RED, "#C00000", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_GREEN, "#00C000", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_YELLOW, "#C0C000", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_BLUE, "#0000C0", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_MAGENTA, "#C000C0", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_CYAN, "#00C0C0", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_WHITE, "#C0C0C0", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_RESET, "*", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_LIGHT_BLACK, "#C0C0C0", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_LIGHT_RED, "#FF0000", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_LIGHT_GREEN, "#00FF00", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_LIGHT_YELLOW, "#FFFF00", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_LIGHT_BLUE, "#0000FF", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_LIGHT_MAGENTA, "#FF00FF", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_LIGHT_CYAN, "#00FFFF", "", "", ""),
                            (_AnsiCodeIndex.CODE_BACK_LIGHT_WHITE, "#FFFFFF", "", "", ""),
                            (_AnsiCodeIndex.CODE_STYLE_RESET_ALL, "*", "*", "*", ""),
                            (_AnsiCodeIndex.CODE_STYLE_BRIGHT, "", "", "bold", ""),
                            (_AnsiCodeIndex.CODE_STYLE_DIM, "", "", "italic", ""),
                            (_AnsiCodeIndex.CODE_STYLE_NORMAL, "", "", "normal", ""),
                            (_AnsiCodeIndex.CODE_INTERNAL_DEFAULT, bg, fg, style, family),
                            (_AnsiCodeIndex.CODE_INTERNAL_QUOTE_START, "", "#0080C0", "", "Consolas, monospace"),
                            (_AnsiCodeIndex.CODE_INTERNAL_QUOTE_END, "", "*", "", "*"),
                            (_AnsiCodeIndex.CODE_INTERNAL_TABLE_START, "", "", "", "Consolas, monospace"),
                            (_AnsiCodeIndex.CODE_INTERNAL_TABLE_END, "", "", "", "*")
                            ) )


def ansi_to_html( text: Optional[str], lookup: Optional[AnsiHtmlScheme] = None, *, debug: bool = False, background: bool = True ) -> str:
    """
    Converts ANSI text to HTML.
    
    :param background:      Include background colours 
    :param text:            Text to convert 
    :param lookup:          An `AnsiHtmlScheme` object defining the colours to use, or `None` for the default (dark).
                            See functions `ansi_scheme_dark` and `ansi_scheme_light`. 
    :param debug:           When `True`, prints the results to a temporary file. 
    :return:                The HTML. 
    """
    if text is None:
        return ""
    
    from mhelper.string_parser import StringParser
    html = []
    
    lookup = lookup.values if lookup is not None else ansi_scheme_dark().values
    default_style = lookup[_AnsiCodeIndex.CODE_INTERNAL_DEFAULT]
    current_style = AnsiHtmlLine( default_style )
    
    text = string_helper.highlight_quotes( text, "`", "`", "\033[-2m", "\033[-3m" )
    text = string_helper.highlight_quotes( text, "┌", "┘", "\033[-4m", "\033[-5m" )
    text = string_helper.highlight_quotes( text, "«", "»", "\033[-2m", "\033[-3m" )
    
    text = text.replace( "\n* ", "\n• " )
    text = text.replace( "\n", '<br/>' )
    text = text.replace( " ", '\xa0' )
    
    parser = StringParser( text )
    
    html.append( '<div style="{}">'.format( current_style.to_style( background = background ) ) )
    
    iterations = 0
    
    ANSI_ESCAPE = '\033['
    
    while not parser.end():
        iterations += 1
        
        if iterations >= 100000:
            raise RuntimeError( "Possible infinite loop in mhelper.qt_gui_helper.ansi_to_html. Internal error. Possible solutions: Use a shorter string. Check the lookup syntax. Causing text follows:\n{}".format( text ) )
        
        html.append( parser.read_past( ANSI_ESCAPE ) )
        
        if parser.end():
            break
        
        code_str = parser.read_past( "m" )
        
        try:
            code = int( code_str )
        except Exception:
            code = None
        
        if code is not None:
            new_style = lookup.get( code, None )
            
            if new_style is not None:
                for attr in "fore", "back", "family", "style":
                    new = getattr( new_style, attr )
                    if new:
                        if new == "*":
                            setattr( current_style, attr, getattr( default_style, attr ) )
                        else:
                            setattr( current_style, attr, new )
                
                html.append( '</span><span style="{}">'.format( current_style.to_style( background = background ) ) )
    
    html.append( '</div>' )
    
    result = "".join( html )
    
    if debug:
        txx = ["ANSI", text, "HTML", result]
        from mhelper import file_helper
        file_helper.write_all_text( "temp-del-me.txt", "\n".join( txx ) )
    
    return result


class _AnsiCodeIndex:
    __slots__ = ()
    CODE_FORE_BLACK = 30
    CODE_FORE_RED = 31
    CODE_FORE_GREEN = 32
    CODE_FORE_YELLOW = 33
    CODE_FORE_BLUE = 34
    CODE_FORE_MAGENTA = 35
    CODE_FORE_CYAN = 36
    CODE_FORE_WHITE = 37
    CODE_FORE_RESET = 39
    CODE_FORE_LIGHT_BLACK = 90
    CODE_FORE_LIGHT_RED = 91
    CODE_FORE_LIGHT_GREEN = 92
    CODE_FORE_LIGHT_YELLOW = 93
    CODE_FORE_LIGHT_BLUE = 94
    CODE_FORE_LIGHT_MAGENTA = 95
    CODE_FORE_LIGHT_CYAN = 96
    CODE_FORE_LIGHT_WHITE = 97
    CODE_BACK_BLACK = 40
    CODE_BACK_RED = 41
    CODE_BACK_GREEN = 42
    CODE_BACK_YELLOW = 43
    CODE_BACK_BLUE = 44
    CODE_BACK_MAGENTA = 45
    CODE_BACK_CYAN = 46
    CODE_BACK_WHITE = 47
    CODE_BACK_RESET = 49
    CODE_BACK_LIGHT_BLACK = 100
    CODE_BACK_LIGHT_RED = 101
    CODE_BACK_LIGHT_GREEN = 102
    CODE_BACK_LIGHT_YELLOW = 103
    CODE_BACK_LIGHT_BLUE = 104
    CODE_BACK_LIGHT_MAGENTA = 105
    CODE_BACK_LIGHT_CYAN = 106
    CODE_BACK_LIGHT_WHITE = 107
    CODE_STYLE_RESET_ALL = 0
    CODE_STYLE_BRIGHT = 1
    CODE_STYLE_DIM = 2
    CODE_STYLE_NORMAL = 22
    
    # Internal codes
    CODE_INTERNAL_DEFAULT = -1
    CODE_INTERNAL_QUOTE_START = -2
    CODE_INTERNAL_QUOTE_END = -3
    CODE_INTERNAL_TABLE_START = -4
    CODE_INTERNAL_TABLE_END = -5
