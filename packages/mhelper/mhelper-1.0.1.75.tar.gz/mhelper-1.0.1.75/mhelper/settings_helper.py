from mhelper import file_helper, io_helper
import os


class SettingsBase:
    def __init__( self ):
        self.__file_name = None
    
    
    @classmethod
    def on_get_file_name( cls ):
        raise NotImplementedError( "abstract" )
    
    
    @classmethod
    def load( cls, file_name: str = None ):
        file_name = SettingsBase.__get_fn( file_name or cls.on_get_file_name() )
        
        try:
            result = io_helper.load_json_pickle( file_name, default = None )
        except Exception as ex:
            raise ValueError( f"Failed to read the configuration file at '{file_name}'." ) from ex
        
        if result is None:
            result = cls()
        else:
            io_helper.default_values(result, cls)
        
        result.__file_name = file_name
        
        
        
        return result
    
    
    @staticmethod
    def __get_fn( file_name ):
        if os.path.sep in file_name:
            return file_name
        
        name, extension = os.path.splitext( file_name )
        fn = file_helper.get_config_file_name( name, extension )
        return fn
    
    
    def save( self, file_name: str = None ):
        file_name = SettingsBase.__get_fn( file_name or self.__file_name )
        io_helper.save_json_pickle( file_name, self )


class History( list ):
    
    def add( self, fn ):
        if fn in self:
            self.remove( fn )
        
        self.append( fn )
        
        if len( self ) > 10:
            del self[0]
