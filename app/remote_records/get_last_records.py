#Module to retreive the last record from the activity database
import sqlite3

def get_last_records():


    conn=sqlite3.connect('/var/www/my_room_env_v2/app/data_base/ac_state_record.db')
    curs=conn.cursor()
    curs.execute("select * from STATUS order by rDAtetime desc limit 1;")
    last_record = curs.fetchall()
    conn.close()

    return last_record
