import sqlite3 
### code to connect to connect sqlie 3
connection=sqlite3.connect("student.db")


## create a cursor object to insert record,create table
cursor=connection.cursor()

## create the table
table_info = """
CREATE TABLE IF NOT EXISTS STUDENT(
    roll_no INTEGER,
    name TEXT
)
"""
cursor.execute(table_info)


## Insert some more records 
cursor.execute('''Insert into STUDENT values('Prateek','Data Science','A',93)''')
cursor.execute('''Insert into STUDENT values('Gudu','AI-ML','A',63)''')
cursor.execute('''Insert into STUDENT values('Chetan','Web Development','A',88)''')
cursor.execute('''Insert into STUDENT values('Pulkit','APP Development','A',61)''')
cursor.execute('''Insert into STUDENT values('Abhishek','Game Development','A',88)''')


## display all the records
print("The inserted records are ")
data=cursor.execute('''Select * from STUDENT''')
for row in data:
    print(row)


## commit your changes in the database
connection.commit()
connection.close()