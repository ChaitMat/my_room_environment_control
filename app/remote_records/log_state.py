#Module record the activity in the database.

import sqlite3

def log_remote_state(state, temperature, fan_speed):
	conn=sqlite3.connect('/var/www/my_room_env_v2/app/data_base/ac_state_record.db')
	curs=conn.cursor()
	curs.execute("""INSERT INTO STATUS values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?),(?),(?))""", (state, temperature, fan_speed))
	conn.commit()
	conn.close()
