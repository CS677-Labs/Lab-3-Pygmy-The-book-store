import sqlite3
from sqlite3 import Error
from datetime import datetime
import logging
import os

logging.basicConfig(filename='orders.log', level=logging.DEBUG)


def log_query(query):
    """
    Function to log every query that is executed on the orders DB.
    """
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "logs", "query_log.txt"), 'a') as f:
        f.write(query+'\n')


def create_connection():
    db_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
    db_file = os.path.join(db_dir, "orders.db")
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.set_trace_callback(log_query)
    except Error as e:
        logging.error("Failed to open connection to sqlite DB. Error - " + str(e))
    
    return conn



def create_table(dbConnection) :
    create_table_sql = """ CREATE TABLE IF NOT EXISTS ORDERS (
        OrderId integer PRIMARY KEY,
        OrderDate text NOT NULL,
        ItemNum integer NOT NULL,
        OrderStatus text NOT NULL
    );"""

    try :
        cursor = dbConnection.cursor()
        cursor.execute(create_table_sql)
        return True
    except Error as e :
        logging.error("Failed to create table. Error - " + str(e))
        return False



# Function to create a new row in orders.db
def appendOrderDetailsToDb(itemNum, orderStatus) :
    now = datetime.now()
    orderDate = now.strftime("%b-%d-%Y %H:%M:%S")
    columnValues = (orderDate, itemNum, orderStatus)

    insert_sql = '''INSERT INTO ORDERS (OrderDate, ItemNum, OrderStatus)
                    VALUES(?,?,?);'''

    dbConnection = create_connection()
    with dbConnection :
        if create_table(dbConnection) is True :
            try :
                cursor = dbConnection.cursor()
                cursor.execute(insert_sql, columnValues)
                dbConnection.commit()
                logging.info("Inserted orderDate - {}, ItemNum - {}, orderStatus - {} to the DataBase".format(orderDate, itemNum, orderStatus))
                return { "OrderId" : cursor.lastrowid, "Date" : orderDate, "ID" : itemNum, "Order status" : orderStatus} 
            except Error as e :
                logging.error("Unable to insert data to the Database. Error - " + str(e))
                return None


# Function to add new row to orders.db
def insertRowToDB(orderDetails) :
    orderId = orderDetails['OrderId']
    orderDate = orderDetails['Date']
    itemNum = orderDetails['ID']
    orderStatus = orderDetails['Order status']
    
    columnValues = (orderId, orderDate, itemNum, orderStatus)

    insert_sql = '''INSERT INTO ORDERS (OrderId, OrderDate, ItemNum, OrderStatus)
                    VALUES(?,?,?,?);'''

    dbConnection = create_connection()
    with dbConnection :
        if create_table(dbConnection) is True :
            try :
                cursor = dbConnection.cursor()
                cursor.execute(insert_sql, columnValues)
                dbConnection.commit()
                logging.info("Inserted orderDate - {}, ItemNum - {}, orderStatus - {} to the DataBase".format(orderDate, itemNum, orderStatus))
                return { "OrderId" : cursor.lastrowid, "Date" : orderDate, "ID" : itemNum, "Order status" : orderStatus} 
            except Error as e :
                logging.error("Unable to insert data to the Database. Error - " + str(e))
                return None



# Function to fetch all rows from orders.db
def getAllRowsFromDb() :
    select_sql = '''SELECT OrderID as OrderId, OrderDate, ItemNum, OrderStatus FROM ORDERS;'''
    dbConnection = create_connection()
    with dbConnection :
        try :
            cursor = dbConnection.cursor()
            cursor.execute(select_sql)
            rows = cursor.fetchall()
            return rows
        except Error as e :
            logging.error("Unable to insert data to the Database. Error - " + str(e))
            return None


def resync_database(data) :
    columnValues = data
    insert_sql = '''INSERT INTO ORDERS (OrderId, OrderDate, ItemNum, OrderStatus)
                    VALUES(?,?,?,?);'''

    dbConnection = create_connection()
    with dbConnection :
        if create_table(dbConnection) is True :
            try :
                cursor = dbConnection.cursor()
                cursor.executemany(insert_sql, columnValues)
                dbConnection.commit()
                logging.info(f"Inserted {len(columnValues)} rows into orders.db")
                return 
            except Error as e :
                logging.error("Unable to insert data to the Database. Error - " + str(e))
                return
    return