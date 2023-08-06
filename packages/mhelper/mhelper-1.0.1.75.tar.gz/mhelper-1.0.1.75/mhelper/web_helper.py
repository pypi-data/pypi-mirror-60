import os
from time import sleep

from mhelper import file_helper, string_helper, log_helper


_log = log_helper.Logger( "mhelper.web_helper.cached_request", False )

NO_FILE = ('', '')


def cached_request( url, *,
                    app = None,
                    headers = None,
                    throttle = 0,
                    data = None,
                    cache = True,
                    files = None,
                    fake = True,
                    cache_key = None ):
    """
    Makes an HTTP request, caching the result.
    Note that only the URL and data are used as the cache keys by default.
    Other fields may be present but are disregarded from the cache.
    
    Requires the `requests` library.
    
    :param url:          Target URL. Including any GET query.
    :param app:          Requesting application. Used to name cache folder. 
    :param headers:      Request headers. 
    :param throttle:     Throttle (delay) requests. 
    :param data:         POST data, if any. 
    :param cache:        Whether to cache the result. 
    :param files:        POST data files, if any. 
    :param fake:         Fake user-agent, origin and referer, if not in `headers`. Required by some forms.
    :param cache_key:    Key to use for the cache. Uses the `url` and `data` if not specified.
                         This is only useful where the URL/data is fixed but the result is dependent on an earlier operation.
    :return:             Page data. 
    """
    try:
        # noinspection PyPackageRequirements
        import requests
    except ImportError as ex:
        raise ImportError( "This feature requires the requests library, which is not currently installed." ) from ex
    
    if fake:
        if headers is None:
            headers = { }
        
        origin = "/".join( url.split( "/", 3 )[:3] )
        referer = url.split( "?", 1 )[0]
        
        headers.setdefault( 'User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0' )
        headers.setdefault( "Origin", origin )
        headers.setdefault( "Referer", referer )
        headers.setdefault( "Accept-Language", "en-GB,en;q=0.5" )
    
    file_name = get_cache_file_name( url, app = app, cache_key = cache_key, data = data )
    
    _log( url )
    
    if data:
        for key, value in data.items():
            _log( f"{key} ---- {value}" )
    
    if cache and os.path.isfile( file_name ):
        _log( "[X] Entry in cache" )
        result = file_helper.read_all_text( file_name )
        return result
    
    _log( "[ ] Entry in cache" )
    
    if throttle:
        sleep( throttle )
    
    if data is None and files is None:
        method = "GET"
    else:
        method = "POST"
    
    request = requests.request( method = method, url = url, data = data, headers = headers, files = files )
    result = request.text
    file_helper.write_all_text( file_name, result )
    
    return result


def get_cache_file_name( url, *, app = None, cache_key = None, data = None ):
    if app is None:
        app = "mhelper", "web_helper"
    
    if cache_key is None:
        cache_key = url + repr( data )
    
    cache_key = str( cache_key )
    hash = string_helper.string_to_hash( cache_key )
    file_name = file_helper.get_application_file_name( *app, "web_cache", hash + ".html" )
    return file_name
