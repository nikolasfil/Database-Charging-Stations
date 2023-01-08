#!/bin/python
import os
import argparse

from cli import App
from creating_database import Creation
from filling_database import Filling


def parsing_arguments():
    #Parser Arguments
    parser = argparse.ArgumentParser(description='Run the project as cli or with gui')
    parser.add_argument('--file','-f',default='data.db')
    
    
    return  parser.parse_args()       

def create_database(file):
    # δημιουργια των πινακων της βασης δεδομενων 
    create = Creation(file)
    create.main()

    # Εισαγωγη δεδομενων για χρηση 
    fill = Filling(file)
    fill.main()
    # Τα δεδομενα αυτα συνδιαζονται με δεδομενα απο τα csv στον φακελο sqldata . 

def main():

    args = parsing_arguments()
    database_file = args.file
    
    if database_file not in os.listdir():
        create_database(database_file)

    application = App(database_file)

    try:
        application.main()
    except KeyboardInterrupt:
        application.exit()



if __name__ == '__main__':
    main()