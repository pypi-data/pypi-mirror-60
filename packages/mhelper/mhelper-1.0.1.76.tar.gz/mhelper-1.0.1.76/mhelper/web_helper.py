import os
from time import sleep

from mhelper import file_helper, string_helper, log_helper


_log = log_helper.Logger( "mhelper.web_helper.cached_request", True )

NO_FILE = ('', '')

__info = False


def cached_request( url, *,
                    app = None,
                    headers = None,
                    throttle = 0,
                    data = None,
                    cache = True,
                    files = None,
                    fake = True,
                    cache_key = None,
                    retries = 3,
                    retry_throttle = 3 ):
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
    
    global __info
    
    if not __info:
        _log( "The web cache is {}", string_helper.format_size( get_cache_size() ) )
        __info = True
    
    title = url.split( "/", 3 )[2]
    
    if fake:
        if headers is None:
            headers = { }
        
        referer = url.split( "?", 1 )[0]
        origin = "/".join( url.split( "/", 3 )[:3] )
        
        headers.setdefault( 'User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0' )
        headers.setdefault( "Origin", origin )
        headers.setdefault( "Referer", referer )
        headers.setdefault( "Accept-Language", "en-GB,en;q=0.5" )
    
    file_name = get_cache_file_name( url, app = app, cache_key = cache_key, data = data )
    
    if cache and os.path.isfile( file_name ):
        _log( "Already cached. ({})", title )
        result = file_helper.read_all_text( file_name )
        return result
    
    _log( "Contacting server... ({})", title )
    
    if throttle:
        sleep( throttle )
    
    if data is None and files is None:
        method = "GET"
    else:
        method = "POST"
    
    request = None
    
    while True:
        try:
            request = requests.request( method = method, url = url, data = data, headers = headers, files = files )
        except Exception as ex:
            if retries:
                _log( "No response, retrying in {} seconds... ({})", retry_throttle, title )
                sleep( retry_throttle )
                retry_throttle *= 2
                retries -= 1
                continue
            
            message = [f"Request failed:",
                       f"",
                       f"import requests",
                       f"requests.request(",
                       f"    method = {method!r}",
                       f"    url = {url!r}",
                       f"    data = {data!r}",
                       f"    headers = {headers!r}",
                       f"    files = {files!r} )",
                       f"",
                       f"Due to an error",
                       f"{ex.__class__.__qualname__}: {ex}"]
            
            raise ConnectionError( "\n".join( message ) )
        else:
            break
    
    _log( "Contacted OK. ({})", title )
    
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


def get_cache_size( app = None ) -> int:
    if app is None:
        app = "mhelper", "web_helper"
    
    directory = file_helper.get_directory( get_cache_file_name( "", app = app ) )
    return file_helper.get_directory_tree_size( directory )
