#!/usr/bin/python  
import xmltv
import MySQLdb
filename = '/PATH/tvguide.xml'
db = MySQLdb.connect(host="localhost",user="USER",passwd="PASSWORD",db="mythconverg")
cur = db.cursor() 
channels = xmltv.read_channels(open(filename, 'r'))
for channel in channels:
	# This will only work if the 2nd value of display-name in the XML file is a numerical SID
        cur.execute("UPDATE channel SET xmltvid='" + channel['id'] + "' WHERE channum=" + channel['display-name'][1][0])
