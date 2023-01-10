#!/bin/python
import platform
import sys
import PySimpleGUI as sgui
import bcrypt
from database_class import DataBase
from cli import App

# IT NEEDS AN ADJUSTMENT FOR THE DICTIONARIES 


class AppGui(App):
    
    def gui_init(self):

        # this is for setting up the pysimplegui layout and stuff
        self.welcome_text='Power Station Management'
        self.section_names=['logged_in','logged_out','login','signup']


        logged_in_layout=self.creating_logged_in_layout()
        logged_out_layout=self.creating_logged_out_layout()
        signup_layout=self.creating_signup_layout()


        login_layout=self.creating_login_layout()

        # we need the self.collapse because it creates collumns that can be hidden

        layout = [  [self.collapse(login_layout,'login',False)],
                    [self.collapse(logged_in_layout,'logged_in',False)],
                    [self.collapse(signup_layout,'signup',False)],
                    [self.collapse(logged_out_layout,'logged_out',True)],
                ]
        
        # self.window=sgui.Window('Application',layout,size=(800,500))
        self.window=sgui.Window('Application',layout)

    def creating_login_layout(self):

        self.login_layout_prompts=['User ID: ','Password: ']
        return [[sgui.Text(self.login_layout_prompts[0], size=(12, 1), font=("Courier", 18)),sgui.InputText(font=("Courier", 18))],[sgui.VPush()],
                [sgui.Text(self.login_layout_prompts[1], size=(12, 1), font=("Courier", 18)),sgui.InputText(font=("Courier", 18))],[sgui.VPush()],
                [sgui.Submit(key="-LOGIN-",  font=("Courier", 18))],[sgui.VPush()],]


    def creating_logged_in_layout(self):

        self.logged_in_functions = {'Account Info':self.info, 'General Info':self.general_info, 'Logout':self.logout,'Exit':self.exit}

        logged_in_layout=[ [sgui.Text(self.welcome_text, font=("Courier", 18))],
                                [sgui.Text(text=self.logged_in_message(), font=("Courier", 18),key='logged_in_message')],
                                [sgui.VPush()],]

        for i in list(self.logged_in_functions.keys()):
            logged_in_layout.append([sgui.Button(i, size=(12, 1), font=("Courier", 18))])
            logged_in_layout.append([sgui.VPush()])

        return logged_in_layout


    def creating_logged_out_layout(self):
        
        self.logged_out_functions = {'Login':self.login, 'Signup':self.signup,'Exit':self.exit}

        logged_out_layout=[[sgui.Text(self.welcome_text, font=("Courier", 18))],[sgui.VPush()],]

        for i in list(self.logged_out_functions.keys()):
            logged_out_layout.append([sgui.Button(i, size=(12, 1), font=("Courier", 18))])
            logged_out_layout.append([sgui.VPush()])
        
        return logged_out_layout


    def creating_signup_layout(self):

        self.signup_layout_prompts=["Firstname: ","Lastname: ","Password: ","PlanType[Basic,Standard,Premium]","Start date[d-m-y]","End date[d-m-y]","Car Vin: ","Connector[AC,DC]: ","Capacity: "]

        signup_layout=[]

        for i in self.signup_layout_prompts:
        
            signup_layout.append([sgui.Text(i, size=(34, 1), font=("Courier", 18)),sgui.InputText(font=("Courier", 18))])
            signup_layout.append([sgui.VPush()],)
        
        signup_layout.append([sgui.Submit(key="-SIGNUP-",  font=("Courier", 18))])
        signup_layout.append([sgui.VPush()],)
        
        return signup_layout


    def window_clear(self):
        '''hids all the columns in the window '''

        for i in self.section_names:
            self.window[i].update(visible=False)
        
        self.clear_input()
        
        self.window.refresh()


    def clear_input(self):
        '''clears all the input Text boxes'''

        # print(self.window.key_dict.items())
        for key, element in self.window.key_dict.items():
        
            if isinstance(element, sgui.Input):
        
                element.update(value='')


    def popup(self,message):

        # https://www.pysimplegui.org/en/latest/#popup-output
        sgui.Popup(message,any_key_closes=True,no_titlebar=True,font=("Courier", 18))


    def login(self):
        
        '''login with id'''
        
        self.window_clear()
        self.window['login'].update(visible=True)
        
        # this is from pysimplegui
        event,values=self.window.read()
        # prompts = [values[i] for i in range(2)]

        prompt_dict = {self.login_keys[i]:values[i] for i in range(2)}

        if event=='-LOGIN-':

            status, result = self.login_prompt_check(prompt_dict)
            
            if status:
                self.user_id = int(values[0])
                self.window.Element('logged_in_message').Update(self.logged_in_message())
            else:    
                self.popup(result)
                        
    def logged_in_message(self):
        return f'\nUser ID: {self.user_id}\n' 


    def logout(self):
        '''Logging out '''

        self.user_id = None
        self.window_clear()
        self.popup('Logged Out successful')
        self.window['logged_out'].update(visible=True)


    def info(self):
        print(self.database.get_user_info(self.user_id))
        

    def general_info(self):
        pass


    def signup(self):
        '''sign up variable prompts'''

        self.window_clear()
        self.window['signup'].update(visible=True)

        event,values=self.window.read()

        # prompts = [values[i] for i in range(2,len(values))]
        prompt_dict = {self.signup_keys[i-2]:values[i] for i in range(2,len(values))}

        if event=='-SIGNUP-':
            status, result = self.signup_prompts_check(prompt_dict)
            
            if not status:
                self.popup(result)

            else:

                customer_attributes,car_attributes= result[0],result[1]

                # work on the error messages a bit
                if not customer_attributes and not car_attributes: 
                    self.popup('\nInvalid Input\n')
                    

                user_id = customer_attributes[0]
                
                customer_exists_var=self.database.customer_exists(customer_attributes)
                car_exists_var=self.database.car_exists(car_attributes)
            
                if  customer_exists_var and car_exists_var:
                    self.popup('\n\nA User with that car already exists\n')
                
                elif customer_exists_var and not car_exists_var:
                    self.database.insert_car(car_attributes)
                    self.popup(f'\n\nAdding a new car to the user: {user_id} \n\n')    
                
                else:
                    self.database.insert_customer(customer_attributes)
                    self.database.insert_car(car_attributes)
                    self.popup(f'\n\nSign Up successful with user id: {user_id}\n')
            
    
            

    def change_password(self):
        '''to be utilized'''
        pass


    def injection_proof(self, query):
        '''Checking for queries that can be used for injecting malicious code'''

        valid = '--' not in query and ';' not in query and "\'" not in query and '\"' not in query
        if valid:
            return f"'{query}'"
        return False


    def str_hash_format(self,string):
        return f"'{str(string)[2:-1]}'"


    def exit(self):
        print('\n Ciao \n')
        self.database.conn.close()
        self.user.conn.close()
        self.window.close()
        sys.exit()



    def todo(self):
        # find out where there are available stations and chargers , based on user logged in
        # calculate best distance based on the capacity and location that we currently have
        # no idea how to have the location of the car
        # also maybe think about passwords ? or maybe not
        # help menu inside the options
        pass


    def collapse(self,layout, key, visible):
        return sgui.pin(sgui.Column(layout, key=key, visible=visible))


    def main(self):

        while True:            
            
            self.event,self.value=self.window.read()
            
            # Exit0 comes from the button exit, while None comes from closing the program from the x trail button

            if self.event in ['Exit',None,'Exit0']:
                self.exit()

            elif self.event in list(self.logged_in_functions.keys()):
                self.logged_in_functions[self.event]()

            elif self.event in list(self.logged_out_functions.keys()):
                self.logged_out_functions[self.event]()
                

            self.window_clear()    
            if self.user_id is not None:
                self.window['logged_in'].update(visible=True)
            else:
                self.window['logged_out'].update(visible=True)
            
            # just for checking we dont really need it 
            print(self.event)

    


if __name__ == '__main__':
    database_file = 'database_data'
    application = AppGui(database_file)
    try:
        application.main()
    except KeyboardInterrupt:
        application.exit()

