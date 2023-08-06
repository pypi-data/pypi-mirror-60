from mhelper import web_helper


def request_all_uniprot_ids( organism = 9606 ):
    url = f"https://www.uniprot.org/uniprot/?query=reviewed:yes+AND+organism:{organism}&format=list"
    
    data = web_helper.cached_request( url )
    
    return data.split( "\n" )
