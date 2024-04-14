from sqlite3 import connect
from datetime import datetime, timedelta
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

def credit(cust_id, amt, remark, offset=0):
    print(f"Account holder: {get_name(cust_id, acc_db)}\n")
    db = connect(acc_db)
    cr = db.cursor()
    new_bal = str((Decimal(get_bal(cust_id, acc_db))+Decimal(amt)).quantize(Decimal('.01')))

    timestamp = datetime.now()
    offset_hrs = timedelta(hours=offset)
    timestamp = timestamp - offset_hrs
    
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

def debit(cust_id, amt, remark, offset=0):
    print(f"Account holder: {get_name(cust_id, acc_db)}\n")
    db = connect(acc_db)
    cr = db.cursor()
    new_bal = str((Decimal(get_bal(cust_id, acc_db))-Decimal(amt)).quantize(Decimal('.01')))

    timestamp = datetime.now()
    offset_hrs = timedelta(hours=offset)
    timestamp = timestamp - offset_hrs
    
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

def undo_last_tnx(cust_id):
    db = connect(tnxs_db)
    cr = db.cursor()
    res = db.execute(f"SELECT type, amt, remark, timestamp, balance FROM transactions WHERE custID='{cust_id}' ORDER BY timestamp DESC LIMIT 1") 
    type=''
    amt=''
    remark=''
    timestamp=''
    balance=''
    for t in res:
        type = t[0]
        amt = t[1]
        remark = t[2]
        timestamp = t[3]
        balance = t[4]
    cr.execute(f"DELETE FROM transactions WHERE custID='{cust_id}' AND timestamp='{timestamp}' AND amt='{amt}' AND remark='{remark}' AND type='{type}' AND balance='{balance}'")    #delete last tnx record
    db.commit()
    db.close()
    
    db = connect(acc_db)
    cr = db.cursor()
    if type=='credit':
        new_bal = str((Decimal(get_bal(cust_id, acc_db))-Decimal(amt)).quantize(Decimal('.01')))
        new_income = str((Decimal(get_income(cust_id, acc_db))-Decimal(amt)).quantize(Decimal('.01')))
        cr.execute(f"UPDATE accounts SET bal= '{new_bal}' WHERE custID='{cust_id}'")
        cr.execute(f"UPDATE accounts SET income= '{new_income}' WHERE custID='{cust_id}'")
    else:
        new_bal = str((Decimal(get_bal(cust_id, acc_db))-Decimal(amt)).quantize(Decimal('.01')))
        new_expenditure = str((Decimal(get_expenditure(cust_id, acc_db))+Decimal(amt)).quantize(Decimal('.01')))
        cr.execute(f"UPDATE accounts SET bal= '{new_bal}' WHERE custID='{cust_id}'")
        cr.execute(f"UPDATE accounts SET expenditure= '{new_expenditure}' WHERE custID='{cust_id}'")
    db.commit()
    db.close()
    
    print("The following transaction is deleted:")
    table = zip([type], [amt], [remark], [balance], [timestamp])
    print(tabulate(table, headers=["type", "amt", "remark", "balance", "timestamp"], floatfmt=".2f"))

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
        
def calc_int(cust_id, int_rate, date1, date2):
    intrest = Decimal('0').quantize(Decimal('.000001'))
    init_date = datetime.strptime(date1, "%d-%m-%Y")
    final_date = datetime.strptime(date2, "%d-%m-%Y")
    int_perc = (Decimal(int_rate)/Decimal('100')).quantize(Decimal('.00001'))
    for day in range(0, (final_date-init_date).days):
        this_day = init_date + timedelta(days=day)
        eod_bal = Decimal(get_eod_bal(cust_id, this_day, tnxs_db))
        intrest = Decimal(intrest+(Decimal(eod_bal*int_perc)/Decimal('365'))).quantize(Decimal('.000001'))
    intrest = str(intrest.quantize(Decimal('.01')))
    keys = [
    "custID", 
    "name", 
    "intrest period start", 
    "intrest period end",
    "calculatd intrest", 
    ]
    values = [
    "@"+cust_id, 
    get_name(cust_id, acc_db), 
    date1,
    date2,
    intrest
    ]
    table = zip(keys, values)
    print(tabulate(table, floatfmt=".2f"))

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
v4.6.2 \
"""
    commands="""
Available commands:
- bank create_acc [custId] [name]
- bank credit [custId] [$amt] ["remark"] ($offset)
- bank debit [custId] [$amt] ["remark"] ($offset)
- bank undo [custId]
- bank acc [custId]
- bank bal [custId]
- bank plot_bal [custID]
- bank tnxs [custId]
- bank calc_int [custID] [intrest_rate] [start_date] [end_date]
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
            if len(argv)>5:
                credit(argv[2], argv[3], argv[4], offset=int(argv[5]))
            else:
                credit(argv[2], argv[3], argv[4])
        elif argv[1] == 'debit':
            if len(argv)>5:
                debit(argv[2], argv[3], argv[4], offset=int(argv[5]))
            else:
                debit(argv[2], argv[3], argv[4])
        elif argv[1] == 'undo':
            undo_last_tnx(argv[2])
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
        elif argv[1] == 'calc_int':
            calc_int(argv[2], argv[3], argv[4], argv[5])
        elif argv[1] == 'del_acc':
            del_acc(argv[2])
        elif argv[1] == 'help':
            print(header_msg)
            print(commands)
        else:
            print("Command not recognized.")
    except IndexError:
        print("Invalid command format.")
        