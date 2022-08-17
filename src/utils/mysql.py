"""
    @file mysql.py
    @author Yash (bloop104@gmail.com)
    @date 8-August-2022
    @version 1.0.0
    
    @brief Utility class containing basic MYSQL functions
    
    @copyright Copyright (c) 2022
"""

from dataclasses import dataclass, replace
from pickle import TRUE
import string, os, mysql.connector
from tokenize import group
from utils.logs import logger
from mysql.connector import errorcode

class MYSQL:
    _mysql = ""
    
    # configuration Parameters
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': '',
    }
    
    Prefix = 'mg_'
    QueryResult = {}
    insert_id = ""
    rowCount = 0
    field = '*'
    
    def __init__(self, connect = False, **kwargs):
        for key in kwargs:
            if key in self.config:
                self.config[key] = kwargs[key]
        
        if connect:
            self.connect()
            
    def connect(self):
        if self._mysql is None:
            try:
                cnx = mysql.connector.connect(
                        user=self.config['user'],
                        password=self.config['password'],
                        host=self.config['host'],
                        database = self.config['database']
                    )
                self._mysql = cnx
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    logger.info("Wrong username or password")
                    return False
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    logger.info("Database doesn't exist")
                    return False
                else:
                    logger.info(err)
                    return False
        
        return self._mysql
    
    def fetch(self, block = 0):
        return self.QueryResult[block] if block in self.QueryResult else {}
    
    def select(
        self,
        table,
        field = '*',
        cond = '',
        prepare = {},
        start = 0,
        limit = '',
        order_by = '',
        direction = '',
        group_by = '',
        is_distinct = False,
        block = 0,
        debug = False
    ):
        order_by = order_by.strip()
        group_by = group_by.strip()
        param = {}
        
        try:
            start = int(start)
        except Exception:
            start = 0
        
        start = start if start > 0 else '0'
        
        param['limit'] = limit
        param['start'] = int(start)
        param['order_by'] = order_by
        param['group_by'] = group_by
        param['direction'] = direction
        param.update(prepare)
        
        add_limit = "LIMIT %(start)s, %(limit)s" if(limit != "" and limit > 0) else ""
        order_by = "ORDER BY %(order_by)s" if(order_by is not None and order_by != '') else ""
        group_by = "GROUP BY %(group_by)s" if(group_by is not None and group_by != '') else ""
        
        table = self._fixtable(table)
        
        select = 'SELECT' if is_distinct == False else 'SELECT DISTINCT'
        query = str(select) + " " + field + " FROM " + table + " " + cond + " " + group_by + " " + order_by + " " + direction + " " + add_limit
        
        self.query(query, param, block, debug)
        
    def where(
        self,
        table,
        condition = {},
        start = None,
        limit = None,
        order_by = '',
        direction = ''
    ):
        if isinstance(self.field, dict):
            count = len(self.field)
            if count == 0:
                field = '*'
            else:
                field = ''
                c = 0
                
                for value in self.field:
                    c += 1
                    field += field
                    if c != count:
                        field += ", "
        else:
            field = self.field
            
        params = self._where(condition)
        self.select(table, field, params['where'], params['param'], start, limit, order_by, direction)
        
    def _toSQL(
        self,
        value,
        type,
        quote = False,
        encode = True
    ):
        if value == "" and value != 0:
            return "NULL"
        else:
            if type == "Number":
                return float(value)
            else:
                if encode:
                    value = self._htmlSpecialChars(value)
                if not quote:
                    return value
                else:
                    return "'" + value + "'"
    
    def _fixtable(self, table_param):
        table_param = str(table_param)
        
        if self.Prefix != '':
            if "#_" in table_param:
                table = string.replace(table_param, "#_", self.Prefix)
            else:
                table = self.Prefix + table_param
        else:
            table = table_param
        
        return table
    
    def _where(self, condition = {}):
        where = ""
        param = {}
        
        if len(condition) > 0 :
            where += "where "
            i = 0
            
            for key in condition :
                value = condition[key]
                i += 1
            
                word = key.strip()
                word_get = word.rsplit(' ',1)
                key = word_get[0].strip()
            
                if len(word_get) == 2 :
                    operator = word_get[1]
                else :
                    operator = "="
            
                where += "  " + str(key) + " " + operator + " " + "%(" + str(key) + ")s"
            
                if i > 0 and i < len(condition):
                    where += " and "
            
                param[key] = value
        else:
           param = condition
        
        return { "where" : where, 'param' : param }

    def _field(self, required = []):
        if len(required) > 0:
            fields = ""
            i = 0
            
            for field in required:
                i += 1
                fields += " " + str(field)
                
                if i < len(required):
                    fields += ", "
            
            self.field = fields
            
    def _htmlSpecialChars(self, text):
        return text.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")