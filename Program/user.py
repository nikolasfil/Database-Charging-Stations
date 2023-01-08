#!/bin/python
import sqlite3 as sq
import bcrypt
from typing import Union
from statistics import fmean


class User:

    def __init__(self, file):
        self.conn = sq.connect(file)

    def hash_password(self, password, salt):
        return bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8'))

    def check_customer_passwd(self, user_id, user_password):
        query = "SELECT password from Customer where id={}".format(user_id)
        cursor_password = self.conn.execute(query)

        hashed = cursor_password.fetchone()[0].encode('utf-8')
        
        user_salt = self.get_salt().encode('utf-8')

        return bcrypt.checkpw(user_password.encode('utf-8'), hashed)


    def change_password(self, user_id, new_password):
        query = f"UPDATE Customer set password={new_password} where id={user_id}"

        self.conn.execute(query)

        self.conn.commit()


    #  -------------------------


    def customer_exists(self, customer_attributes):
        '''Returns true if the customer information we are trying to insert exist in the table'''

        query = """ SELECT COUNT(*) 
                    from customer 
                    where id={0}""".format(*customer_attributes)

        cursor = self.conn.execute(query)
        return cursor.fetchone()[0] == 1


    def get_salt(self):
        query = 'SELECT salt from Customer'
        cursor = self.conn.execute(query)
        # return [row[0] for row in cursor][0]
        return cursor.fetchone()[0]


    def get_car_vin(self,user_id):
        query_car = f"SELECT vin from car where owner_id={user_id}"
        cursor = self.conn.execute(query_car)
        return cursor.fetchall()

    def get_user_ids(self):
        '''gets a list with the user_ids'''

        # cursor is iterable(generator), it contains the columns of a row in a tuple
        cursor = self.conn.execute('SELECT id from Customer')
        return [row[0] for row in cursor]


    def get_new_user_id(self):
        user_id = 0
        user_ids = self.get_user_ids()

        while user_id in user_ids:
            user_id += 1
        return user_id


    def get_user_id(self,customer_attributes,car_attributes):
        query = """ SELECT id 
                    from customer join car on id=owner_id
                    where fname={1} and lname={2} and birthdate={3} and plan={4} and plan_start={5} and plan_end={6} and password={7} and vin{9} and connector={11} and capacity={12}""".format(*customer_attributes,*car_attributes)

        cursor = self.conn.execute(query)
        return cursor.fetchone()[0]


    def get_user_info(self, user_id):
        '''Returns a string with customer and car table info of a user id'''

        query_customer = "SELECT * from customer where id={};".format(user_id)

        cursor_user = self.conn.execute(query_customer)


        query_car = "SELECT * from car where owner_id={};".format(user_id)

        cursor_car = self.conn.execute(query_car)


        return cursor_user,cursor_car

    def get_customer_id(self, customer_attributes):
        if self.customer_exists(customer_attributes):
            # https://stackoverflow.com/questions/7568627/using-python-string-formatting-with-lists

            query = """ SELECT id
                        from customer
                        where fname={1} and lname={2} and birthdate={3} and plan={4} and plan_start={5} and plan_end={6}""".format(*customer_attributes)

            cursor = self.conn.execute(query)

            return cursor.fetchone()[0]

        return False

    def get_customer_expenses(self, customer_id:str, start_datetime:Union[str,None]=None, end_datetime:Union[str,None]=None) -> float:
        '''
        Get the expenses of a single customer for a certain date range or lifetime
        '''

        start = f"and ch.start_datetime > '{start_datetime}'"
        end = f"and ch.end_datetime < '{end_datetime}'"

        query = f'''
        select sum(energy * case when ch.charging_type = 'ac' then p.ac_kwhr else p.dc_kwhr end) as expense
        from charges as ch
        join car on ch.car_vin = car.vin
        join customer as cu on car.owner_id = cu.id
        join plan as p on cu.plan = p.type
        where cu.id = {customer_id}
        {start if start_datetime is not None else ''}
        {end if end_datetime is not None else ''}
        '''

        cursor = self.conn.execute(query)
        return cursor.fetchone()


    #  -------------------------

    def insert_customer(self, customer_attributes: list):

        query = "INSERT INTO customer(id,fname,lname,birthdate,plan,plan_start,plan_end,password,salt) VALUES (" + ','.join(
            [str(i) for i in customer_attributes]) + ")"

        self.conn.execute(query)

        self.conn.commit()

    #  -------------------------

