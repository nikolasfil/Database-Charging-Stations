#!/bin/python
import sqlite3 as sq
import bcrypt
import sys
import datetime


# https://www.tutorialspoint.com/sqlite/sqlite_python.htm
# Τα αρχεια us_firstname και us_lastname αποκτηθηκαν απο το github project : 

class Filling:
    def __init__(self, file):
        try:
            self.conn = sq.connect(file)
        except Exception as e:
            print(f'Database Data must be in the same folder\n{e}')
            sys.exit()

        self.salt = bcrypt.gensalt()
        self.quantity=10
        self.table_names = ['car','charger','charges','customer','fault','plan','reserves','station']


        self.init_options()
        self.init_columns()


    # ------------Initialization Functions--------------- 

    def init_options(self):
        self.options_plantype=["'Basic'","'Standard'","'Premium'"]
        self.options_price=[10,20,30]
        self.options_ac_kwhr=[3,2,1]
        self.options_dc_kwhr=[3,2,1]
        self.options_current_type=["'ac'","'dc'"]
        self.options_ac_connector = ['J1772','Mennekes','GB/T(AC)','Tesla']
        self.options_dc_connector = ['CCS1','CCS2','CHAdeMO','GB/T(DC)']


        self.options_firstdate=[]
        self.options_seconddate=[]
        self.options_station_locations=['8GC37QPP','8GC36PWP','8GC36P4G','8GC32Q3R','8GC42GFM','8G93QM2G','8G94PC3H','8G94H2XQ','8G95Q246']
        self.options_charger_locations=[]

    
    def init_columns(self):
        self.columns_car        = ['vin','owner_id','connector','capacity']
        self.columns_charger    = ['location','station_location','type','connector','working','occupied']
        self.columns_charges    = ['charger_location','car_vin','start_datetime','end_datetime','charging_type','energy']
        self.columns_customer   = ['id','fname','lname','birthdate','plan','plan_start','plan_end','password','salt']
        self.columns_fault      = ['charger_location','error_code','occured_on','fixed_on']
        self.columns_plan       = ['type','price','ac_kwhr','dc_kwhr']
        self.columns_reserves   = ['customer_id','charger_location','start','duration','reserved_on']
        self.columns_station    = ['location','num_of_chargers']

        self.columns = [self.columns_car,self.columns_charger,self.columns_charges,self.columns_customer,self.columns_fault,self.columns_plan,self.columns_reserves,self.columns_station]
    

    # ---------- Using Data ----------  

    def clearing(self,tablename:str):
        '''clears the specific tablename from the values, but does not delete the columns'''
        self.conn.execute(f'DELETE FROM {tablename}')
        self.conn.commit()

    def use_data(self,cols,values,i):
        return ",".join([f'{values[i%len(table[col])]}' for col in cols] )

    def insert_data(self,table_name,columns,values):
        for data in values:

            command = f"INSERT INTO {table_name}({','.join(columns)}) VALUES ({','.join(list(map(str,data)))})"
            self.conn.execute(command)
        
        self.conn.commit()        


    # ---------- Creating Datetimes ----------  

    def insert_random_data_datetime_info(self,start_year=2020, quantity=5):
        # early batch of random data, we can specify it later on 
        count = 0
        for y in range(start_year,start_year+1+self.quantity//365):
            for m in range(1,13):
                for d in range(1,32):
                    if self.check_date(f"{y}-{m}-{d}"):

                        self.options_firstdate.append(f"'{y}-{m}-{d}'")
                        count+=1
                        if count+2 == quantity:
                            return 
                        self.options_seconddate.append(f"'{y}-{m}-{d}'")


    def check_date(self, date_string):
        '''date_string is a string that contains y-m-d and valid date datetime object'''

        if date_string.count('-')!=2:
            return False

        datelist=list(map(int, date_string.split('-')))
        try:
            newDate = datetime.datetime(datelist[0], datelist[1], datelist[2])
            return True
        except ValueError:
            return False

    # ---------- Creating Data ----------  

    # ---------- Car ----------  
    
    # https://mockaroo.com/?fbclid=IwAR1fwiJMbliVzvCWkQuErPv0Xy184HjxsWThF4Ft5AqUM0xzHBRyi7fhevM

    # ---------- Charger ----------  


    def create_data_charger(self,quantity=10):
        '''location,station_location,type,connector,working,occupied'''
        chargers = []
        for j in range(len(self.options_station_locations)):
            for i in range(quantity%26):
                typ = ["ac","dc"][(i+j)%2]
                if typ == "ac":
                    model = self.options_ac_connector[(i+j)%4]
                if typ == "dc":
                    model = self.options_dc_connector[(i+j)%4]

                location = f'{self.options_station_locations[j]}+{chr(ord("A"))}{chr(ord("A")+i)}'

                chargers.append( (f"'{location}'", f"'{self.options_station_locations[j]}'",f"'{typ}'",f"'{model}'",True,False ))          

        return chargers

    # ---------- Customer ----------  

    def hashing_password(self,password):
        return self.stringing_from_double(bcrypt.hashpw(password.encode('utf-8'),self.salt))

    def stringing_from_double(self,string):
        return f"'{str(string)[2:-1]}'"


    def create_data_customer(self,quantity = 5):
        '''id, fname, lname, birthdate, plan, plan_start, plan_end, password, salt'''
        fname,lname = self.get_names(quantity)

        # fix random bdates make a function

        return [ ( i+1, fname[i], lname[i] , "'2001-01-01'" , self.options_plantype[i%len(self.options_plantype)], "'2020-01-01'", "'2021-01-01'" , self.hashing_password(fname[i]) ,self.stringing_from_double(self.salt)) for i in range(quantity)]
    

    def create_data_admin(self):
        '''id, fname, lname, birthdate, plan, plan_start, plan_end, password, salt'''
        
        return [ ( 0,"'admin'" ,"'admin'" , "'2001-01-01'" , "'Premium'", "'1900-01-01'", "'3021-01-01'" , self.hashing_password("'admin'") ,self.stringing_from_double(self.salt))]

    # ---------- Plan ----------  

    
    def create_data_plan(self):
        '''type, price, ac_kwhr, dc_kwhr'''
         
        return [ (self.options_plantype[i], self.options_price[i], self.options_ac_kwhr[i], self.options_dc_kwhr[i]) for i in range(len(self.options_plantype)) ]


    # ---------- Station ----------  


    def create_data_station(self,quantity=10):
        '''location, num_of_chargers'''

        return [ (f"'{i}'",quantity%26) for i in self.options_station_locations] 


    # ---------- Names ----------  

    def get_names(self,quantity=5):
        firstname = []
        lastname = []

        with open('us_firstname.txt','r') as f:
            for i in range(quantity):
                name = f.readline().strip('\n')
                firstname.append(f"'{name}'")

        with open('us_lastname.txt','r') as f:
            for i in range(quantity):
                name =f.readline().strip('\n')
                lastname.append(f"'{name}'")
        return firstname,lastname


    # ---------- From Files ----------

    def load_data(self,filename):
        count = 0
        with open(filename) as f:
            for i in f:
                self.conn.execute(i)
                count+=1
                if count == self.quantity:
                    break
            self.conn.commit()


    # ---------- Main ----------

    def main(self):
          

        for table in self.table_names:
            self.clearing(table)

        print('Table Created and Cleared')

        
        self.insert_data('customer',self.columns_customer,self.create_data_admin())
        self.insert_data('customer',self.columns_customer,self.create_data_customer(10))
        print('Customer Data inserted')
        
        self.insert_data('plan',self.columns_plan,self.create_data_plan())
        print('Plan Data inserted')
        
        self.quantity = 10
        self.load_data('sqldata/car.sql')
        print('Car Data inserted')

        self.insert_data('charger',self.columns_charger,self.create_data_charger())
        print('Charger Data inserted')
        

        self.insert_data('station',self.columns_station,self.create_data_station())
        print('Station Data inserted')

        self.conn.close()



if __name__ == '__main__':
    app = Filling('data.db')
    app.main()