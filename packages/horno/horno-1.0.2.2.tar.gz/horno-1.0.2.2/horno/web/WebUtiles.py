import html

import lxml.html
from horno.utiles.Singleton import Singleton


#==============================================================================================
class HtmlHelper (metaclass=Singleton):
    
    #------------------------------------------------------------------------------------------
    def __init__(self):
        
        pass
        
    #------------------------------------------------------------------------------------------
    def UnescapearTexto(self, texto):
                        
        return html.unescape(texto)
        
    #------------------------------------------------------------------------------------------
    def CargarUrl(self, url):

        url_partes = url.split('://', 2)
        url = '%s://%s' % (url_partes[0], url_partes[-1].replace('//', '/'))

        from urllib import request
        req = request.Request(url, headers={'User-Agent' : "Magic Browser"})
        page_content = request.urlopen(req).read()
        page_elem = lxml.html.fromstring(page_content)
        return page_elem
