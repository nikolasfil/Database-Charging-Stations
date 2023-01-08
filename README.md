
## Application for Car Charging Stations Management


----

### main.py

Is the main program to run 

Takes one optional argument 

```Bash
python main.py # simply runs the program in cli mode 
```


```Bash
python main.py -f file # specifies the database file to associate with the application . Default value : data.db 
```

If the database does not exist in the folder the program is run, then it is created with either the name specified by the -f flag , or the default value data.db 

----

### cli.py

It is the main application, that runs in a command line mode 

Contains login, signup and other functions 

----

### creating_database.py

Creates the table that we use for our database 

----

### filling_database.py

After the database is created, inserting data inserts randomly generated and custom data in the database, useful for statistics and other functions

----

### user.py

handles the authentication of the user in the login, and the signup process 

----

### database_class.py

Handles the requests from the app to the database 

----

### requirements.txt

the libraries used in the programs 

```bash
python3 -m pip3 install -r requirements.txt 
```

----

