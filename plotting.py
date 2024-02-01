def plot_bal(cust_id, acc_db, tnxs_db):
    from matplotlib.pyplot import rcParams, subplots, setp, show
    from matplotlib.dates import DateFormatter, MonthLocator
    from sqlite3 import connect
    from datetime import datetime
    from math import ceil
    x=[]
    y=[]
    db = connect(tnxs_db)
    tnxs = db.execute(f"SELECT timestamp, balance FROM transactions WHERE custID='{cust_id}' ORDER BY timestamp ASC")
    for tnx in tnxs:
        timestamp = tnx[0]
        time_of_tnx = None
        if len(timestamp) < 12:
            time_of_tnx = datetime.strptime(timestamp, "%Y-%m-%d")
        else:
            time_of_tnx = datetime.strptime(tnx[0], "%Y-%m-%d %H:%M:%S")
        x.append(time_of_tnx)
        y.append(float(tnx[1]))
    db.close()
    
    rcParams['text.color']= "#bdc1c6" #"#c6cdd5"
    
    fig, ax = subplots(layout="constrained", facecolor = "#202124")
    ax.plot(x, y, color="#81c995", linestyle=":") #marker="."
    ax.set_xlabel("time")
    ax.set_ylabel("acc bal ($)")
    ax.set_title("acc bal over time")
    
    ax.grid(True, color="#3f4245", linestyle=':', linewidth=1) #"#3f4245"
    ax.set_facecolor("#303134")
    ax.set_yticks(range(0, int(max(y))+1, int(ceil((max(y)/18)/500.0))*500))
    ax.xaxis.label.set_color("#bdc1c6")
    ax.yaxis.label.set_color("#bdc1c6")
    ax.spines['left'].set_color("#3f4245")
    ax.spines['top'].set_color("#3f4245")
    ax.spines['right'].set_color("#3f4245")
    ax.spines['bottom'].set_color("#3f4245")
    
    ax.tick_params(axis='x', colors="#929296") #"#929296"
    ax.tick_params(axis='y', colors="#929296")
    
    ax.fmt_xdata = DateFormatter("%Y-%m-%d")
    ax.xaxis.set_major_locator(MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(DateFormatter("%b %Y"))
    setp(ax.get_xticklabels(), rotation=45)
    show()
