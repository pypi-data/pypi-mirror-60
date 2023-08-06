import html

from horno.datos import Encoding
from horno.utiles.IO import IOSistema
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

    #------------------------------------------------------------------------------------------
    def ElemToString(self, elem):
        
        from lxml.etree import tostring
        inner_html = tostring(elem)
        return inner_html        

    #------------------------------------------------------------------------------------------
    def XPathSafeText(self, elem, paths, default=''):
        
        try:
            if type(elem) in [str, bytes] or any([t in str(type(elem)) for t in ['_ElementStringResult', '_ElementUnicodeResult']]): 
                return Encoding().NormalizarTexto(elem)
            if not type(paths) == list: 
                paths = [paths]
            for path in paths:
                res = elem.xpath(path)
                if not res: continue
                txt = Encoding().NormalizarTexto(res[0]).strip()
                if not txt: continue
                return txt
            return default
        except Exception as e:
            IOSistema().PrintLine(e)
            return '[ERROR-xpathtext]'

    #------------------------------------------------------------------------------------------
    def XPathSafeProp(self, elem, path, prop, default=''):

        try:
            res = elem.xpath(path)
            if not res: return default
            txt = Encoding().NormalizarTexto(res[0].get(prop))
            return txt
        except Exception as e:
            IOSistema().PrintLine(e)
            return '[ERROR-xpathprop]'
        


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
