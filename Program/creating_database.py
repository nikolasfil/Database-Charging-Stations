#!/bin/python
import sqlite3 as sq
import sys
import datetime


# https://www.tutorialspoint.com/sqlite/sqlite_python.htm


class Creation:
    def __init__(self, file):
        try:
            self.conn = sq.connect(file)
        except Exception as e:
            print(e)
            sys.exit()

        self.table_names = ['car','charger','charges','customer','fault','plan','reserves','station']


    def create_table(self,tablename):
        if tablename=='car':
            query = """CREATE TABLE car(
                    vin         STRING(7)       NOT NULL,
                    owner_id    INTEGER         NOT NULL,
                    connector   VARCHAR(255)    NOT NULL,
                    capacity    FLOAT           NOT NULL,
                    PRIMARY KEY (vin) ,
                    FOREIGN KEY (owner_id) REFERENCES customer(id) ON DELETE CASCADE ON UPDATE CASCADE);"""


        elif tablename=='charger':
            query = """CREATE TABLE charger (
                    location            STRING(8)       NOT NULL,
                    station_location    STRING(8)       NOT NULL,
                    type                STRING(2)       NOT NULL,
                    connector           VARCHAR(255)    NOT NULL,
                    PRIMARY KEY (location) ,
                    FOREIGN KEY (station_location) REFERENCES station(location) ON DELETE CASCADE ON UPDATE CASCADE);"""

        elif tablename=='charges':
            query = """ CREATE TABLE charges (
                        charger_location    STRING(8)   NOT NULL,
                        car_vin             STRING(7)   NOT NULL,
                        start_datetime      DATETIME    NOT NULL,
                        end_datetime        DATETIME    ,
                        charging_type       STRING(2)   NOT NULL,
                        energy              FLOAT       ,
                        PRIMARY KEY (charger_location,car_vin,start_datetime),
                        FOREIGN KEY (car_vin) REFERENCES car(vin) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (charger_location) REFERENCES charger(location) ON DELETE CASCADE ON UPDATE CASCADE);"""

        elif tablename=='customer':
            query = """CREATE TABLE customer (
                        id          INTEGER     NOT NULL,
                        fname       VARCHAR     NOT NULL,
                        lname       VARCHAR     NOT NULL,
                        birthdate   DATETIME    NOT NULL,
                        plan        VARCHAR     NOT NULL,
                        plan_start  DATE        NOT NULL,
                        plan_end    DATE        NOT NULL,
                        password    VARCHAR     NOT NULL,
                        salt        VARCHAR     NOT NULL,
                        PRIMARY KEY (id) ,
                        FOREIGN KEY (plan) REFERENCES plan(type) ON DELETE CASCADE ON UPDATE CASCADE); """

        elif tablename=='fault':
            query = """ CREATE TABLE fault (
                        charger_location    STRING(8)   NOT NUll,
                        error_code          INTEGER     NOT NUll,
                        occured_on          DATETIME    NOT NULL,
                        fixed_on            DATETIME ,
                        PRIMARY KEY (charger_location, error_code, occured_on),
                        FOREIGN KEY (charger_location) REFERENCES charger(location) ON DELETE CASCADE ON UPDATE CASCADE);"""

        elif tablename=='plan':
            query = """ CREATE TABLE plan (
                        type    VARCHAR(255)    NOT NULL,
                        price   FLOAT           NOT NULL,
                        ac_kwhr FLOAT           NOT NULL,
                        dc_kwhr FLOAT           NOT NULL,
                        PRIMARY KEY (type) );"""

        elif tablename=='reserves':
            query = """ CREATE TABLE reserves (
                        customer_id         INTEGER     NOT NULL,
                        charger_location    STRING(8)   NOT NULL,
                        start               DATETIME    NOT NULL,
                        end                 DATETIME    NOT NULL,
                        reserved_on         DATETIME    NOT NULL,
                        PRIMARY KEY (customer_id, charger_location, start) ,
                        FOREIGN KEY (customer_id) REFERENCES customer(id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (charger_location) REFERENCES charger(location) ON DELETE CASCADE ON UPDATE CASCADE);"""

        elif tablename=='station':
            query = """CREATE TABLE station (
                        location        STRING(8)   NOT NULL,
                        num_of_chargers INTEGER     NOT NULL,
                        PRIMARY KEY (location) );"""



        self.conn.execute(query)
        self.conn.commit()



    def main(self):

        for table in self.table_names:
            self.create_table(table)

        self.conn.close()



if __name__ == '__main__':
    # app = Creation('database_data')
    app = Creation('data.db')
    app.main()
