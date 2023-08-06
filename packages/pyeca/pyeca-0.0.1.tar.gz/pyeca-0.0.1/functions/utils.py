# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 15:32:24 2020

@author: 31000476
"""

from datetime import datetime
import os.path
from pathlib import Path

class FindFile(object):
    """
    Clase para instanciar objetos que permiten
    la búsqueda recursiva de un archivo en una
    ruta dada
    Params:
        path: <str> Ruta de busqueda
        fileName: <str> Nombre archivo a buscar
        first: <Bool> Opcional, Establece que la
                búsqueda se detenga con la primera
                ocurrencia encontrada. Default False
        order: <str> Opcional, establece el orden
                aplicado a través de la fecha de
                modificación del archivo. Default
                'desc'
    """
    def __init__(self, path, fileName, first=False, order='desc',
                 recurse=False):
        self.filename = fileName
        self.path = Path(path)
        self._original_path = path
        self._result = []
        self.first = first
        self._newer = None
        self._older = None
        self._name_list = []
        self._date_list = []
        self._counter_id = 0
        self._ordered_list = []
        self._order = order
        self._min_id = 0
        self._max_id = 0

    def _validate(self):
        if not isinstance(self.filename, str):
            raise Exception('ARCHIVO NO VALIDO')
        try:
            self.path.absolute()
        except Exception as e:
            raise Exception(e)
        return True

    def find(self):
        global stop
        stop = False
        def rFind(path, fileName):
            global stop
            for x in path.iterdir():
                if stop: break
                if x.is_dir():
                    rFind(x, fileName)
                else:
                    if fileName.upper() == x.name.upper():
                        self._counter_id += 1
                        self._result.append({
                                'id': self._counter_id,
                                'path': x.absolute(),
                                'name': x.name,
                                'date': self._getDatetime(x.absolute())
                                })
                        self._name_list.append((self._counter_id, x.name))
                        self._date_list.append((self._counter_id, \
                            self._getDatetime(x.absolute())))
                        if self.first: stop = True
        if not self._validate():
            print('DATOS NO VALIDOS')
            return
        rFind(self.path, self.filename)
        self._setNewer()
        self._setOlder()
        self._ordered_list = self._orderby()
        self._set_min_max_id()

    def getFirst(self):
        if self._ordered_list:
            return self._format_path(self._get_by_id(self._min_id))
        return self._result[0] if self._result else None
        
    def getLast(self):
        if self._ordered_list:
            return self._format_path(self._get_by_id(self._max_id))
        return self._result[-1] if self._result else None

    def _setNewer(self):
        if self._result:
            if len(self._result) > 1:
                self._newer = self._result[0]['path']
                for path in self._result:
                    if os.path.getmtime(path['path']) \
                        > os.path.getmtime(self._newer):
                        self._newer = path['path']
            else:
                self._newer = self._result[0]['path']
        else:
            self._newer = None

    def _setOlder(self):
        if self._result:
            if len(self._result) > 1:
                self._older = self._result[0]['path']
                for path in self._result:
                    if os.path.getmtime(path['path']) \
                        < os.path.getmtime(self._older):
                        self._older = path['path']
            else:
                self._older = self._result[0]['path']
        else:
            self._older = None

    # Retorna la ocurrencia mas nueva
    def getNewer(self):
        return self._newer
    
    # Retorna la ocurrencia mas antigua
    def getOlder(self):
        return self._older

    # Lista de todas las ocurrencias encontradas    
    def getList(self):
        rs = []
        for id, date in self._ordered_list:
            for path in self._result:
                if path['id'] == id:
                    rs.append(self._format_path(path))
        return rs
    
    def _getDatetime(self, path):
        try:
            rs = datetime.fromtimestamp(os.path.getmtime(path))
            return rs
        except Exception as e:
            return None

    def _orderby(self):
        if self._order == 'desc':
            return sorted(self._date_list, key=lambda x: x[1], reverse=True)
        else:
            return sorted(self._date_list, key=lambda x: x[1])

    def _get_by_id(self, id=1):
        rs = None
        for path in self._result:
            if path['id'] == id:
                rs = path
                break
        return rs

    def _set_min_max_id(self):
        if not self._ordered_list:
            return None
        if self._order == 'desc':
            self._min_id = self._ordered_list[-1][0]
            self._max_id = self._ordered_list[0][0]
        else:
            self._min_id = self._ordered_list[0][0]
            self._max_id = self._ordered_list[-1][0]

    def _format_path(self, path):
        return [
                path['path'],
                path['date']\
                    .strftime('%Y-%m-%d %H:%M:%S')
                    ]
    def exists(self):
        return len(self._result) > 0