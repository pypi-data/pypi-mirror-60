import html

from horno.utiles.Singleton import Singleton


#==============================================================================================
class HtmlHelper (metaclass=Singleton):
    
    #------------------------------------------------------------------------------------------
    def UnescapearTexto(self, texto):
                        
        return html.unescape(texto)
        
    #------------------------------------------------------------------------------------------
    def CargarUrl(self, url):

        import lxml.html

        url_partes = url.split('://', 2)
        url = '%s://%s' % (url_partes[0], url_partes[-1].replace('//', '/'))

        from urllib import request
        req = request.Request(url, headers={'User-Agent' : "Magic Browser"})
        page_content = request.urlopen(req).read()
        page_elem = lxml.html.fromstring(page_content)
        return page_elem


#==============================================================================================
class UrlHelper ():
    
    #------------------------------------------------------------------------------------------
    def __init__(self, url):
        
        from urllib.parse import urlparse
        self.url_data = urlparse(url)
        self.esquema = self.url_data.scheme or 'http'
        self.hostpuerto = self.url_data.netloc
        self.host = self.url_data.hostname
        self.ruta = self.url_data.path
        self.puerto = self.url_data.port
        self.params = self.url_data.params
        self.query = self.url_data.query

    #------------------------------------------------------------------------------------------
    def to_full(self):

        url_link_ok = '%s://%s%s/%s' % (
            self.esquema, 
            self.hostpuerto,
            self.ruta
        )
        return url_link_ok
