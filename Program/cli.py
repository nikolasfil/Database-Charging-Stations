#!/bin/python
import platform,os,sys
import datetime

from database_class import DataBase
from user import User


class App:
    def __init__(self,file):

        # is used to escape to the menu after executing an action in order not to clear the screen right away
        self.is_inside_options = False

        # there is no need for checking if we open it from the Program folder, or from main.py
        self.database   = DataBase(file)
        self.user       = User(file)

        # initialize the user_id  
        self.user_id = None


    # --------------- Functions for Checking ---------------


    def date_check(self, date_string):
        '''date_string is a string that contains y-m-d and valid date datetime object'''

        if date_string.count('-')!=2:
            return False

        datelist=list(map(int, date_string.split('-')))
        try:
            newDate = datetime.datetime(datelist[0], datelist[1], datelist[2])
            return True
            # return newDate
        except ValueError:
            return False

    def datetime_check(self,datetime_string):
        '''datetime_string is a string that contains y-m-d h:m:s and valid date datetime object'''

        if datetime_string.count('-')!=2 or datetime_string.count(":")!=2:
            return False
        
        datelist=list(map(int, datetime_string.split(' ')[0].split('-')))
        timelist=list(map(int, datetime_string.split(' ')[1].split(':')))

                

        try:
            newDate = datetime.datetime(*datelist,*timelist)
            return True
            # return newDate
        except ValueError:
            return False

    def prompt_invalid_check(self,variable,alpha=False,choices=None,date=False,num=False,datetime=False):
        '''checks the different kind of prompts'''

        if not variable:
            return True
        if alpha :
            return not variable[1:-1].isalpha()
        if choices is not None:
            return variable[1:-1] not in choices
        if date:
            return not self.date_check(variable[1:-1])
        if num:
            return not variable[1:-1].isnumeric()
        if datetime:
            return not self.datetime_check(variable[1:-1])
            
        return not variable 


    # --------------- login Functions ---------------


    def login(self):
        '''login with id'''
 
        login_prompt_dict = {}
        print('-'*10)
        login_prompt_dict['UserID']   = input(f"{'User Id: ':<10}"+"| ")            
        login_prompt_dict['Password'] = input(f"{'Password: ':<10}"+"| ")
        print('-'*10)

        # καλουμε την συναρτηση prompt_check() για να ελεγξουμε την εγκυροτητα των δεδομενων 
        status, message = self.login_prompt_check(login_prompt_dict)

        if status:
            self.user_id = login_prompt_dict['UserID']

        return message



    def login_prompt_check(self,prompt_dict):
        
        # Η injection_proof() χρησιμοποιειται για τον καθαρισμο των input 

        prompt_dict={i:self.injection_proof(v) for i,v in prompt_dict.items()}

        if  self.prompt_invalid_check(prompt_dict['UserID'],num=True):
            return False,'\nPlease Provide valid user id'
            
        prompt_dict['UserID']=int(prompt_dict['UserID'][1:-1])

        if prompt_dict['UserID'] not in self.user.get_user_ids():
            return False,'\nUser is not registered. Please Sign UP '
            
        if self.prompt_invalid_check(prompt_dict['Password']):
            return False,'\nPassword: Invalid Input'

        # check the password against the one in the database
        if not self.user.check_customer_passwd(prompt_dict['UserID'], prompt_dict['Password']):
            return False,'\n Wrong Password'
            
        # give the global variable user_id the user_id collected by the user
        self.user_id = prompt_dict['UserID']
        
        return True, f'\nLogin to user {prompt_dict["UserID"]} successful\n'


    #  --------------- General for user --------------- 


    def logout(self):
        '''Logging out '''

        # nullify the global user_id
        self.user_id = None
        return '\nLogout successful\n\n'

    def info(self):
        '''Show information about the user'''
 
        cursor_user , cursor_car = self.user.get_user_info(self.user_id)

        customer_op = list(map(lambda x: x[0],cursor_user.description))

        customer_info_op = '|'.join(f' {customer_op[i]}: {v} ' for i, v in enumerate(list(cursor_user)[0][:-2]))

        car_op = list(map(lambda x: x[0],cursor_car.description))

        cars_info_op = '\n'.join(['|'.join(f' {car_op[i]}: {v:5} ' for i, v in enumerate(k)) for k in list(cursor_car)])

        return f'{"_" * len(customer_info_op)}'.join(
            ['', '\n\n' + customer_info_op + '\n', "\n\n\nCar Info\n", '\n\n' + cars_info_op + '\n']) + '_' * len(
            customer_info_op)
       
    def general_info(self):
        '''Στατιστικα στοιχεια για τον χρηστη '''        


        expenses = self.user.get_customer_expenses(self.user_id)

        customer_expenses = f"Bill: {expenses[0]}"        

        general_list = [customer_expenses]

        length = 40
        result = ''

        for info in general_list:
            result += f'{"-"*length}\n{info}\n{"-"*length}\n\n'

        return result
        

    # --------------- Sign up functions ---------------


    def signup(self):
        '''sign up Menu'''
        
        signup_prompt_dict={}
        status, result = self.signup_prompts(signup_prompt_dict)

        if not status:
            return result

        customer_attributes, car_attributes = result[0],result[1]


        if not customer_attributes and not car_attributes:
            return '\nInvalid Input\n'
            
        user_id = customer_attributes[0]

        # Ελεγχουμε αμα τα στοιχεια του χρηστη υπαρχουν 
        customer_exists_var = self.user.customer_exists(customer_attributes)
        car_exists_var = self.database.car_exists(car_attributes)


        if customer_exists_var and car_exists_var:
            return f'\n\nA User:{user_id} with that car already exists\n'

        elif customer_exists_var and not car_exists_var:

            self.database.insert_car(car_attributes)
            return f'\n\nAdding a new car to the user: {user_id} \n\n'
        
        elif not customer_attributes and car_exists_var:
            self.user.insert_customer(customer_attributes)
            return f'\n\nUser {user_id} signed up succesfully, but car with vin: {car_attributes[0]} already exists \n\n'

        else:

            self.database.insert_customer(customer_attributes)
            self.database.insert_car(car_attributes)
            self.user_id=user_id
            return f'\n\nSign Up successful with user id: {user_id}\n'

    def signup_prompts(self,signup_prompt_dict):
        '''all the inputs for the signup process'''

        print('-'*34)
        signup_prompt_dict['ID']         = input(f'{"ID: ": <34}' + '| ')
        signup_prompt_dict['Firstname']  = input(f'{"Firstname: ": <34}' + '| ')
        signup_prompt_dict['Lastname']   = input(f'{"Lastname: ": <34}' + '| ')
        signup_prompt_dict['Birthdate']  = input(f'{"Birthdate: ": <34}' + '| ')
        signup_prompt_dict['Password']   = input(f'{"Password: ": <34}' + '| ')
        signup_prompt_dict['PlanType']   = input(f'{"PlanType[Basic,Standard,Premium]: ": <34}' + '| ')
        signup_prompt_dict['StartDate']  = input(f'{"Start date[y-m-d]: ": <34}' + '| ')
        signup_prompt_dict['EndDate']    = input(f'{"End date[y-m-d]: ": <34}' + '| ')
        print('-'*34)
        signup_prompt_dict['CarVin']     = input(f'{"Car Vin: ": <34}' + '| ')
        signup_prompt_dict['Connector']  = input(f'{"Connector[AC,DC]: ": <34}' + '| ')
        signup_prompt_dict['Capacity']   = input(f'{"Capacity: ": <34}' + '| ')
        print('-'*34)


        return self.signup_prompts_check(signup_prompt_dict)

    def signup_prompts_check(self,signup_prompt_dict):
        '''all the inputs for the signup process'''

        signup_prompt_dict['PlanType']=signup_prompt_dict['PlanType'].capitalize()
        signup_prompt_dict['Connector']=signup_prompt_dict['Connector'].lower()

        signup_prompt_dict={i:self.injection_proof(v) for i,v in signup_prompt_dict.items()}

        if self.prompt_invalid_check(signup_prompt_dict['ID'],num=True) :
            return False, '\nID: Invalid Input\n'

        if self.prompt_invalid_check(signup_prompt_dict['Firstname'],alpha=True) :
            return False, '\nFirstname: Invalid Input\n'

        if self.prompt_invalid_check(signup_prompt_dict['Lastname'],alpha=True) :
            return False, '\nLastname: Invalid Input\n'

        if self.prompt_invalid_check(signup_prompt_dict['Birthdate'],date=True):
            return False,'\nBirthdate: Invalid Input\n'

        if self.prompt_invalid_check(signup_prompt_dict['Password']):
            return False, '\nPassword: Invalid Input\n'
    
        if self.prompt_invalid_check(signup_prompt_dict['PlanType'],choices=['Basic', 'Standard', 'Premium']):
            return False, '\nPlanType: Choose on of the options\n'

        if self.prompt_invalid_check(signup_prompt_dict['StartDate'],date=True):
            return False, '\nStartdate: Invalid Input\n'

        if self.prompt_invalid_check(signup_prompt_dict['EndDate'],date=True):
            return False, '\nEnddate: Invalid Input\n'

        if self.prompt_invalid_check(signup_prompt_dict['CarVin'],num=True):
            return False, 'Car Vin number: Invalid Input'

        signup_prompt_dict['CarVin'] = int(signup_prompt_dict['CarVin'][1:-1])

        if self.prompt_invalid_check(signup_prompt_dict['Connector'],['ac', 'dc']):
            return False, '\n Car Connector: Invalid Input \n'

        if self.prompt_invalid_check(signup_prompt_dict['Capacity']):
            return False, '\nCar Capacity : Invalid Input\n'

        try:
            signup_prompt_dict['Capacity'] = float(signup_prompt_dict['Capacity'][1:-1])
        except:
            return False, '\nCar Capacity : Invalid Input\n'

        user_salt=self.user.get_salt() 

        # Κανουμε κρυπτογραφηση των κωδικων με την χρηση της βιβλιοθηκης bcrypt . 
        # Χρησιμοποιουμε ενα τυχαιο συνολο χαρακτηρων salt για να μην μπορουν να γινουν ευκολα decrypt οι κωδικοι  
        # το οποιο το αποθηκευουμε στην βαση για να μπορουμε να το χρησιμοποιησουμε ξανα 

        signup_prompt_dict['Password'] = f"'{str(self.user.hash_password(signup_prompt_dict['Password'],user_salt))[2:-1]}'"

        user_salt=f"'{str(self.user.get_salt())[2:-1]}'" 

        customer_attributes = [signup_prompt_dict['ID'],signup_prompt_dict['Firstname'], signup_prompt_dict['Lastname'],
                                signup_prompt_dict['Birthdate'], signup_prompt_dict['PlanType'],
                                 signup_prompt_dict['StartDate'],signup_prompt_dict['EndDate'],
                               signup_prompt_dict['Password'] ,user_salt]


        car_attributes = [signup_prompt_dict['CarVin'], signup_prompt_dict['ID'], signup_prompt_dict['Connector'], signup_prompt_dict['Capacity']]
        
        return True,[customer_attributes, car_attributes]


    # --------------- adding new car ---------------


    def adding_new_car(self):
        ''' Εισαγωγη νεου αυτοκινητου στον χρηστη '''

        newcar_prompt_dict = {}

        status, result = self.adding_new_car_prompts(newcar_prompt_dict)
        
        if not status:
            return result

        car_attributes = result
        
        if not self.database.car_exists(car_attributes):

            self.database.insert_car(car_attributes)

            return f'\n\nAdded car vin: {car_attributes[0]} to the user: {self.user_id}\n\n'

        return f'\n\nThe car vin:{car_attributes[0]} is already in the account of the user{self.user_id}\n\n'

    def adding_new_car_prompts(self,newcar_prompt_dict):
        ''' Εισαγωγη δεδομενων απο τον χρηστη  '''

        print('-'*34)
        newcar_prompt_dict['CarVin']   = input(f'{"Car Vin: ": <34}' + '| ')
        newcar_prompt_dict['Connector']= input(f'{"Connector[AC,DC]: ": <34}' + '| ')
        newcar_prompt_dict['Capacity'] = input(f'{"Capacity: ": <34}' + '| ')
        print('-'*34)

        return  self.adding_new_car_prompts_check(newcar_prompt_dict)

    def adding_new_car_prompts_check(self,newcar_prompt_dict):
        ''' Ελεγχος των δεδομενων απο τον χρηστη  '''

        newcar_prompt_dict['Connector'] = newcar_prompt_dict['Connector'].lower()
        newcar_prompt_dict={i:self.injection_proof(v) for i,v in newcar_prompt_dict.items()}

        if self.prompt_invalid_check(newcar_prompt_dict['CarVin'],num=True):
            return False, '\nCar Vin: Invalid Input \n'
        newcar_prompt_dict['CarVin'] = int(newcar_prompt_dict['CarVin'][1:-1])

        if self.prompt_invalid_check(newcar_prompt_dict['Connector'],choices=['ac', 'dc']):
            return False, '\nCar Connector: Please Choose one of the options given \n'

        if self.prompt_invalid_check(newcar_prompt_dict['Capacity']):
            return False,'\n Car Capacity: Invalid Input \n'
        
        try:
            newcar_prompt_dict['Capacity'] = float(newcar_prompt_dict['Capacity'][1:-1])
        except:
            return False, '\n Car Capacity: Invalid Input For float \n'            

        car_attributes = [newcar_prompt_dict['CarVin'], self.user_id, newcar_prompt_dict['Connector'], newcar_prompt_dict['Capacity']]

        return True, car_attributes
        

    # --------------- change passwords ---------------


    def change_password(self):
        '''  '''


        change_password_prompt_dict={}
        
        valid, result = self.change_password_prompt(change_password_prompt_dict)
        
        if not valid:
            return result
            
        self.user.change_password(self.user_id,result)
        return '\nPassword changed succesfully'

    def change_password_prompt(self,change_password_prompt_dict):
        '''Cli input for old and new password '''

        print('-'*34)
        change_password_prompt_dict['OldPassword'] = input(f'{"Old Password: "}' + '| ')
        change_password_prompt_dict['NewPassword'] = input(f'{"New Password: "}' + '| ')
        print('-'*34)
        
        return self.change_password_prompt_check(change_password_prompt_dict)
                   
    def change_password_prompt_check(self,change_password_prompt_dict):

        change_password_prompt_dict={i:self.injection_proof(v) for i,v in change_password_prompt_dict.items()}

        if self.prompt_invalid_check(change_password_prompt_dict['OldPassword']):
            return False, '\nInvalid Input'

        if not self.user.check_customer_passwd(self.user_id, change_password_prompt_dict['OldPassword']):
            return False, '\nWrong password\n'
        
        if self.prompt_invalid_check(change_password_prompt_dict['NewPassword']):
            return False, '\nInvalid Input'

        if change_password_prompt_dict['OldPassword'] == change_password_prompt_dict['NewPassword']:
            return False, '\nNew password can\'t be the same as the old password\n'

        user_salt = self.user.get_salt()

        return True,  f"'{str(self.user.hash_password(change_password_prompt_dict['NewPassword'], user_salt))[2:-1]}'"


    # --------------- Forgot ID  ---------------


    def forgot_id(self):

        status , result = self.forgot_id_prompt()


        if status:

            return f"\n\nUser ID is : {self.user.get_user_id(result[0],result[1])}\n"

        else:
            return result


    def forgot_id_prompt(self):
        forgot_id_prompt_dict={}
        
        
        print('-'*34)
        forgot_id_prompt_dict['Firstname']  = input(f'{"Firstname: ": <34}' + '| ')
        forgot_id_prompt_dict['Lastname']   = input(f'{"Lastname: ": <34}' + '| ')
        forgot_id_prompt_dict['Birthdate']  = input(f'{"Birthdate: ": <34}' + '| ')
        forgot_id_prompt_dict['Password']   = input(f'{"Password: ": <34}' + '| ')
        forgot_id_prompt_dict['PlanType']   = input(f'{"PlanType[Basic,Standard,Premium]: ": <34}' + '| ')
        forgot_id_prompt_dict['StartDate']  = input(f'{"Start date[y-m-d]: ": <34}' + '| ')
        forgot_id_prompt_dict['EndDate']    = input(f'{"End date[y-m-d]: ": <34}' + '| ')
        print('-'*34)
        forgot_id_prompt_dict['CarVin']     = input(f'{"Car Vin: ": <34}' + '| ')
        forgot_id_prompt_dict['Connector']  = input(f'{"Connector[AC,DC]: ": <34}' + '| ')
        forgot_id_prompt_dict['Capacity']   = input(f'{"Capacity: ": <34}' + '| ')
        print('-'*34)

        return self.forgot_id_prompt_check(forgot_id_prompt_dict)

    def forgot_id_prompt_check(self,forgot_id_prompt_dict):

        forgot_id_prompt_dict['PlanType']=forgot_id_prompt_dict['PlanType'].capitalize()
        forgot_id_prompt_dict['Connector']=forgot_id_prompt_dict['Connector'].lower()

        forgot_id_prompt_dict={i:self.injection_proof(v) for i,v in forgot_id_prompt_dict.items()}

        if self.prompt_invalid_check(forgot_id_prompt_dict['Firstname'],alpha=True) :
            return False, '\nFirstname: Invalid Input\n'

        if self.prompt_invalid_check(forgot_id_prompt_dict['Lastname'],alpha=True) :
            return False, '\nLastname: Invalid Input\n'

        if self.prompt_invalid_check(forgot_id_prompt_dict['Birthdate'],date=True):
            return False,'\nBirthdate: Invalid Input\n'

        if self.prompt_invalid_check(forgot_id_prompt_dict['Password']):
            return False, '\nPassword: Invalid Input\n'

        if self.prompt_invalid_check(forgot_id_prompt_dict['PlanType'],choices=['Basic', 'Standard', 'Premium']):
            return False, '\nPlanType: Choose on of the options\n'

        if self.prompt_invalid_check(forgot_id_prompt_dict['StartDate'],date=True):
            return False, '\nStartdate: Invalid Input\n'

        if self.prompt_invalid_check(forgot_id_prompt_dict['EndDate'],date=True):
            return False, '\nEnddate: Invalid Input\n'

        if self.prompt_invalid_check(forgot_id_prompt_dict['CarVin'],num=True):
            return False, 'Car Vin number: Invalid Input'

        forgot_id_prompt_dict['CarVin'] = int(forgot_id_prompt_dict['CarVin'][1:-1])

        if self.prompt_invalid_check(forgot_id_prompt_dict['Connector'],['ac', 'dc']):
            return False, '\n Car Connector: Invalid Input \n'

        if self.prompt_invalid_check(forgot_id_prompt_dict['Capacity']):
            return False, '\nCar Capacity : Invalid Input\n'

        try:
            forgot_id_prompt_dict['Capacity'] = float(forgot_id_prompt_dict['Capacity'][1:-1])
        except:
            return False, '\nCar Capacity : Invalid Input\n'

        user_salt=self.user.get_salt()

        forgot_id_prompt_dict['Password'] = f"'{str(self.user.hash_password(forgot_id_prompt_dict['Password'],user_salt))[2:-1]}'"

        user_salt=f"'{str(self.user.get_salt())[2:-1]}'"

        customer_attributes = [None,forgot_id_prompt_dict['Firstname'], forgot_id_prompt_dict['Lastname'],
                                forgot_id_prompt_dict['Birthdate'], forgot_id_prompt_dict['PlanType'],
                                 forgot_id_prompt_dict['StartDate'],forgot_id_prompt_dict['EndDate'],
                               forgot_id_prompt_dict['Password'] ,user_salt]


        car_attributes = [forgot_id_prompt_dict['CarVin'], None, forgot_id_prompt_dict['Connector'], forgot_id_prompt_dict['Capacity']]

        return True,[customer_attributes, car_attributes]


    # --------------- Reserving ---------------


    def reserving(self):
        reserving_prompts_dict = {}
        status,result = self.reserving_prompts(reserving_prompts_dict)

        return result

    def reserving_prompts(self,reserving_prompts_dict):
         

        # check if the station has a charger that is compatible with the car
        # check that that charger is free 

        car_vins = [i[0] for i in self.user.get_car_vin(f"'{self.user_id}'")]
        if len(car_vins)>1:
            print('For Which Car to reserve?\n'+'\n'.join(car_vins))
            reserving_prompts_dict['vin'] = input(f"Vin: ")
        elif len(car_vins)==1:
            reserving_prompts_dict['vin'] = car_vins[0]


        reserving_prompts_dict['station_location']=input('Station Location: ')

        reserving_prompts_dict['start'] = input('Reserve from: ')
        reserving_prompts_dict['end'] = input('Reserve until: ')

        return self.reserving_prompts_check(reserving_prompts_dict)

    def reserving_prompts_check(self,reserving_prompts_dict):

        reserving_prompts_dict = {i: self.injection_proof(v) for i, v in reserving_prompts_dict.items()}

        if not self.prompt_invalid_check(reserving_prompts_dict['charger_location'],choices=[]):
            return False,'Charger Location Error'

        if not self.prompt_invalid_check(reserving_prompts_dict['start'],datetime=True):
            return False, 'Start DateTime is Not Correct'

        if not self.prompt_invalid_check(reserving_prompts_dict['end'],datetime=True):
            return False, 'End DateTime is Not Correct'

        
        valid = self.database.insert_reserve(self.user_id,reserving_prompts_dict['charger_location'],reserving_prompts_dict['start'],reserving_prompts_dict['end'])

        
        if valid :
            return True, f'Reservation from {reserving_prompts_dict["start"]} until {reserving_prompts_dict["end"]} at charger {reserving_prompts_dict["charger_location"]} was successful'

        return False, "Reservation was unsuccessful"


    # --------------- Statistics Functions ---------------

    def statistics(self):

        active_charging =f'{self.database.get_charging_sessions()} are currently active'


        free_chargers_true = "Free Chargers at this moment \n\n"+"\n".join([f"{i[1]} free , Connector Type: {i[0]}" for i in self.database.get_free_chargers(True)])


        free_chargers_false = "Free Chargers At this moment\n\n"+"\n".join([f"{i[1]} free, Type: {i[0]}" for i in self.database.get_free_chargers()])

        total_energy_served=f'Total Energy Served: {self.database.get_total_energy_served()}'

        
        statistics_list = [active_charging, free_chargers_true, free_chargers_false,total_energy_served,]

        length = 40
        result = ''

        for statistic in statistics_list:
            result += f'{"-"*length}\n{statistic}\n{"-"*length}\n\n'

        return result


    # --------------- Admin Fix Fault ---------------


    def admin_fix_fault(self):
        admin_fix_fault_prompt_dict={}
        active_failures_list = self.database.get_active_failures()
        print(f"Active Failures: {len(active_failures_list)}\n\n"+"\n".join([f'In station {i[0]}, error code: {i[1]:2},  since {i[2]}' for i in active_failures_list]),"\n")

        admin_fix_fault_prompt_dict['failures'] = active_failures_list
        status, result = self.admin_fix_fault_prompts(admin_fix_fault_prompt_dict)

        if not status:
            return result

        if self.database.update_fault(f"'{result[0]}'",result[1],f"'{result[2]}'",f"'{result[3]}'"):
            return f'Error {result[1]} on station {result[0]} fixed on {result[3]}'
        return 'Something went wrong'
    
    def admin_fix_fault_prompts(self,admin_fix_fault_prompt_dict):

        admin_fix_fault_prompt_dict['charger_location'] = input('Choose Location: ')

        admin_fix_fault_prompt_dict['fixed_on'] = input('Fixed on: ')

        return self.admin_fix_fault_prompts_check(admin_fix_fault_prompt_dict)
    


    def admin_fix_fault_prompts_check(self,admin_fix_fault_prompt_dict):


        admin_fix_fault_prompt_dict={i:(self.injection_proof(v) if i!='failures' else v)   for i,v in admin_fix_fault_prompt_dict.items()}

        
        fault_locations = [i[0] for i in admin_fix_fault_prompt_dict['failures']] 
        if self.prompt_invalid_check(admin_fix_fault_prompt_dict['charger_location'],choices=fault_locations):
            return False,'Error on location'

        if admin_fix_fault_prompt_dict['fixed_on']!="'now'" and self.prompt_invalid_check(admin_fix_fault_prompt_dict['fixed_on'],datetime=True):
            return False,'Error on fixed_on'

        if admin_fix_fault_prompt_dict['fixed_on']=="'now'":
            admin_fix_fault_prompt_dict['fixed_on'] = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        for i in admin_fix_fault_prompt_dict['failures']:
            if i[0] == admin_fix_fault_prompt_dict['charger_location'][1:-1]:
                ls = list(i)
                ls[3]=admin_fix_fault_prompt_dict['fixed_on']
                break

        if ls[2]>ls[1]:
            return False,'Fixed on must occur after the error has '

        return True,ls

       


    # --------------- Admin Statistics ---------------

    def admin_statistics(self):
  
        active_failures_list = self.database.get_active_failures()
        
        if len(active_failures_list)>1:
            active_failures = f"Active Failures {len(active_failures_list)}:\n\n"+ "\n".join([f'Oldest: In station {active_failures_list[0][0]}, error code: {active_failures_list[0][1]:2},  since {active_failures_list[0][2]}',f'Newest: In station {active_failures_list[-1][0]}, error code: {active_failures_list[-1][1]:2},  since {active_failures_list[-1][2]}',])
        else:
            active_failures = "Active Failures:\n\n"+ "\n".join([f'In station {i[0]}, error code: {i[1]:2},  since {i[2]}' for i in active_failures_list])


        energy_consumption_list = self.database.get_energy_consumption()

        if len(energy_consumption_list)>1:
            energy_consumption = f"Energy Consumption this month: {sum(energy_consumption_list)} \n\n"+"\n".join([f"Station {energy_consumption_list[0][0]} consumed the most energy ({energy_consumption_list[0][1]})",f"Station {energy_consumption_list[-1][0]} consumed the least energy ({energy_consumption_list[-1][1]})"])
        else:
            energy_consumption = "Energy Consumption this month\n\n"+"\n".join([f"Station {i[0]} consumed {i[1]} energy " for i in energy_consumption_list])


        hourly_usage_list = self.database.get_hourly_usage()
        if len(hourly_usage_list)>1:
            hourly_usage = "Hourly Usage\n\n"+"\n".join([f"Busiest hour was : {hourly_usage_list[0][2]}:00, at Charger: {hourly_usage_list[0][0]}  with {hourly_usage_list[0][1]} cars",f"Least Busy hour was : {hourly_usage_list[-1][2]}:00, at Charger: {hourly_usage_list[-1][0]} with {hourly_usage_list[-1][1]} cars",])
        else:
            hourly_usage = "Hourly Usage\n\n"+"\n".join([f"Charger: {i[0]} charged {i[1]} cars, at {i[2]}:00" for i in hourly_usage_list])


        revenue_list = self.database.get_station_revenue()

        if len(revenue_list)>1 :
            revenue_station = "Revenue Per Station\n\n" + "\n".join([f"Most Profitable Station: {revenue_list[0][0]} with {revenue_list[0][1]}",f"Least Profitable Station: {revenue_list[-1][0]} with {revenue_list[-1][1]}",])
        else:
            revenue_station = "Revenue Per Station\n\n" + "\n".join([f"Station: {i[0]} , revenue: {i[1]}" for i in revenue_list])


        statistics_list = [active_failures,energy_consumption,hourly_usage,revenue_station]

        length = 40

        result = ''

        for statistic in statistics_list:
            result += f'{"-" * length}\n{statistic}\n{"-" * length}\n\n'

        return result


    # --------------- General Functions ---------------

    def clear(self):
        '''Clears the terminal Screen'''

        if 'linux' in platform.system().lower() or 'darwin' in platform.system().lower():
            os.system('clear')
        if 'windows' in platform.system().lower():
            os.system('clc')

    def injection_proof(self, query):
        '''Checking for queries that can be used for injecting malicious code'''

        valid = '--' not in query and ';' not in query and "\'" not in query and '\"' not in query and len(query)>0
        if valid:
            return f"'{query}'"

        return False

    def options_message(self, option_list):
        return ''.join([f'\n Option {i} : {v}' for i, v in enumerate(option_list)]) + '\n Option 99: Exit\n\n'

    def exit_options(self):
        '''simple menu to prevent the results of the option chosen to be cleared'''

        if not self.is_inside_options:
            return

        user_option = input('>>>')

        if user_option in ['exit', '99', '-1']:
            self.exit()

        self.is_inside_options = False
        self.clear()

    def exit(self):
        '''closes the database and exits'''

        print('\n Ciao \n')
        self.database.conn.close()
        self.user.conn.close()
        sys.exit()

    
    # --------------- Main Functions ---------------

    def main_option_menu(self, option_functions):
        '''sub menu choosing options'''

        options_list=list(option_functions.keys())
        print(self.options_message(options_list))

        user_option = input('>>')

        if user_option == 'help':
            print('Extra stuff coming away')

        elif user_option in ['exit', '99', '-1']:
            self.exit()

        # search for walrus operator python

        elif user_option.isnumeric() and (num_option := int(user_option)) < len(options_list):

            self.is_inside_options = True

            print(f"\n{options_list[num_option]}\n")

            try:
                print(option_functions[options_list[num_option]]())
            except :
                self.clear()
                self.is_inside_options=False

        else:
            # this is for clearing the screen if you are done with an option
            self.is_inside_options = False

            self.clear()

        self.exit_options()

    def main(self):

        self.clear()

        while True:

            print('\nWelcome to Power Station Management\n')

            if self.user_id is not None and self.user_id!='0':
                # logged in
                print(f'\nUser ID: {self.user_id}\n')

                option_functions = {'Account Info':self.info, 'General Info':self.general_info, 'Add a new car':self.adding_new_car,'Change Password':self.change_password,'Logout':self.logout,"Reserve":self.reserving}

            elif self.user_id is not None and self.user_id=='0':
                
                option_functions={'Statistics':self.admin_statistics,'Logout':self.logout,'Fix Fault':self.admin_fix_fault}
                print('Admin Panel')

            else:
                # not logged in
                option_functions = {'Login':self.login,'Signup':self.signup,'Forgot ID':self.forgot_id,'Statistics':self.statistics}

            
            self.main_option_menu(option_functions)
                

if __name__ == '__main__':
    database_file = 'database_data'
    application = App(database_file)
            

    try:
        application.main()
    except KeyboardInterrupt:
        application.exit()

