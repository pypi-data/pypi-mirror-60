"""
Contains constants and a class for dealing with 24 bit colours.
"""
from typing import Tuple, Iterable, Union, List
from mhelper import exception_helper


_ColourLike = Union[Tuple[int, int, int], str, "Colour", None, int, List[int]]


class Colour:
    __slots__ = "__r", "__g", "__b", "__a", "__name"
    
    
    def __init__( self, *args: _ColourLike, name = None ):
        """
        Constructs a colour.
        
        :param args:    [A,] R, G, B or HTML or Tuple([A,] R, G, B).
        
                        Note that the `_ColourLike` types `None` and `Colour`
                        aren't supported here, they should be passed to `use`
                        instead.
                        
                        ARGB should be an int [0,255] or a float [0,1].
                        Floats in (1,255] are tolerated. 
        """
        self.__name = name
        
        if not args:
            raise ValueError( f"`args` cannot be empty in the constructor. Did you mean to use `{Colour.use.__qualname__}` instead?" )
        elif len( args ) == 1:
            arg = args[0]
            
            if arg is None:
                raise ValueError( f"`arg` cannot be `None` in the constructor. Did you mean to use `{Colour.use.__qualname__}` instead?" )
            elif isinstance( arg, Colour ):
                raise ValueError( f"`arg` cannot be a `Colour` in the constructor. Colour is immutable and a copy should not be made. Did you mean to use `{Colour.use.__qualname__}` instead?" )
            elif isinstance( arg, str ):
                #
                # From string
                #
                if arg.startswith( "#" ):
                    arg = arg[1:]
                
                try:
                    self.__a = None
                    self.__r, self.__g, self.__b = (int( arg[cursor:cursor + 2], 16 ) for cursor in (0, 2, 4))
                except ValueError:
                    raise ValueError( f"`arg` must specify a valid colour code when it is a `str`, but this is not: {arg!r}" )
            elif isinstance( arg, tuple ) or isinstance( arg, list ):
                if len( arg ) == 3:
                    #
                    # From 3-tuple
                    #
                    self.__a = None
                    self.__r, self.__g, self.__b = arg
                elif len( arg ) == 4:
                    #
                    # From 4-tuple
                    #
                    self.__a, self.__r, self.__g, self.__b = arg
                else:
                    raise ValueError( f"`arg` must be of length 3 or 4 when it is a `tuple`, but this is not: {arg}" )
            else:
                raise exception_helper.type_error( "args[0]", args, _ColourLike )
        elif len( args ) == 3:
            #
            # From three ints
            #
            self.__a = None
            self.__r, self.__g, self.__b = args[0], args[1], args[2]
        elif len( args ) == 4:
            #
            # From four ints
            #
            self.__a, self.__r, self.__g, self.__b = args[0], args[1], args[2], args[3]
        else:
            raise ValueError( f"`args` must be of length 3 or 4 when it is a `tuple`, but this is not: {args}" )
        
        if isinstance( self.__a, float ) or isinstance( self.__r, float ) or isinstance( self.__g, float ) or isinstance( self.__b, float ):
            if (self.__a is None or self.__a <= 1) and self.__r <= 1 and self.__g <= 1 and self.__b <= 1:
                if self.__a is not None:
                    self.__a = int( self.__a * 255 )
                self.__r = int( self.__r * 255 )
                self.__g = int( self.__g * 255 )
                self.__b = int( self.__b * 255 )
            else:
                if self.__a is not None:
                    self.__a = int( self.__a )
                self.__r = int( self.__r )
                self.__g = int( self.__g )
                self.__b = int( self.__b )
        
        if self.__a is None:
            self.__a = 255
        
        assert isinstance( self.__a, int ), self
        assert isinstance( self.__r, int ), self
        assert isinstance( self.__g, int ), self
        assert isinstance( self.__b, int ), self
    
    
    def __repr__( self ):
        return f"{type( self ).__name__}({self.__a}, {self.__r}, {self.__g}, {self.__b})"
    
    
    @staticmethod
    def average( colours ):
        colours=tuple(colours)
        n = len(colours)
        a = sum( x.a for x in colours )//n
        r = sum( x.r for x in colours )//n
        g = sum( x.g for x in colours )//n
        b = sum( x.b for x in colours )//n
        return Colour( a, r, g, b )
    
    
    @staticmethod
    def use( *args: _ColourLike ):
        """
        Constructs from `args`, unless `args` is already a `Colour` (return
        that) or empty/`None` (return `None`).
        """
        if not args:
            return None
        elif len( args ) == 1:
            if args[0] is None:
                return None
            elif isinstance( args[0], Colour ):
                return args[0]
        
        return Colour( *args )
    
    
    @property
    def rgb( self ) -> Tuple[int, int, int]:
        return self.__r, self.__g, self.__b
    
    
    def nearest_colour( self, subjects: Iterable[_ColourLike] ):
        """
        Nearest colour (simple Euclidean)
        """
        return min( subjects, key = lambda subject: sum( (s - q) ** 2 for s, q in zip( Colour.use( subject ).rgb, self.rgb ) ) )
    
    
    def __floordiv__( self, other ):
        return Colour( self.r // other, self.g // other, self.b // other )
    
    
    def contrasting_bw( self, bright: "Colour" = None, dark: "Colour" = None ) -> "Colour":
        """
        Returns `dark` if this colour is closer to white, or `bright` if this
        colour is closer to black.
        """
        if self.l < 128:
            return Colour( 255, 255, 255 ) if bright is None else bright
        else:
            return Colour( 0, 0, 0 ) if dark is None else dark
    
    
    def mix( self, other: "Colour", fraction: float ) -> "Colour":
        """
        :param other:       Other colour 
        :param fraction:    Fraction of the other colour in the result 
        :return:            New colour 
        """
        if other is None:
            return self
        
        r = int( self.r + (other.r - self.r) * fraction )
        g = int( self.g + (other.g - self.g) * fraction )
        b = int( self.b + (other.b - self.b) * fraction )
        return Colour( r, g, b )
    
    
    @property
    def l( self ) -> int:
        """
        Lightness (0-255)
        """
        return int( 0.299 * self.__r + 0.587 * self.__g + 0.114 * self.__b )
    
    
    @property
    def a( self ) -> int:
        """
        Alpha (0-255)
        """
        return self.__a
    
    
    @property
    def r( self ) -> int:
        """
        Red (0-255)
        """
        return self.__r
    
    
    @property
    def g( self ) -> int:
        """
        Green (0-255)
        """
        return self.__g
    
    
    @property
    def b( self ) -> int:
        """
        Blue (0-255)
        """
        return self.__b
    
    
    @property
    def name( self ):
        """
        Name (HTML of not available).
        """
        return self.__name or self.html
    
    
    @property
    def html( self ) -> str:
        """
        Colour as HTML Code #RRGGBB
        """
        return "#{0:02x}{1:02x}{2:02x}".format( self.__r, self.__g, self.__b )
    
    
    @property
    def ansif( self ) -> str:
        """
        Colour as ANSI foreground colour code. 
        """
        import mhelper.ansi
        return mhelper.ansi.fore( self )
    
    
    @property
    def ansib( self ) -> str:
        """
        Colour as ANSI background colour code. 
        """
        import mhelper.ansi
        return mhelper.ansi.back( self )


class Colours:
    """
    Colour names and codes for DOS colours (capitals) and web colours
    (camelcase).
    
    Note that the web colours are a bit obscure, for instance `DarkGray` is
    lighter than `Gray`.
    """
    Transparent = Colour( 0, 0, 0, 0, name = "Transparent" )
    AliceBlue = Colour( 240, 248, 255, name = "AliceBlue" )  # F0F8FF 
    AntiqueWhite = Colour( 250, 235, 215, name = "AntiqueWhite" )  # FAEBD7 
    Aqua = Colour( 0, 255, 255, name = "Aqua" )  # 00FFFF 
    Aquamarine = Colour( 127, 255, 212, name = "Aquamarine" )  # 7FFFD4 
    Azure = Colour( 240, 255, 255, name = "Azure" )  # F0FFFF 
    Beige = Colour( 245, 245, 220, name = "Beige" )  # F5F5DC 
    Bisque = Colour( 255, 228, 196, name = "Bisque" )  # FFE4C4 
    Black = Colour( 0, 0, 0, name = "Black" )  # 000000 
    BlanchedAlmond = Colour( 255, 235, 205, name = "BlanchedAlmond" )  # FFEBCD 
    Blue = Colour( 0, 0, 255, name = "Blue" )  # 0000FF 
    BlueViolet = Colour( 138, 43, 226, name = "BlueViolet" )  # 8A2BE2 
    Brown = Colour( 165, 42, 42, name = "Brown" )  # A52A2A 
    BurlyWood = Colour( 222, 184, 135, name = "BurlyWood" )  # DEB887 
    CadetBlue = Colour( 95, 158, 160, name = "CadetBlue" )  # 5F9EA0 
    Chartreuse = Colour( 127, 255, 0, name = "Chartreuse" )  # 7FFF00 
    Chocolate = Colour( 210, 105, 30, name = "Chocolate" )  # D2691E 
    Coral = Colour( 255, 127, 80, name = "Coral" )  # FF7F50 
    CornflowerBlue = Colour( 100, 149, 237, name = "CornflowerBlue" )  # 6495ED 
    Cornsilk = Colour( 255, 248, 220, name = "Cornsilk" )  # FFF8DC 
    Crimson = Colour( 220, 20, 60, name = "Crimson" )  # DC143C 
    Cyan = Colour( 0, 255, 255, name = "Cyan" )  # 00FFFF 
    DarkBlue = Colour( 0, 0, 139, name = "DarkBlue" )  # 00008B 
    DarkCyan = Colour( 0, 139, 139, name = "DarkCyan" )  # 008B8B 
    DarkGoldenRod = Colour( 184, 134, 11, name = "DarkGoldenRod" )  # B8860B 
    DarkGray = Colour( 169, 169, 169, name = "DarkGray" )  # A9A9A9 
    DarkGrey = Colour( 169, 169, 169, name = "DarkGrey" )  # A9A9A9 
    DarkGreen = Colour( 0, 100, 0, name = "DarkGreen" )  # 006400 
    DarkKhaki = Colour( 189, 183, 107, name = "DarkKhaki" )  # BDB76B 
    DarkMagenta = Colour( 139, 0, 139, name = "DarkMagenta" )  # 8B008B 
    DarkOliveGreen = Colour( 85, 107, 47, name = "DarkOliveGreen" )  # 556B2F 
    DarkOrange = Colour( 255, 140, 0, name = "DarkOrange" )  # FF8C00 
    DarkOrchid = Colour( 153, 50, 204, name = "DarkOrchid" )  # 9932CC 
    DarkRed = Colour( 139, 0, 0, name = "DarkRed" )  # 8B0000 
    DarkSalmon = Colour( 233, 150, 122, name = "DarkSalmon" )  # E9967A 
    DarkSeaGreen = Colour( 143, 188, 143, name = "DarkSeaGreen" )  # 8FBC8F 
    DarkSlateBlue = Colour( 72, 61, 139, name = "DarkSlateBlue" )  # 483D8B 
    DarkSlateGray = Colour( 47, 79, 79, name = "DarkSlateGray" )  # 2F4F4F 
    DarkSlateGrey = Colour( 47, 79, 79, name = "DarkSlateGrey" )  # 2F4F4F 
    DarkTurquoise = Colour( 0, 206, 209, name = "DarkTurquoise" )  # 00CED1 
    DarkViolet = Colour( 148, 0, 211, name = "DarkViolet" )  # 9400D3 
    DeepPink = Colour( 255, 20, 147, name = "DeepPink" )  # FF1493 
    DeepSkyBlue = Colour( 0, 191, 255, name = "DeepSkyBlue" )  # 00BFFF 
    DimGray = Colour( 105, 105, 105, name = "DimGray" )  # 696969 
    DimGrey = Colour( 105, 105, 105, name = "DimGrey" )  # 696969 
    DodgerBlue = Colour( 30, 144, 255, name = "DodgerBlue" )  # 1E90FF 
    FireBrick = Colour( 178, 34, 34, name = "FireBrick" )  # B22222 
    FloralWhite = Colour( 255, 250, 240, name = "FloralWhite" )  # FFFAF0 
    ForestGreen = Colour( 34, 139, 34, name = "ForestGreen" )  # 228B22 
    Fuchsia = Colour( 255, 0, 255, name = "Fuchsia" )  # FF00FF 
    Gainsboro = Colour( 220, 220, 220, name = "Gainsboro" )  # DCDCDC 
    GhostWhite = Colour( 248, 248, 255, name = "GhostWhite" )  # F8F8FF 
    Gold = Colour( 255, 215, 0, name = "Gold" )  # FFD700 
    GoldenRod = Colour( 218, 165, 32, name = "GoldenRod" )  # DAA520 
    Gray = Colour( 128, 128, 128, name = "Gray" )  # 808080 
    Grey = Colour( 128, 128, 128, name = "Grey" )  # 808080 
    Green = Colour( 0, 128, 0, name = "Green" )  # 008000 
    GreenYellow = Colour( 173, 255, 47, name = "GreenYellow" )  # ADFF2F 
    HoneyDew = Colour( 240, 255, 240, name = "HoneyDew" )  # F0FFF0 
    HotPink = Colour( 255, 105, 180, name = "HotPink" )  # FF69B4 
    IndianRed = Colour( 205, 92, 92, name = "IndianRed" )  # CD5C5C 
    Indigo = Colour( 75, 0, 130, name = "Indigo" )  # 4B0082 
    Ivory = Colour( 255, 255, 240, name = "Ivory" )  # FFFFF0 
    Khaki = Colour( 240, 230, 140, name = "Khaki" )  # F0E68C 
    Lavender = Colour( 230, 230, 250, name = "Lavender" )  # E6E6FA 
    LavenderBlush = Colour( 255, 240, 245, name = "LavenderBlush" )  # FFF0F5 
    LawnGreen = Colour( 124, 252, 0, name = "LawnGreen" )  # 7CFC00 
    LemonChiffon = Colour( 255, 250, 205, name = "LemonChiffon" )  # FFFACD 
    LightBlue = Colour( 173, 216, 230, name = "LightBlue" )  # ADD8E6 
    LightCoral = Colour( 240, 128, 128, name = "LightCoral" )  # F08080 
    LightCyan = Colour( 224, 255, 255, name = "LightCyan" )  # E0FFFF 
    LightGoldenRodYellow = Colour( 250, 250, 210, name = "LightGoldenRodYellow" )  # FAFAD2 
    LightGray = Colour( 211, 211, 211, name = "LightGray" )  # D3D3D3 
    LightGrey = Colour( 211, 211, 211, name = "LightGrey" )  # D3D3D3 
    LightGreen = Colour( 144, 238, 144, name = "LightGreen" )  # 90EE90 
    LightPink = Colour( 255, 182, 193, name = "LightPink" )  # FFB6C1 
    LightSalmon = Colour( 255, 160, 122, name = "LightSalmon" )  # FFA07A 
    LightSeaGreen = Colour( 32, 178, 170, name = "LightSeaGreen" )  # 20B2AA 
    LightSkyBlue = Colour( 135, 206, 250, name = "LightSkyBlue" )  # 87CEFA 
    LightSlateGray = Colour( 119, 136, 153, name = "LightSlateGray" )  # 778899 
    LightSlateGrey = Colour( 119, 136, 153, name = "LightSlateGrey" )  # 778899 
    LightSteelBlue = Colour( 176, 196, 222, name = "LightSteelBlue" )  # B0C4DE 
    LightYellow = Colour( 255, 255, 224, name = "LightYellow" )  # FFFFE0 
    Lime = Colour( 0, 255, 0, name = "Lime" )  # 00FF00 
    LimeGreen = Colour( 50, 205, 50, name = "LimeGreen" )  # 32CD32 
    Linen = Colour( 250, 240, 230, name = "Linen" )  # FAF0E6 
    Magenta = Colour( 255, 0, 255, name = "Magenta" )  # FF00FF 
    Maroon = Colour( 128, 0, 0, name = "Maroon" )  # 800000 
    MediumAquaMarine = Colour( 102, 205, 170, name = "MediumAquaMarine" )  # 66CDAA 
    MediumBlue = Colour( 0, 0, 205, name = "MediumBlue" )  # 0000CD 
    MediumOrchid = Colour( 186, 85, 211, name = "MediumOrchid" )  # BA55D3 
    MediumPurple = Colour( 147, 112, 219, name = "MediumPurple" )  # 9370DB 
    MediumSeaGreen = Colour( 60, 179, 113, name = "MediumSeaGreen" )  # 3CB371 
    MediumSlateBlue = Colour( 123, 104, 238, name = "MediumSlateBlue" )  # 7B68EE 
    MediumSpringGreen = Colour( 0, 250, 154, name = "MediumSpringGreen" )  # 00FA9A 
    MediumTurquoise = Colour( 72, 209, 204, name = "MediumTurquoise" )  # 48D1CC 
    MediumVioletRed = Colour( 199, 21, 133, name = "MediumVioletRed" )  # C71585 
    MidnightBlue = Colour( 25, 25, 112, name = "MidnightBlue" )  # 191970 
    MintCream = Colour( 245, 255, 250, name = "MintCream" )  # F5FFFA 
    MistyRose = Colour( 255, 228, 225, name = "MistyRose" )  # FFE4E1 
    Moccasin = Colour( 255, 228, 181, name = "Moccasin" )  # FFE4B5 
    NavajoWhite = Colour( 255, 222, 173, name = "NavajoWhite" )  # FFDEAD 
    Navy = Colour( 0, 0, 128, name = "Navy" )  # 000080 
    OldLace = Colour( 253, 245, 230, name = "OldLace" )  # FDF5E6 
    Olive = Colour( 128, 128, 0, name = "Olive" )  # 808000 
    OliveDrab = Colour( 107, 142, 35, name = "OliveDrab" )  # 6B8E23 
    Orange = Colour( 255, 165, 0, name = "Orange" )  # FFA500 
    OrangeRed = Colour( 255, 69, 0, name = "OrangeRed" )  # FF4500 
    Orchid = Colour( 218, 112, 214, name = "Orchid" )  # DA70D6 
    PaleGoldenRod = Colour( 238, 232, 170, name = "PaleGoldenRod" )  # EEE8AA 
    PaleGreen = Colour( 152, 251, 152, name = "PaleGreen" )  # 98FB98 
    PaleTurquoise = Colour( 175, 238, 238, name = "PaleTurquoise" )  # AFEEEE 
    PaleVioletRed = Colour( 219, 112, 147, name = "PaleVioletRed" )  # DB7093 
    PapayaWhip = Colour( 255, 239, 213, name = "PapayaWhip" )  # FFEFD5 
    PeachPuff = Colour( 255, 218, 185, name = "PeachPuff" )  # FFDAB9 
    Peru = Colour( 205, 133, 63, name = "Peru" )  # CD853F 
    Pink = Colour( 255, 192, 203, name = "Pink" )  # FFC0CB 
    Plum = Colour( 221, 160, 221, name = "Plum" )  # DDA0DD 
    PowderBlue = Colour( 176, 224, 230, name = "PowderBlue" )  # B0E0E6 
    Purple = Colour( 128, 0, 128, name = "Purple" )  # 800080 
    RebeccaPurple = Colour( 102, 51, 153, name = "RebeccaPurple" )  # 663399 
    Red = Colour( 255, 0, 0, name = "Red" )  # FF0000 
    RosyBrown = Colour( 188, 143, 143, name = "RosyBrown" )  # BC8F8F 
    RoyalBlue = Colour( 65, 105, 225, name = "RoyalBlue" )  # 4169E1 
    SaddleBrown = Colour( 139, 69, 19, name = "SaddleBrown" )  # 8B4513 
    Salmon = Colour( 250, 128, 114, name = "Salmon" )  # FA8072 
    SandyBrown = Colour( 244, 164, 96, name = "SandyBrown" )  # F4A460 
    SeaGreen = Colour( 46, 139, 87, name = "SeaGreen" )  # 2E8B57 
    SeaShell = Colour( 255, 245, 238, name = "SeaShell" )  # FFF5EE 
    Sienna = Colour( 160, 82, 45, name = "Sienna" )  # A0522D 
    Silver = Colour( 192, 192, 192, name = "Silver" )  # C0C0C0 
    SkyBlue = Colour( 135, 206, 235, name = "SkyBlue" )  # 87CEEB 
    SlateBlue = Colour( 106, 90, 205, name = "SlateBlue" )  # 6A5ACD 
    SlateGray = Colour( 112, 128, 144, name = "SlateGray" )  # 708090 
    SlateGrey = Colour( 112, 128, 144, name = "SlateGrey" )  # 708090 
    Snow = Colour( 255, 250, 250, name = "Snow" )  # FFFAFA 
    SpringGreen = Colour( 0, 255, 127, name = "SpringGreen" )  # 00FF7F 
    SteelBlue = Colour( 70, 130, 180, name = "SteelBlue" )  # 4682B4 
    Tan = Colour( 210, 180, 140, name = "Tan" )  # D2B48C 
    Teal = Colour( 0, 128, 128, name = "Teal" )  # 008080 
    Thistle = Colour( 216, 191, 216, name = "Thistle" )  # D8BFD8 
    Tomato = Colour( 255, 99, 71, name = "Tomato" )  # FF6347 
    Turquoise = Colour( 64, 224, 208, name = "Turquoise" )  # 40E0D0 
    Violet = Colour( 238, 130, 238, name = "Violet" )  # EE82EE 
    Wheat = Colour( 245, 222, 179, name = "Wheat" )  # F5DEB3 
    White = Colour( 255, 255, 255, name = "White" )  # FFFFFF 
    WhiteSmoke = Colour( 245, 245, 245, name = "WhiteSmoke" )  # F5F5F5 
    Yellow = Colour( 255, 255, 0, name = "Yellow" )  # FFFF00 
    YellowGreen = Colour( 154, 205, 50, name = "YellowGreen" )  # 9ACD32
    BLACK = Colour( 0, 0, 0, name = "BLACK" )  # 000000 
    DARK_GRAY = Colour( 64, 64, 64, name = "DARK_GRAY" )  # 404040 
    GRAY = Colour( 128, 128, 128, name = "GRAY" )  # 808080 
    LIGHT_GRAY = Colour( 192, 192, 192, name = "LIGHT_GRAY" )  # C0C0C0 
    WHITE = Colour( 255, 255, 255, name = "WHITE" )  # FFFFFF 
    RED = Colour( 255, 0, 0, name = "RED" )  # FF0000 
    GREEN = Colour( 0, 255, 0, name = "GREEN" )  # 00FF00 
    BLUE = Colour( 0, 0, 255, name = "BLUE" )  # 0000FF 
    CYAN = Colour( 0, 255, 255, name = "CYAN" )  # 00FFFF 
    MAGENTA = Colour( 255, 0, 255, name = "MAGENTA" )  # FF00FF 
    YELLOW = Colour( 255, 255, 0, name = "YELLOW" )  # FFFF00 
    ORANGE = Colour( 255, 128, 0, name = "ORANGE" )  # FF8000 
    FUSCHIA = Colour( 255, 0, 128, name = "FUSCHIA" )  # FF0080 
    LIME = Colour( 128, 255, 0, name = "LIME" )  # 80FF00 
    SPRING_GREEN = Colour( 0, 255, 128, name = "SPRING_GREEN" )  # 00FF80 
    PURPLE = Colour( 128, 0, 255, name = "PURPLE" )  # 8000FF 
    DODGER_BLUE = Colour( 0, 128, 255, name = "DODGER_BLUE" )  # 0080FF 
    DARK_RED = Colour( 128, 0, 0, name = "DARK_RED" )  # 800000 
    DARK_GREEN = Colour( 0, 128, 0, name = "DARK_GREEN" )  # 008000 
    DARK_BLUE = Colour( 0, 0, 128, name = "DARK_BLUE" )  # 000080 
    DARK_CYAN = Colour( 0, 128, 128, name = "DARK_CYAN" )  # 008080 
    DARK_MAGENTA = Colour( 128, 0, 128, name = "DARK_MAGENTA" )  # 800080 
    DARK_YELLOW = Colour( 128, 128, 0, name = "DARK_YELLOW" )  # 808000 
    DARK_ORANGE = Colour( 128, 64, 0, name = "DARK_ORANGE" )  # 804000 
    DARK_FUSCHIA = Colour( 128, 0, 64, name = "DARK_FUSCHIA" )  # 800040 
    DARK_LIME = Colour( 64, 128, 0, name = "DARK_LIME" )  # 408000 
    DARK_SPRINGGREEN = Colour( 0, 128, 64, name = "DARK_SPRINGGREEN" )  # 008040 
    DARK_PURPLE = Colour( 64, 0, 128, name = "DARK_PURPLE" )  # 400080 
    DARK_DODGERBLUE = Colour( 0, 64, 128, name = "DARK_DODGERBLUE" )  # 004080 
    LIGHT_RED = Colour( 255, 128, 128, name = "LIGHT_RED" )  # FF8080 
    LIGHT_GREEN = Colour( 128, 255, 128, name = "LIGHT_GREEN" )  # 80FF80 
    LIGHT_BLUE = Colour( 128, 128, 255, name = "LIGHT_BLUE" )  # 8080FF 
    LIGHT_CYAN = Colour( 128, 255, 255, name = "LIGHT_CYAN" )  # 80FFFF 
    LIGHT_MAGENTA = Colour( 255, 0, 255, name = "LIGHT_MAGENTA" )  # FF00FF 
    LIGHT_YELLOW = Colour( 255, 255, 128, name = "LIGHT_YELLOW" )  # FFFF80
