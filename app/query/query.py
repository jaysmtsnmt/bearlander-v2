from app.common.paths import *
from app.query.exceptions import *
import logging
import json

logging.basicConfig(
    handlers = [
        logging.FileHandler(f"{PATH_LOGTXT}"),
        logging.StreamHandler()
    ],
    level = logging.INFO, #determine which level of logs to display - at info, debug isn't displayed, but everything else is.
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

logger = logging.getLogger("Query")

class Table:
    def __init__(self, name, type, path):
        self.name, self.type, self.path = name, type, path

    def __str__(self):
        return f"{self.name} | Type: {self.type} | Path: {self.path}"

from enum import Enum
class Tables(Enum):
    USERS = Table(
        name = "users",
        type = "csv",
        path = f"{PATH_USER_DATA}/users.csv"
    )

    USERDATA_DATABASE = Table(
        name = "Users",
        type = "sql",
        path = f"{PATH_USER_DATA}/database.db"
    )

class Query(Enum):
    SELECT = "select" #must pass filters
    DELETE = "delete" #must pass filters
    INSERT = "insert" #must pass filters
    UPDATE = "update" #must pass filters
    
import csv
class CSVHandler:
    @staticmethod
    def select(table:Tables, filters:dict):
        file_path = table.path

        with open(file_path, "r", newline="") as file:
            data = csv.DictReader(file) #written to data as list of dictionaries
            headers = data.fieldnames

            if filters != {}:
                results = []
                for line in data:
                    if all(line[header] == value for header, value in filters.items()):
                        results.append(line)

            else:
                results = data

        return results #returns as dictionary ! NO LONGER READ USING INDEXES!

    @staticmethod
    def delete(table:Tables, filters:dict):
        file_path = table.path
        
        with open(file_path, "r", newline="") as file:
            data = list(csv.DictReader(file))
            headers = data.fieldnames

            results = []
            for line in data:
                if not all(line[column] == data for column, data in filters.items()): #if negative match with filters
                    results.append(line)

            with open(file_path, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=headers)

                writer.writerows(results)

    @staticmethod
    def insert(table:Tables, values:list):
        """values should be 
        [   { "name" : Jayden, "column" : value }, 
            { etc 
        ]

        or single dictionary of column with value
        """

        file_path = table.path
        if not values: #check if values is none (which means no values were passed in kwargs)
            t = f"CSVINSERT | No values were passed in kwargs. | {table}"
            logger.critical(t)
            raise CSVError(t)

        if type(values) == dict: #convert to list for writerows
            values = [values]

        try: 
            with open(file_path, "r", newline="") as file:
                data = csv.DictReader(file)
                headers = data.fieldnames

            with open(file_path, "a", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=headers)

                writer.writerows(values)

        except ValueError:
            t = f"CSVINSERT | Extra column passed into table {table} | {values}"
            logger.critical(t)
            raise CSVError(t)

    @staticmethod
    def update(table:Tables, filters_and_values:dict):
        file_path = table.path

class QueryConditions:
    @staticmethod
    def exact(column:str, value:str):
        return f"{column} = '{value}'"
    
    @staticmethod
    def larger(column:str, value:str):
        return f"{column} > '{value}'"
    
    @staticmethod
    def smaller(column:str, value:str):
        return f"{column} < '{value}'"

    @staticmethod
    def smaller_equal(column:str, value:str):
        return f"{column} <= '{value}'"
    
    @staticmethod
    def larger_equal(column:str, value:str):
        return f"{column} >= '{value}'"


import sqlite3
class SQLHandler:
    @staticmethod
    def select(table:Tables, filters:dict):
        conn = sqlite3.connect(table.path)
        conn.row_factory = sqlite3.Row

        statement = f"""SELECT * FROM {table.name}"""
        if filters: 
            conditions = []
            if filters.get("specialised_filters"): #specialised_filters is a list in filters, in which QueryConditions is passed
                conditions = conditions + filters.get("specialised_filters") # ["age > 1", "name = Jayden", etc]

            for column, value in filters.items(): #append the rest, or append normal filters
                if column != "specialised_filters": conditions.append(QueryConditions.exact(column, value)) #ignore specialised filters. 

            statement += " WHERE " + " AND ".join(conditions)

        cursor = conn.execute(statement)
        rows = cursor.fetchall()
        rows = [dict(row) for row in rows]

        for row in rows: #reload all json objects into their respective lists or dictionaries.
            for key, value in row.items():
                if type(value) not in [str, int, float, bool] and value is not None:
                    row[key] = json.load(value)

        conn.close()
        return rows

    @staticmethod
    def update(table:Tables, filters_and_values:dict):
        pass

    @staticmethod
    def insert(table:Tables, values):
        if values: #if not none passed
            conn = sqlite3.connect(table.path)
            conn.row_factory = sqlite3.Row

            if type(values) == dict:
                values = [values]

            headers = values[0].keys()

            for row in values: #reload all json objects into their respective lists or dictionaries.
                for key, value in row.items():
                    if type(value) not in [str, int, float, bool] and value is not None:
                        row[key] = json.dumps(value)

                    if value is None:
                        row[key] = 'None'

            values = tuple([str(tuple(row.values())) for row in values])

            statement = f"""INSERT OR REPLACE INTO {table.name} ({", ".join(headers)}) 
                        VALUES {", ".join(values)} """
            
            # print(statement)
            conn.execute(statement)

            conn.commit()
            conn.close()

        else: 
            t = f"SQLINSERT | No values passed into insert(). | {table}"
            logger.critical(t)
            raise SQLError(t)
        

def query(table:Tables, operation:Query, **kwargs): 
    """
    General Query function for all tables stored in csv type, json type and also sql type. 
    args: 
        table = Table.USERS, 
        operation = Query.SELECT
    
    **filters: 
        name="jayden", password="password"
        OR if insert operation : 
        values = [{}] list of dictionaries

        if filters is None, return all data.
    """

    #check for valid tables & operators

    table = table.value
    if table in Tables and operation in Query:
        if table.type == "csv": #calling csv handlers
            if operation == Query.SELECT: #complete select operation
                data = CSVHandler.select(table=table,
                                         filters=kwargs)
                
                return data

            elif operation == Query.DELETE: #route to delete operators
                CSVHandler.delete(table=table,
                                  filters=kwargs)

            elif operation == Query.INSERT: 
                CSVHandler.insert(table=table,
                                values=kwargs.get("values"))
        
            elif operation == Query.UPDATE:  #unwritten!
                pass
        
        elif table.type == "sql": #calling sql handlers
            if operation == Query.SELECT: #complete select operation
                data = SQLHandler.select(
                    table=table,
                    filters=kwargs
                )

                return data

            elif operation == Query.DELETE: #route to delete operators
                pass

            elif operation == Query.INSERT: 
                data = SQLHandler.insert(
                    table=table,
                    values=kwargs.get("values")
                )
        
            elif operation == Query.UPDATE: 
                pass

    else:
        t = f"Invalid table or operation. | {table} | {operation}"
        logger.critical(t)
        raise InvalidOperation(t)