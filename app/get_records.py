#Module to retreive temperature history requested by the client to publish on the temperature vs time graph

import sqlite3
import json

def getrecords(hours):
    conn=sqlite3.connect('/var/www/lab_app/lab_app.db')
    curs=conn.cursor()
    curs.execute("select * from temperatures where rDatetime >= datetime('now','localtime', ?)", (hours,))
    temp = curs.fetchall()
    conn.close()
    
    temp_data = {}
    for i in range(len(temp)):
        temp_dict={}
        temp_dict['hrs'] = int(temp[i][0][11:13])
        temp_dict['mins'] = int(temp[i][0][14:16])
        temp_dict['sec'] = int(temp[i][0][17:])
        temp_dict['temp'] = temp[i][2]
        temp_data['data_'+str(i)] = temp_dict
    jsonStr = json.dumps(temp_data)

    return jsonStr
