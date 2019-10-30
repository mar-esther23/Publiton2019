from re import sub
from unidecode import unidecode

def clean_string(s):
    if type(s)==str:
        s = unidecode(s)
        s = sub('[^A-Za-z0-9 ]+', '', s)
        s = sub('\s+', ' ', s)
        s = s.strip().title()
    else: s=''
    return s

import re
import pickle
import logging
import warnings
import pandas as pd
from fuzzywuzzy import process
from unidecode import unidecode

def simplificar_string(texto):
    """
    Recibe un string y regresa una versión en minusculas sin acentos o 
    caracteres especiales.
    """
    texto = unidecode(texto).strip().lower()
    texto = re.sub(r"[^a-zA-Z0-9]+", ' ', texto)
    return texto

def generar_diccionario_mapeo(datos, catalogo, 
    warn=90, limit=50, limit_value=None, max_opciones=3):
    """
    Toma una lista 'datos' de strings sucios que seran mapeados a un 'catalogo' y regresa el diccionario 
    con ese mapeo. Genera warnings si los datos tienen baja similitud al catálogo. Utiliza fuzzywuzzy.process.extract(). 
    
    Parametros
    ----------
    datos: list of str
        Lista de strings con los datos a mapear al catálogo
    catalogo: list of str
        Catalogo de opciones validas
    warn: int, default '90'
        Valor de similitud en el cual se avisa al usuario que hay baja similitud con las opciones del catálogo
    limit: int, default '50'
        Valor mínimo de similitud en el cual se mapea el string al catálogo
    limit_value: str, default 'None'
        Valor que se regresa si no hay una similitud mínima entre el string y el catálogo. 
        Si 'None' se regresa el valor original del string en datos
    max_opciones: int, default 3
        Número de opciones de mapeo a mostrar


    Regresa
    -------
    diccionario
        Diccionario que permite mapear las opciones al catálogo

    Ejemplos
    --------
    
    Estandarizar los datos a un catálogo. Si un valor no se encuentra en el catálogo, por ejemplo 'Cuahutemoc', dejar el valor original.

    >>> datos = ['Iztapalápa', 'B Juarez', 'Iztapapapa', 'Alvaro Obregon', 'ÁlvaroObregón', 'Cuahutemoc']
    >>> catalogo = ['Iztapalapa', 'Benito Juarez', 'Álvaro Obregón']
    >>> generar_diccionario_mapeo(datos, catalogo, limit_value=None)
    {'B Juarez': 'Benito Juarez',
     'Cuahutemoc': 'Cuahutemoc',
     'ÁlvaroObregón': 'Álvaro Obregón',
     'Alvaro Obregon': 'Álvaro Obregón',
     'Iztapalápa': 'Iztapalapa',
     'Iztapapapa': 'Iztapalapa'}
    """

    def crear_warning_opciones(val, warn_type, max_opciones):
        max_opciones = min(len(val), max_opciones)
        opciones = ', '.join([str(i[0])+' ('+str(i[1])+')' for i in val[0:max_opciones]])
        warn_message = "\n\t{}: {}.\n\tOpciones: {}" \
                                        .format(warn_type, i, opciones )
        warnings.warn( warn_message )

    # validar datos
    #Formateamos los datos y catalogo
    datos_ = list(set(datos))
    datos_ ={simplificar_string(s):s for s in datos_}
    catalogo_ = list(set(catalogo))
    catalogo_ ={simplificar_string(s):s for s in catalogo_}
    #Generamos el diccionario de equivalencias de valores unicos para ahorrar tiempo de procesamiento
    s_dic = {}
    ignorados = {}
    if limit_value!=None:
        catalogo_[limit_value]=limit_value
    for i in datos_.keys():
        # ignorar lo que no es string
        if type(i)!=str: 
            if limit_value==None: s_dic[i]=i
            else: s_dic[i]=limit_value
        else:
            # comparar con catalogo
            val = process.extract(i, catalogo_.keys())
            
            # Nula similitud
            if val[0][1] < limit: 
                if val[0][1] <= warn: 
                    crear_warning_opciones(val, 'IGNORADO', max_opciones)
                catalogo_[i] = datos_[i]
                if limit_value==None: s_dic[i]=i
                else: s_dic[i]=limit_value
            
            else: 
                if val[0][1] > limit and val[0][1] <= warn: # Baja similitud, levantar warning
                    crear_warning_opciones(val, 'BAJA SIMILITUD', max_opciones)
                s_dic[i] = val[0][0]
    # Regresar a formato original
    s_dic = {datos_[k]:catalogo_[v] for k,v in s_dic.items() }
    return s_dic