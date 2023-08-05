# python-duplicate 
[![Build Status](https://travis-ci.com/Clement-O/python-duplicate.svg?branch=master)](https://travis-ci.com/Clement-O/python-duplicate) 
[![Coverage Status](https://coveralls.io/repos/github/Clement-O/python-duplicate/badge.svg?branch=master)](https://coveralls.io/github/Clement-O/python-duplicate?branch=master)
[![Documentation Status](https://readthedocs.org/projects/python-duplicate/badge/?version=latest)](https://python-duplicate.readthedocs.io/en/latest/?badge=latest)

The python-duplicate library intend to find and deal with duplicate.
It can be installed with ```pip install python-duplicate ```.
Depending on what you need, it can:
- Find and return the unique or duplicate items* of a list
- Create a new list of unique items* from a list
- Find and return the indexes of said items* (act as a feedback)
- Find the rows (or just PK) of unique or duplicate column for MySQL 8 and PosgreSQL 10

*items can be a list, tuple, dict, number or string

## Upcoming improvements
In the future I intend to add support for:
- JSON
- Other type of item for list (Object class for example)
- Handle suppression of duplicate for MySQL and PostgreSQL
- Handle research of unique / duplicate on more than one table / column / pk
- Support more version of MySQL and Postgres
- Support more database type

## Testing
If you want to test it, please make sure to:
 - Install the requirements > dev.req
 - Install MySQL 8 & PostgreSQL 10 and create them an user with right to create and delete database
 - Create an .env file filed as this:
     ```
     POSTGRES_HOSTNAME = localhost
     POSTGRES_DATABASE = pyd
     POSTGRES_USER = test
     POSTGRES_PASSWORD = test
     POSTGRES_PORT = 5432
     
     MYSQL_HOSTNAME = localhost
     MYSQL_DATABASE = pyd
     MYSQL_USER = test
     MYSQL_PASSWORD = test
     MYSQL_PORT = 3306
     ```
Once it's done you can start the test with ```python -m unittest discover```.
__It will drop any existing database defined in the .env file__, recreate and fill it with fixtures data (_found in test/database/fixtures_). 
At the end of the test the databases created will be deleted.
