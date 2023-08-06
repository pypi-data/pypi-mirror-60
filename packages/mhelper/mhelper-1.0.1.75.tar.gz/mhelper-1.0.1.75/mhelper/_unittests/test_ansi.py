from mhelper import ansi, colours


do_not_test = { ansi.ALTERNATE_SCREEN, ansi.ALTERNATE_SCREEN_OFF, ansi.CLEAR_SCREEN }
test_types = { str, colours.Colour }


def is_acceptable( name, value ):
    if name.startswith( "_" ):
        return False
    
    if type( value ) not in test_types:
        return False
    
    if value in do_not_test:
        return False
    
    return True


def run_ansi_tests():
    for obj in (ansi.Back24, ansi.Fore24, colours, colours.Colours, ansi, ansi.Fore, ansi.Back, ansi.Style):
        on = obj.__name__
        
        print( "=" * len( on ) )
        print( on )
        print( "=" * len( on ) )
        
        x = { name: getattr( obj, name ) for name in dir( obj ) if is_acceptable( name, getattr( obj, name ) ) }
        
        rm = []
        
        for name, code in x.items():
            for name2, code2 in x.items():
                if code == code2 and name != name2 and len( name2 ) > len( name ):
                    rm.append( name )
                    break
        
        for name in rm:
            del x[name]
        
        for index, (name, code) in enumerate( x.items() ):
            if index % 4 == 0:
                print()
            else:
                print( " | ", end = "" )
            
            if isinstance( code, colours.Colour ):
                code = code.ansib
            
            if name.endswith( "_OFF" ):
                on_name = name[:-4]
                on_code = getattr( obj, on_name )
                print( "{:<20} = {}{}{}{}{}{}{}".format( name, on_name, on_code, "ON", code, "OFF", ansi.RESET, " " * (15 - len( on_name )) ), end = "" )
            else:
                print( "{:<20} = {}{}{}{}".format( name, code, name, ansi.RESET, " " * (20 - len( name )) ), end = "" )
        
        print()
        print()
    
    on = "Gradients"
    print( "=" * len( on ) )
    print( on )
    print( "=" * len( on ) )
    print()
    
    for i in range( 0, 255, 4 ):
        print( ansi.fore( i, 0, 0 ) + "*", end = "" )
    
    print( ansi.RESET )
    
    for i in range( 0, 255, 4 ):
        print( ansi.fore( 0, i, 0 ) + "*", end = "" )
    
    print( ansi.RESET )
    
    for i in range( 0, 255, 4 ):
        print( ansi.fore( 0, 0, i ) + "*", end = "" )
    
    print( ansi.RESET )
    
    for i in range( 0, 255, 4 ):
        print( ansi.back( i, 0, 0 ) + "*", end = "" )
    
    print( ansi.RESET )
    
    for i in range( 0, 255, 4 ):
        print( ansi.back( 0, i, 0 ) + "*", end = "" )
    
    print( ansi.RESET )
    
    for i in range( 0, 255, 4 ):
        print( ansi.back( 0, 0, i ) + "*", end = "" )
    
    print( ansi.RESET )
    
    print()


if __name__ == "__main__":
    run_ansi_tests()
