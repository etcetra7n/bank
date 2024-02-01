from sqlite3 import connect
from datetime import datetime
from decimal import getcontext, Decimal

getcontext().prec = 28

def get_name(cust_id, acc_db):
    db = connect(acc_db)
    res = db.execute(f"SELECT name FROM accounts WHERE custID='{cust_id}'")
    res = next(x for x in res)
    db.close()
    return res[0]

def get_bal(cust_id, acc_db):
    db = connect(acc_db)
    res = db.execute(f"SELECT bal FROM accounts WHERE custID='{cust_id}'")
    res = next(x for x in res)
    db.close()
    return res[0]

def get_inrate(cust_id, acc_db):
    db = connect(acc_db)
    res = db.execute(f"SELECT inrate FROM accounts WHERE custID='{cust_id}'")
    res = next(x for x in res)
    db.close()
    return res[0]

def get_outrate(cust_id, acc_db):
    db = connect(acc_db)
    res = db.execute(f"SELECT outrate FROM accounts WHERE custID='{cust_id}'")
    res = next(x for x in res)
    db.close()
    return res[0]

def get_income(cust_id, acc_db):
    db = connect(acc_db)
    res = db.execute(f"SELECT income FROM accounts WHERE custID='{cust_id}'")
    res = next(x for x in res)
    db.close()
    return res[0]

def get_expenditure(cust_id, acc_db):
    db = connect(acc_db)
    res = db.execute(f"SELECT expenditure FROM accounts WHERE custID='{cust_id}'")
    res = next(x for x in res)
    db.close()
    return res[0]

def get_date_of_opening(cust_id, acc_db):
    db = connect(acc_db)
    res = db.execute(f"SELECT date_of_opening FROM accounts WHERE custID='{cust_id}'")
    res = next(x for x in res)
    db.close()
    res = res[0]
    date_of_opening = datetime.strptime(res, "%Y-%m-%d %H:%M:%S")
    return date_of_opening
    
def get_outrate(cust_id, acc_db):
    timestamp = datetime.now()
    time_diff = timestamp - get_date_of_opening(cust_id, acc_db)
    number_of_days = time_diff.days
    expenditure = Decimal(get_expenditure(cust_id, acc_db))
    outrate = str((expenditure/((Decimal(number_of_days))+1)).quantize(Decimal('.01')))
    return outrate

def get_inrate(cust_id, acc_db):
    timestamp = datetime.now()
    time_diff = timestamp - get_date_of_opening(cust_id, acc_db)
    number_of_days = time_diff.days
    income = Decimal(get_income(cust_id, acc_db))
    inrate = str((income/((Decimal(number_of_days))+1)).quantize(Decimal('.01')))
    return inrate

def get_eod_bal(cust_id, date, acc_db):
    pass
    #date as string in iso format
    
