__g_publisher = None


def rst_to_html_fragment( rst ):
    global __g_publisher
    if __g_publisher is None:
        __g_publisher = __Publisher()
    
    r = __g_publisher( rst )
    return r


# noinspection PyPackageRequirements
class __Publisher:
    __slots__ = "translator", "writer"
    
    
    def __init__( self ):
        from docutils.writers.html4css1 import Writer
        self.writer = Writer()
        self.writer.translator_class = self.__get_translator_class()
    
    
    @staticmethod
    def __get_translator_class():
        from docutils.writers.html4css1 import HTMLTranslator
        
        
        # noinspection PyAttributeOutsideInit
        class _NoHeaderHTMLTranslator( HTMLTranslator ):
            def __init__( self, document ):
                super().__init__( document )
            
            
            def depart_document( self, node ):
                super().depart_document( node )
                self.html_head = ['', '', '', '', '']
                self.head_prefix = []
                self.body_prefix = []
                self.body_suffix = []
                self.stylesheet = []
                self.meta = []
                self.head = []
            
            
            def visit_title_reference( self, node ):
                self.body.append( self.starttag( node, 'code', '' ) )
            
            
            def depart_title_reference( self, _ ):
                self.body.append( '</code>' )
        
        
        return _NoHeaderHTMLTranslator
    
    
    def __call__( self, doc ):
        import docutils.core
        from mhelper import string_helper
        try:
            data = docutils.core.publish_string( string_helper.strip_lines_to_first( str( doc ) ),
                                                 settings_overrides = { "report_level": 100, "field_name_limit": 0 },
                                                 writer = self.writer )
        except Exception as ex:
            return f"{type( ex ).__name__}: { str( ex ) }"
        else:
            return data.decode( "utf8" ).strip()
