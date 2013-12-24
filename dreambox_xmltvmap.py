#!/usr/bin/python
#
# This script will look at lamedb from a dreambox (enigma2) and XML output from MC2XML.
#
# It will generate a channels.xml used with the dreambox epgimport plugin.
#
# Pieces of this were stolen from everywhere, mostly here:
# scriptlib.py  by Ambrosa http://www.ambrosa.net
#
# This probably won't work for you, and I've removed basically all the error checking.
#
# You've been warned, be sure to back up your data before running this garbage.

import os
import sys
import time
import re
import shutil
import xmltv
# Define variables
lamedb_path="/xmltv/"
lamedb=lamedb_path + "lamedb"
xmltv_file="/xmltv/tvguidesat.xml"
map_file="/xmltv/channels.xml"
xml_channels = xmltv.read_channels(open(xmltv_file, 'r'))
combined_dict = {}

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
	fm = open(map_file,"w")
	fm.write("<?xml version=\"1.0\" encoding=\"latin-1\"?>\n")
	fm.write("<channels>\n")
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
		channel_name=channel_name.strip(' \n\r')
		tmp = sid.split(":")
		sid = "1:0:1:" + tmp[0] + ":" + tmp[2] + ":" + tmp[3] + ":" + tmp[1] + ":0:0:0:"
		str_channum = str(channum[0])
		dict_value = (sid,channel_name)
		if combined_dict.has_key(str_channum):
			combined_dict[str_channum].append(dict_value)
		else:
			combined_dict[str_channum]=[dict_value]
		fd.readline() # read the third line (provider) but do nothing since we're not using it
	fd.close()
	# Start writing output
	for xml_channel in xml_channels:
		xml_sid = xml_channel['display-name'][1][0]
		if combined_dict.has_key(xml_sid):
			fm.write("<channel id=\"" + xml_channel['id'] + "\">" + combined_dict[xml_sid][0][0] + "</channel>" + " <!-- " + combined_dict[xml_sid][0][1] + " - " + xml_sid + " -->" + "\n")
	fm.write("</channels>\n")
	fm.close()

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

