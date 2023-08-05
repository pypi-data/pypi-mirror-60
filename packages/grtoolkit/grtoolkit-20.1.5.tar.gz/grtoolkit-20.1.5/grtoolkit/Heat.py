import pyodbc, os, sys

def Farenheit(Celcius):
    return 9.0/5.0*Celcius+32.0

def Celcius(Farenheit):
    return (Farenheit-32.0)/9.0*5.0



# def read_db():
#     "Select all from A04_Saturated_Water_Temperature"

# print(readSQL(os.path.dirname(sys.argv[0]) + "\\PropertyTables.accdb", "Select * from A04_Saturated_Water_Temperature"))