import re

from horno.utiles.Singleton import Singleton


#=============================================================================================
class Textos (metaclass=Singleton):

    #------------------------------------------------------------------------------------------
    def __init__(self):

        ''

    #------------------------------------------------------------------------------------------
    def ContieneDigitos(self, texto):
    
        return not re.match(".*[0-9]+.*", texto) is None

#=============================================================================================
class Listas (metaclass=Singleton):

    #------------------------------------------------------------------------------------------
    def __init__(self):

        ''

    #------------------------------------------------------------------------------------------
    def ElegirValor(self, key, default, dic):
        
        return dic.get(key, default)

    #------------------------------------------------------------------------------------------
    def ElegirPrimeroNoVacio(self, default, lista):
        
        lista_no_vacios = [e for e in lista if len(e)]
        return lista_no_vacios[0] if len(lista_no_vacios) else default
