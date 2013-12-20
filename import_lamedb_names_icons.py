#!/usr/bin/python
#
# This script will look at lamedb channel names from a dreambox and import them to MythTV
# It will also import channel icons (db picon format) and import them to MythTV
#
# Pieces of this were stolen from everywhere, mostly here:
# scriptlib.py  by Ambrosa http://www.ambrosa.net
#
# This probably won't work for you, and I've removed basically all the error checking.
#
# You've been warned, be sure to back up your Myth DB before running this garbage.

import os
import sys
import time
import re
import MySQLdb
import shutil

# Define variables
lamedb_path="/root/"
lamedb=lamedb_path + "lamedb"
picon_path="/picon/"
mythicon_path="/mythtv/.mythtv/channels/"


db = MySQLdb.connect(host="localhost",user="mythtv",passwd="PASSWORD",db="mythconverg")
cur = db.cursor() 


def decode_charset(s):
	u = None
	charset_list = ('utf-8','iso-8859-1','iso-8859-2','iso-8859-15')

	for charset in charset_list:
		try:
			u = unicode(s,charset,"strict")
		except:
			pass
		else:
			break

	if u == None:
		print("CHARSET ERROR while decoding lamedb")
		sys.exit(1)
	else:
		return(u)



def read_lamedb():
	if not os.path.exists(lamedb):
		print("ERROR ! \'%s\' NOT FOUND" % lamedb)
		sys.exit(1)
	# lamedb mix UTF-8 + iso-8859-* inside it
	# need charset decoding line by line
	fd = open(lamedb,"r")

	# skip transponder section
	# read lamedb until are found "end" and "services" lines
	while True:
		temp = decode_charset(fd.readline())
		if temp == '' :
			print("ERROR parsing lamedb, transponder section: end of file")
			sys.exit(1)

		temp = temp.strip(' \n\r')
		if temp == u"end":
			# next line should be "services"
			temp = decode_charset(fd.readline())
			temp = temp.strip(' \n\r')
			if temp == u'services':
				# reached end of transponder section, end loop and continue with parsing channel section
				break
			else:
				print("ERROR parsing lamedb, transponder section: not found \"end + services\" lines")
				sys.exit(1)

	# parsing lamedb channel section
	while True:
		sid = decode_charset(fd.readline()) # read SID , it's the first line
		channum=convert_sid(sid)
		if sid == '' :
			print("ERROR parsing lamedb, channel_name section: end of file")
			sys.exit(1)

		sid = sid.strip(' \n\r')

		if sid == u'end':
			# reached end of channel section, end loop
			break;

		channel_name = decode_charset(fd.readline()) # read channel name, this is the second line
		channel_name=channel_name.encode('utf-8')
		icon = re.sub('[^a-zA-Z0-9\n\.]', '', channel_name)
		icon = icon.replace('\n', '')
		icon = mythicon_path + icon + ".png"
		sid = sid.upper()
		tmp = sid.split(":")
		picon = picon_path + "1_0_1_" + tmp[0].lstrip("0") + "_" + tmp[2].lstrip("0") + "_" + tmp[3].lstrip("0") + "_" + tmp[1].lstrip("0") + "_0_0_0.png"
		fd.readline() # read the third line (provider) but do nothing since we're not using it
		cur.execute("UPDATE channel SET name='" + re.escape(channel_name) + "' WHERE channum=" + str(channum[0]))
		if os.path.exists(picon):
			print("importing icon for " + channel_name.replace('\n', '') + "...")
			shutil.copyfile(picon, icon)
			cur.execute("UPDATE channel SET icon='" + icon + "' WHERE channum=" + str(channum[0]))
		else:
			print("ERROR: icon for " + channel_name.replace('\n', '') + " doesn't exist!" + " (" + picon + ")")

	fd.close()


def convert_sid(sid):
	s=[]

	# SID:ns:TSID:ONID:stype:unused

	try:
		tmp = sid.split(":")
		s.append(int(tmp[0],0x10))  # SID
		s.append(int(tmp[2],0X10))  # TSID
		s.append(int(tmp[3],0X10))  # ONID
	except:
		pass

	return(s)



read_lamedb()

