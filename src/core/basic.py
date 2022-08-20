import imp
from multiprocessing.spawn import import_main_path
from sqlite3 import connect
from main import connection

def addInventory(id, stock):
    connection.insert("inventory", {"id": id, "stock": stock}, )