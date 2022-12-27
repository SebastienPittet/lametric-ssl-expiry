import os
import sqlite3
from datetime import datetime

# configuration
DATABASE = os.path.join(os.getcwd(), 'sslExpiry.db')
DB_SCHEMA = os.path.join(os.getcwd(), 'schema.sql')

####################################################
# Some functions to handle the database


def connect_db(db_file=DATABASE):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn


def init_db():
    try:
        conn = connect_db(DATABASE)
        with open(DB_SCHEMA, mode='r') as f:
            cur = conn.cursor()
            cur.executescript(f.read())
            f.close()
            conn.commit()
    finally:
        conn.close()


def query_db(query, args=(), one=False):
    cur = connect_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


# ###################################################

def StoreDB(hostname, port, timestamp, remoteaddr):
    conn = connect_db(DATABASE)
    cur = conn.cursor()
    
    #to avoid SQL injection
    values_to_insert = [(hostname, port, remoteaddr, timestamp)]
    cur.executemany("""
        INSERT INTO metrics (hostname, port, remoteAddr, timestamp)
        VALUES (?,?,?,?);""", values_to_insert)
    conn.commit()

    return None


def GetDB():
    """
    Execute some queries and returns a dict
    """

    count_last_h = 0
    results = {}
    conn = connect_db(DATABASE)
    cur = conn.cursor()

    # Count of hostnames
    hostname_count = """SELECT COUNT(DISTINCT hostname) AS "Hostname_Count" FROM metrics;
    """
    cur.execute(hostname_count)
    try:
        counthostname, = cur.fetchone()
    except Exception:
        counthostname = 0

    # Last hostname
    last_hostname = """SELECT hostname FROM metrics ORDER BY timestamp DESC LIMIT 1;
    """
    cur.execute(last_hostname)
    try:
        lastcert, = cur.fetchone()
    except Exception:
        lastcert = "None"

    # Last hour checks
    current_time = datetime.now()
    lasthour = current_time.timestamp() - 3600
    count_last_hour = f"""SELECT COUNT(DISTINCT hostname) AS "LastHourCount" FROM metrics WHERE timestamp >= {lasthour};
    """
    cur.execute(count_last_hour)

    try:
        count_last_h, = cur.fetchone()
    except Exception:
        count_last_h = 0

    results = {
        "Hostname Count": counthostname,
        "Last Hostname": lastcert,
        "Last Hour Checks": count_last_h
    }
    conn.close()
    return results

# init DB at the first run.
if not os.path.isfile(DATABASE):
    init_db()

