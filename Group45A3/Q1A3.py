import sqlite3
import time
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
import sys
import os

def uninformed(c):

    c.execute('PRAGMA automatic_index=OFF')
    
    c.execute('DROP TABLE IF EXISTS Customers_new')
    c.execute('CREATE TABLE Customers_new (customer_id text, customer_postal_code integer)')
    c.execute('INSERT INTO Customers_new SELECT customer_id, customer_postal_code FROM Customers')
    c.execute('DROP TABLE Customers')
    c.execute('ALTER TABLE Customers_new RENAME TO Customers')
    
    c.execute('DROP TABLE IF EXISTS Sellers_new')
    c.execute('CREATE TABLE Sellers_new (seller_id text, seller_postal_code integer)')
    c.execute('INSERT INTO Sellers_new SELECT seller_id, seller_postal_code FROM Sellers')
    c.execute('DROP TABLE Sellers')
    c.execute('ALTER TABLE Sellers_new RENAME TO Sellers')
    
    c.execute('DROP TABLE IF EXISTS Orders_new')
    c.execute('CREATE TABLE Orders_new (order_id text, customer_id text)')
    c.execute('INSERT INTO Orders_new SELECT order_id, customer_id FROM Orders')
    c.execute('DROP TABLE Orders')
    c.execute('ALTER TABLE Orders_new RENAME TO Orders')
    
    c.execute('DROP TABLE IF EXISTS Order_items_new')
    c.execute('CREATE TABLE Order_items_new (order_id text, order_item_id integer, product_id text, seller_id text)')
    c.execute('INSERT INTO Order_items_new SELECT order_id, order_item_id, product_id, seller_id FROM Order_items')
    c.execute('DROP TABLE Order_items')
    c.execute('ALTER TABLE Order_items_new RENAME TO Order_items')

def self_optimized(c):

    c.execute('PRAGMA automatic_index=ON')
    c.execute('DROP TABLE IF EXISTS Customers_new')
    c.execute('CREATE TABLE Customers_new (customer_id text PRIMARY KEY, customer_postal_code integer)')
    c.execute('INSERT INTO Customers_new SELECT * FROM Customers')
    c.execute('DROP TABLE Customers')
    c.execute('ALTER TABLE Customers_new RENAME TO Customers')

    c.execute('DROP TABLE IF EXISTS Sellers_new')
    c.execute('CREATE TABLE Sellers_new (seller_id text PRIMARY KEY, seller_postal_code integer)')
    c.execute('INSERT INTO Sellers_new SELECT * FROM Sellers')
    c.execute('DROP TABLE Sellers')
    c.execute('ALTER TABLE Sellers_new RENAME TO Sellers')

    c.execute('DROP TABLE IF EXISTS Orders_new')
    c.execute('CREATE TABLE Orders_new (order_id text PRIMARY KEY, customer_id text, FOREIGN KEY(customer_id) REFERENCES Customers(customer_id))')
    c.execute('INSERT INTO Orders_new SELECT * FROM Orders')
    c.execute('DROP TABLE Orders')
    c.execute('ALTER TABLE Orders_new RENAME TO Orders')

    c.execute('DROP TABLE IF EXISTS Order_items_new')
    c.execute('CREATE TABLE Order_items_new (order_id text, order_item_id integer, product_id text, seller_id text, PRIMARY KEY(order_id, order_item_id, product_id, seller_id), FOREIGN KEY(seller_id) REFERENCES Sellers(seller_id), FOREIGN KEY(order_id) REFERENCES Orders(order_id))')
    c.execute('INSERT INTO Order_items_new SELECT * FROM Order_items')
    c.execute('DROP TABLE Order_items')
    c.execute('ALTER TABLE Order_items_new RENAME TO Order_items')

def user_optimized(c):
    c.execute('PRAGMA automatic_index=ON')
    

    c.execute('DROP TABLE IF EXISTS Customers_new')
    c.execute('DROP TABLE IF EXISTS Sellers_new')
    c.execute('DROP TABLE IF EXISTS Orders_new')
    c.execute('DROP TABLE IF EXISTS Order_items_new')
    c.execute('CREATE TABLE Customers_new (customer_id text PRIMARY KEY, customer_postal_code integer)')
    c.execute('CREATE TABLE Sellers_new (seller_id text PRIMARY KEY, seller_postal_code integer)')
    c.execute('CREATE TABLE Orders_new (order_id text PRIMARY KEY, customer_id text, FOREIGN KEY(customer_id) REFERENCES Customers_new(customer_id))')
    c.execute('CREATE TABLE Order_items_new (order_id text, order_item_id integer, product_id text, seller_id text, PRIMARY KEY(order_id, order_item_id, product_id, seller_id), FOREIGN KEY(seller_id) REFERENCES Sellers_new(seller_id), FOREIGN KEY(order_id) REFERENCES Orders_new(order_id))')
    
    c.execute('INSERT INTO Customers_new SELECT * FROM Customers')
    c.execute('INSERT INTO Sellers_new SELECT * FROM Sellers')
    c.execute('INSERT INTO Orders_new SELECT * FROM Orders')
    c.execute('INSERT INTO Order_items_new SELECT * FROM Order_items')
    
    c.execute('DROP TABLE Customers')
    c.execute('DROP TABLE Sellers')
    c.execute('DROP TABLE Orders')
    c.execute('DROP TABLE Order_items')
    
    c.execute('ALTER TABLE Customers_new RENAME TO Customers')
    c.execute('ALTER TABLE Sellers_new RENAME TO Sellers')
    c.execute('ALTER TABLE Orders_new RENAME TO Orders')
    c.execute('ALTER TABLE Order_items_new RENAME TO Order_items')
    
    c.execute('CREATE INDEX customer_postal_code_idx ON Customers(customer_postal_code)')
    c.execute('CREATE INDEX seller_postal_code_idx ON Sellers(seller_postal_code)')
    c.execute('CREATE INDEX order_customer_id_idx ON Orders(customer_id)')
    c.execute('CREATE INDEX order_seller_id_idx ON Order_items(seller_id)')

def main():
    databases = ['../Group45A3_DBs/A3Small.db', '../Group45A3_DBs/A3Medium.db', '../Group45A3_DBs/A3Large.db']

    uninformed_arr = []
    self_optimized_arr = []
    user_optimized_arr = []
    query1 = """
    SELECT customer_postal_code 
    FROM Customers 
    ORDER BY RANDOM() 
    LIMIT 1
    """
    query2 = """
    SELECT COUNT(DISTINCT o.order_id)
    FROM Customers c, Orders o, Order_items oi
    WHERE c.customer_id = o.customer_id AND 
    o.order_id = oi.order_id AND
    c.customer_postal_code = ?
    GROUP BY c.customer_postal_code
    HAVING COUNT(*) > 1;
    """


    for database in databases:


        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute(query1)
        customer_postal_code = str(c.fetchone()[0])
        
        uninformed(c)
        start_time = time.time()
        for i in range(50):
            c.execute(query2, (customer_postal_code,))
        end_time = time.time()
        total_time1 = end_time - start_time
        uninformed_arr.append(total_time1*20)

        conn.close()
        conn = sqlite3.connect(database)
        c = conn.cursor()

        self_optimized(c)
        start_time = time.time()
        for i in range(50):
            c.execute(query2, (customer_postal_code,))
        end_time = time.time()
        total_time2 = end_time - start_time
        self_optimized_arr.append(total_time2*20)

        conn.close()
        conn = sqlite3.connect(database)
        c = conn.cursor()

        user_optimized(c)
        start_time = time.time()
        for i in range(50):
            c.execute(query2, (customer_postal_code,))
        end_time = time.time() 
        total_time3 = end_time - start_time
        user_optimized_arr.append(total_time3*20)

        conn.close()

    x = ['SmallDB', 'MediumDB', 'LargeDB']

    uninformed_data = np.array(uninformed_arr)
    self_optimized_data = np.array(self_optimized_arr)
    user_optimized_data = np.array(user_optimized_arr)

    plt.bar(x, uninformed_data, color='gold')
    plt.bar(x, self_optimized_data, bottom=uninformed_data, color='lightskyblue')
    plt.bar(x, user_optimized_data, bottom=uninformed_data+self_optimized_data, color='tomato')
    plt.title('Query 1 (runtime in ms)')
    plt.legend(["uninformed", "self optimized", "user optimized"])
    plt.show()
    plt.savefig('image.png')

    print(np.array(uninformed_arr))
    print(np.array(self_optimized_arr))
    print(np.array(user_optimized_arr))

main()