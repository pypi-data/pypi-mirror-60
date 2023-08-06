from html import escape

def new_plot(x):
    import matplotlib.pyplot
    fig = matplotlib.pyplot.figure( x )
    matplotlib.pyplot.title( x )
    

def add_handlers():
    def int_formatter( obj ):
        html = ["<table>"]
        html.append( f"<thead><tr><th><var>{type( obj ).__name__}</var></th>" )
        html.append( "<td>{0}</td>".format( escape( str( obj ) ) ) )
        html.append( "</tr>" )
        html.append( "</table>" )
        
        return "".join( html )
    
    
    def dict_formatter( obj ):
        html = ["<table>"]
        html.append( f"<thead><tr><th colspan=3><var>{type( obj ).__name__}</var> of {len( obj )} items</th></tr>" )
        html.append( "<tr>" )
        html.append( "<th>Index</th>" )
        html.append( "<th>Key</th>" )
        html.append( "<th>Value</th>" )
        html.append( "</tr></thead>" )
        
        for i, (key, value) in enumerate( obj.items() ):
            html.append( "<tr>" )
            html.append( "<td>{0}</td>".format( i ) )
            html.append( "<td>{0}</td>".format( escape( str( key ) ) ) )
            html.append( "<td>{0}</td>".format( escape( str( value ) ) ) )
            html.append( "</tr>" )
        html.append( "</table>" )
        
        return "".join( html )
    
    
    def list_formatter( obj ):
        html = ["<table>"]
        html.append( f"<thead><tr><th colspan=2><var>{type( obj ).__name__}</var> of {len( obj )} items</th></tr>" )
        html.append( "<tr>" )
        html.append( "<th>Index</th>" )
        html.append( "<th>Value</th>" )
        html.append( "</tr></thead>" )
        
        for i, value in enumerate( obj ):
            html.append( "<tr>" )
            html.append( "<td>{0}</td>".format( i ) )
            
            if isinstance(value, list) or isinstance(value, tuple):
                for cell in value:
                    html.append( "<td>{0}</td>".format( escape( str( cell ) ) ) )
            else:
                html.append( "<td>{0}</td>".format( escape( str( value ) ) ) )
            html.append( "</tr>" )
        html.append( "</table>" )
        
        return "".join( html )
    
    
    import IPython
    ip = IPython.get_ipython()
    formatter = ip.display_formatter.formatters['text/html']
    formatter.for_type( dict, dict_formatter )
    
    for ty in (list, tuple, set, frozenset):
        formatter.for_type( ty, list_formatter )
    
    for ty in (int, float, bool, str):
        formatter.for_type( ty, int_formatter )
    
    # from IPython.core.interactiveshell import InteractiveShell
    # InteractiveShell.ast_node_interactivity = "all"
