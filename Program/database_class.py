import sqlite3 as sq
from typing import Union
from datetime import datetime, timedelta
from statistics import fmean

# need to check the vin of cars too cause it is a primary/unique key for the cars

class DataBase:

    def __init__(self, file):
        self.conn = sq.connect(file)

    def get_free_chargers(self, connector:bool=False) -> list[tuple[str, int]]:
        '''
            Get number of free chargers by type
        '''


        if connector == False:
            item = 'type'
        else:
            item = 'connector'


        query = f'''
        select {item}, count({item})
        from (
            select location, connector, type
            from charger
            EXCEPT
            select distinct a.location, connector, type
            from charger as a join charges as b
            on a.location = b.charger_location
            where end_datetime is null
        )
        group by {item}
        '''

        cursor = self.conn.execute(query)
        return list(cursor)

    def find_available_chargers(self, vin:str) -> list:
        '''
        Find available chargers of certain type and connector
        '''

        query = f'''
        select connector from car
        where vin = {vin}
        '''

        cursor = self.conn.execute(query)
        connector = cursor.fetchone()[0]

        query = f'''
        select location
        from charger
        where connector = '{connector}'
        EXCEPT
        select distinct a.location
        from charger as a join charges as b
        on a.location = b.charger_location
        where end_datetime is null
        '''

        cursor = self.conn.execute(query)
        return cursor.fetchall()

    def get_charging_sessions(self, active:bool=True) -> int:
        '''
            Get charging sessions, either total or currently active
        '''

        query = 'select count(car_vin) from charges'

        if active == True:
            query += ' where end_datetime is null'

        cursor = self.conn.execute(query)
        return cursor.fetchone()[0]

    def get_total_energy_served(self) -> int:
        '''
            Get total energy served
        '''

        query = 'select sum(energy) from charges'
        cursor = self.conn.execute(query)
        return cursor.fetchone()[0]

    def get_station_revenue(self, station:Union[str,None]=None) -> list:
        '''
            Get all or specific station revenue
        '''

        query = '''
        select ch.charger_location,
        sum(energy * case when ch.charging_type = 'ac' then p.ac_kwhr else p.dc_kwhr end) as income
        from charges as ch
        join car on ch.car_vin = car.vin
        join customer as cu on car.owner_id = cu.id
        join plan as p on cu.plan = p.type
        '''

        if station == None:
            query += " group by ch.charger_location "
        else:
            query += f" where ch.charger_location = {station} "

        query+=' order by income desc'
        cursor = self.conn.execute(query)
        return cursor.fetchall()

    def get_active_failures(self) -> list:
        '''
            Get failures currently active on all stations
        '''

        # query = 'select * from fault where fixed_on is null'
        query = 'select * from fault where fixed_on is null order by occured_on'
        cursor = self.conn.execute(query)
        return cursor.fetchall()


    def get_energy_consumption(self, month:Union[str, None]=None) -> list:
        '''
            Get energy consumption for all stations for a given month
            If month == None, use current month
        '''

        date = "now" if month == None else f"{month+'-01'}"

        query = f'''
        select sum(energy) as total_energy
        from charges
        where strftime("%Y-%m", start_datetime) = strftime("%Y-%m", date('{date}'))
        group by charger_location
        order by total_energy desc
        '''

        cursor = self.conn.execute(query)
        return cursor.fetchall()

    def get_hourly_usage(self, charging_station:Union[str,None]=None) -> list:
        '''
        Get hourly usage for the whole system or a specific station, ranked in descending order
        '''

        charger = f"where charger_location = {charging_station}"

        query = f'''
        select charger_location,count(*) as count, strftime("%H", start_datetime) as hour
        from charges
        {charger if charging_station is not None else ''}
        group by hour
        order by count desc
        '''

        cursor = self.conn.execute(query)
        return cursor.fetchall()

    def get_mean_time_between_failures(self, charging_station:Union[str,None]=None) -> float:
        '''
        Get mean time (in seconds) between failures for the whole system or a specific station
        '''

        station = f"where charging_station = {charging_station}"

        query = f"select occured_on from fault {station if charging_station is not None else ''} order by occured_on"

        data = self.conn.execute(query).fetchall()
        data = [datetime.strptime(x[0], "%Y-%m-%d %H:%M:%S") for x in data]

        diffs = []
        for i in range(1, len(data)):
            diffs.append((data[i]-data[i-1]).total_seconds())

        return fmean(diffs)



    def car_exists(self, car_attributes):
        '''Returns true if the car information we are trying to insert exist in the table'''

        query = """ SELECT COUNT(*)
                    from car where vin={0}""".format(*car_attributes)

        cursor = self.conn.execute(query)

        # return [row[0] for row in cursor][0] == 1
        return cursor.fetchone()[0] == 1


    # ------ Inserts ---------

    def insert_car(self, car_attributes: list):

        query = "INSERT INTO car(vin,owner_id,connector,capacity) VALUES (" + ','.join(
            [str(i) for i in car_attributes]) + ")"

        self.conn.execute(query)

        self.conn.commit()

    def insert_charge(
        self,
        charger_location:str,
        vin:str,
        start:datetime,
        type:str,
        energy:Union[float,None]=None,
        end:Union[datetime, None]=None
    ) -> bool:
        '''
        Insert new charging session into database
        Return True if charger is available and insertion can be made, otherwise return False
        '''

        query = f'''
        select * from charges
        where charger_location = {charger_location} and end_datetime is null'
        '''

        cursor = self.conn.execute(query)
        if cursor.rowcount > 0: return False

        if energy is not None and end is not None:
            query = f'''
            INSERT INTO charges
            ("charger_location", "car_vin", "start_datetime", "end_datetime", "charging_type", "energy")
            VALUES ({charger_location}, {vin}, '{start}', '{end}', {type}, {energy})
            '''
        elif energy is None:
            query = f'''
            INSERT INTO charges
            ("charger_location", "car_vin", "start_datetime", "end_datetime", "charging_type")
            VALUES ({charger_location}, {vin}, '{start}', '{end}', {type})
            '''
        elif type is None:
            query = f'''
            INSERT INTO charges
            ("charger_location", "car_vin", "start_datetime", "end_datetime", "energy")
            VALUES ({charger_location}, {vin}, '{start}', '{end}', {energy})
            '''

        cursor = self.conn.execute(query)
        self.conn.commit()

        return True if cursor.rowcount == 1 else False

    def insert_fault(
        self,
        charger_location:str,
        error_code:str,
        occured_on:datetime,
        fixed_on:Union[datetime,None]=None
    ) -> bool:
        '''
        Insert new charger fault into database
        Return True on successful insert, otherwise return False
        '''

        query = ''

        if fixed_on is not None:
            query = f'''
            INSERT INTO fault
            VALUES ({charger_location}, {error_code}, '{occured_on}', '{fixed_on}')
            '''

        else:
            query = f'''
            INSERT INTO fault
            ("charger_location", "error_code", "occured_on")
            VALUES ({charger_location}, {error_code}, '{occured_on}')
            '''

        cursor = self.conn.execute(query)
        self.conn.commit()

        return True if cursor.rowcount == 1 else False

    def insert_reserve(
        self,
        customer_id:str,
        charger_location:str,
        start:datetime,
        end:datetime,
        reserved_on:datetime
    ) -> bool:
        '''
        Insert new reservation into database
        Return True if charger is available and reservation can be made, otherwise return False
        '''

        query = f'''
        select * from reserves
        where charger_location = {charger_location}
        and (
            start < '{start}' and '{start}' < end or
            start < '{end}' and '{end}' < end or
            '{start}' < start and start < '{end}' or
            '{start}' < end and end < '{end}'
        )
        '''

        cursor = self.conn.execute(query)
        if cursor.rowcount > 0: return False

        query = f'''
        INSERT INTO reserves
        VALUES ({customer_id}, {charger_location}, '{start}', '{end}', '{reserved_on}')
        '''

        cursor = self.conn.execute(query)
        self.conn.commit()

        return True if cursor.rowcount == 1 else False


    # --------- UPdates -------------

    def update_charge(
        self,
        charger_location:str,
        vin:str,
        start:datetime,
        energy:Union[float,None]=None,
        end:Union[datetime, None]=None
    ) -> bool:

        '''
        Update charging session in database
        Return True on successful update, otherwise return False
        '''

        query = f'''
        UPDATE charges
        SET energy={energy}, end='{end}'
        WHERE charger_location={charger_location} and vin={vin} and start='{start}'
        '''

        cursor = self.conn.execute(query)
        self.conn.commit()

        return True if cursor.rowcount == 1 else False


    def update_fault(
        self,
        charger_location:str,
        error_code:str,
        occured_on:datetime,
        fixed_on:Union[datetime,None]=None
    ) -> bool:
        '''
        Update charger fault in database
        Return True on successful update, otherwise return False
        '''

        query = f'''
        UPDATE fault
        SET fixed_on='{fixed_on}'
        WHERE charger_location={charger_location} and error_code={error_code} and occured_on='{occured_on}'
        '''

        cursor = self.conn.execute(query)
        self.conn.commit()

        return True if cursor.rowcount == 1 else False
