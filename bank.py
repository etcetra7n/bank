from sqlite3 import connect
from datetime import datetime
from sys import argv
from decimal import getcontext, Decimal
from tabulate import tabulate
from getters import *
from plotting import *

global acc_db
global tnxs_db

testing = False
if testing:
    acc_db = r"accounts.db"
    tnxs_db = r"transactions.db"
else:
    acc_db = r"C:/ProgramData/bank/accounts.db"
    tnxs_db = r"C:/ProgramData/bank/transactions.db"
    
getcontext().prec = 28

def create_acc(cust_id, name):
    db = connect(acc_db)
    cr = db.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cr.execute(f"INSERT INTO accounts VALUES ('{cust_id}', '{name}', '0', '{timestamp}', '0', '0')")
    db.commit()
    db.close()
    print(f"Account created successfully.")

def credit(cust_id, amt, remark):
    print(f"Account holder: {get_name(cust_id, acc_db)}\n")
    db = connect(acc_db)
    cr = db.cursor()
    new_bal = str((Decimal(get_bal(cust_id, acc_db))+Decimal(amt)).quantize(Decimal('.01')))

    timestamp = datetime.now()
    income = Decimal(get_income(cust_id, acc_db))+Decimal(amt)
    income = str(income.quantize(Decimal('.01')))

    cr.execute(f"UPDATE accounts SET bal= '{new_bal}' WHERE custID='{cust_id}'")
    cr.execute(f"UPDATE accounts SET income= '{income}' WHERE custID='{cust_id}'")
    db.commit()
    db.close()

    db = connect(tnxs_db)
    cr = db.cursor()
    timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    cr.execute(f"INSERT INTO transactions VALUES ('{cust_id}', 'credit', '+{amt}', '{remark}', '{timestamp}', '{get_bal(cust_id, acc_db)}')")
    db.commit()
    db.close()
    print(f"Credited ${amt} successfully.")
    print(f"Current balance: {get_bal(cust_id, acc_db)}")

def debit(cust_id, amt, remark):
    print(f"Account holder: {get_name(cust_id, acc_db)}\n")
    db = connect(acc_db)
    cr = db.cursor()
    new_bal = str((Decimal(get_bal(cust_id, acc_db))-Decimal(amt)).quantize(Decimal('.01')))

    timestamp = datetime.now()
    expenditure = Decimal(get_expenditure(cust_id, acc_db))+Decimal(amt)
    expenditure = str(expenditure.quantize(Decimal('.01')))

    cr.execute(f"UPDATE accounts SET bal= '{new_bal}' WHERE custID='{cust_id}'")
    cr.execute(f"UPDATE accounts SET expenditure='{expenditure}' WHERE custID='{cust_id}'")
    db.commit()
    db.close()

    db = connect(tnxs_db)
    cr = db.cursor()
    timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    cr.execute(f"INSERT INTO transactions VALUES ('{cust_id}', 'debit', '-{amt}', '{remark}', '{timestamp}', '{get_bal(cust_id, acc_db)}')")
    db.commit()
    db.close()
    print(f"Debited ${amt} successfully.")
    print(f"Current balance: {get_bal(cust_id, acc_db)}")

def accs():
    db = connect(acc_db)
    accs = db.execute(f"SELECT custID, name, bal FROM accounts")
    cust_id=[]
    name=[]
    bal=[]
    for acc in accs:
        cust_id.append(acc[0])
        name.append(acc[1])
        bal.append(acc[2])
    table = zip(cust_id, name, bal)
    print(tabulate(table, headers=["custID", "name", "bal"], tablefmt='rst'))
    db.close()

def del_acc(cust_id):
    print(f"WARNING: deleting account @{cust_id}")
    print(f"Account holder: {get_name(cust_id, acc_db)}")
    print(f"Available balance: {get_bal(cust_id, acc_db)}\n")
    print("Are you sure you want to proceed? (YES/n): ", end="")
    confirmation = input()
    if confirmation=="YES":
        db = connect(acc_db)
        db.execute(f"DELETE FROM accounts WHERE custID='{cust_id}'")
        db.commit()
        db.close()
        print(f"Deleted successfully.")
    else:
        print("Aborted.")


def acc(cust_id):
    keys = [
    "custID", 
    "name", 
    "bal", 
    "date_of_opening",
    "income", 
    "expenditure", 
    "inrate", 
    "outrate"
    ]
    values = [
    "@"+cust_id, 
    get_name(cust_id, acc_db), 
    get_bal(cust_id, acc_db), 
    get_date_of_opening(cust_id, acc_db),
    get_income(cust_id, acc_db), 
    get_expenditure(cust_id, acc_db), 
    get_inrate(cust_id, acc_db), 
    get_outrate(cust_id, acc_db)
    ]
    table = zip(keys, values)
    print(tabulate(table, floatfmt=".2f"))

def bal(cust_id):
    keys = ["Account holder", "Available balance"]
    values = [get_name(cust_id, acc_db), get_bal(cust_id, acc_db)]
    table = zip(keys, values)
    print(tabulate(table, floatfmt=".2f"))

def tnxs(cust_id):
    print(f"Account holder: {get_name(cust_id, acc_db)}")
    print(f"Available balance: {get_bal(cust_id, acc_db)}\n")

    db = connect(tnxs_db)
    type=[]
    amt=[]
    remark=[]
    timestamp=[]
    balance=[]
    tnxs = db.execute(f"SELECT type, amt, remark, timestamp, balance FROM transactions WHERE custID='{cust_id}' ORDER BY timestamp ASC")
    for t in tnxs:
        type.append(t[0])
        amt.append(t[1])
        remark.append(t[2])
        timestamp.append(t[3])
        balance.append(t[4])
    table = zip(type, amt, remark, balance, timestamp)
    print(tabulate(table, headers=["type", "amt", "remark", "balance", "timestamp"], tablefmt='rst', floatfmt=".2f"))
    db.close()

if __name__ == "__main__":
    header_msg="""\
Taurus Bank Inc.
v4.3.8 \
"""
    commands="""
Available commands:
- bank create_acc [custId] [name]
- bank credit [custId] [$amt] ["remark"]
- bank debit [custId] [$amt] ["remark"]
- bank acc [custId]
- bank bal [custId]
- bank plot_bal [custID]
- bank tnxs [custId]
- bank accs (list of accounts)
- bank del_acc [custId] \
        """
    try:
        if(len(argv)<=1):
            print(header_msg)
            print(commands)
        elif argv[1] == 'create_acc':
            create_acc(argv[2], argv[3])
        elif argv[1] == 'credit':
            credit(argv[2], argv[3], argv[4])
        elif argv[1] == 'debit':
            debit(argv[2], argv[3], argv[4])
        elif argv[1] == 'acc':
            acc(argv[2])
        elif argv[1] == 'bal':
            bal(argv[2])
        elif argv[1] == 'plot_bal':
            plot_bal(argv[2], acc_db, tnxs_db)
        elif argv[1] == 'tnxs':
            tnxs(argv[2])
        elif argv[1] == 'accs':
            accs()
        elif argv[1] == 'del_acc':
            del_acc(argv[2])
        elif argv[1] == 'help':
            print(header_msg)
            print(commands)
        else:
            print("Command not recognized.")
    except IndexError:
        print("Invalid command format.")
        