#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import sys

#��ȡ�û��������
def getUserInput():
	start = ""
	end = ""
	offset = 0
	if (len(sys.argv) == 1) or (sys.argv[1] == "-h") or (sys.argv[1] == "--help"):
		print "Usage: " + sys.argv[0] + " start-time end-time offset-time"
	
	if (len(sys.argv) >1) and (sys.argv[1].isdigit()):
		start = sys.argv[1]
	else:
		while (start == ""):
			start = raw_input("Please input start time:")
	
	if (len(sys.argv) >2) and (sys.argv[2].isdigit()):
		end = sys.argv[2]
	else:
		while (end == ""):
			end = raw_input("Please input end time:")

	if (len(sys.argv) >3) and (sys.argv[3].isdigit()):
		offset = sys.argv[3]
	else:
		print "offset default is 0"

	return start,end,offset
#

#��ȡ��Ҫ�޸ĵ�rrd�ļ��б�
def GetFilelist():
	file_list = []
	file = open("filelist.txt")
	f = file.readlines()
	for x in f:
		#ͨ������ȥ���˵�:1.�ļ��б���'#'�ſ�ͷ��ע�� 2.�հ���
		if re.match(r'(^#|^$)',x):
			continue
		file_list.append((x.split()[0],x.split()[1]))
	file.close()
	return file_list
#

#ִ��ϵͳ���ʵ�ִӱ�����������ȡ��Ҫ������
def fetch_data(rrdfile,start_time,end_time):
	cmd = "rrdtool fetch " + rrdfile + " AVERAGE --start " + start_time + " --end " + end_time + " > rrd_data.tmp"
	#print cmd
	a = os.system(cmd)
	f = open("rrd_data.tmp")
	rrd_data_array = f.readlines()
	f.close()
	rrd_data_dict = {}
	for x in rrd_data_array:
		#ȥ��"rrdtool fetch"��ȡ���ݵķǱ�Ҫ���ݣ�1.���� 2.�հ׿�ͷ
		if re.match(r'(^\s|^$)',x):
			continue
		arr_a = x.split(":")
		rrd_data_dict[arr_a[0]] = arr_a[1].split()
	return rrd_data_dict
#

#The master core
#xml�����滻
def date_replace(xml_file,rrd_data,offset):
	f = open(xml_file)
	alllines = f.readlines()
	f.close()
	#����rrd_data����ȡÿ��ʱ��ڵ������ֵ��ȥ�滻��xml���ɵ�list
	for x in rrd_data:
		#xΪ��ȡ����ʱ��㣺1410425100
		i = 0
		while i < len(alllines):
			y = alllines[i]
			#print "y",y
			#yΪ��Ҫ�����滻���У�<!-- 2014-09-11 18:20:00 CST / 1410430800 --> <row><v>NaN</v><v>NaN</v></row>
			if (y.find(str(int(x) + offset)) >= 0):
				p1 = re.compile(r'<row><v>(\d.\.\d*.e\+\d*.|NaN)</v>')
				p2 = re.compile(r'<v>(\d.\.\d*.e\+\d*.|NaN)</v></row>')
				
				replace1 = "<row><v>" + rrd_data[x][0] + "</v>"
				replace2 = "<v>" + rrd_data[x][1] + "</v></row>"
				
				y = re.sub( p1, replace1, y)
				y = re.sub( p2, replace2, y)
				alllines[i] = y
				#ͨ�������滻�������µ�׼ȷ��xml�У�<!-- 2014-09-11 18:20:00 CST / 1410430800 --> <row><v>5.8968040288e+07</v><v>6.8763777241e+08</v></row>
			i += 1
	return alllines
#

#ִ��ϵͳ���ʵ��rrd��xml��ת��
def rrd_to_xml(rrdfile):
	(filepath,filename)=os.path.split(rrdfile)
	to_xml_file = filepath + os.sep + filename.split('.')[0] + ".xml"
	cmd = r"rrdtool dump "+ rrdfile + r" > " + to_xml_file
	os.system(cmd)
	return to_xml_file
#

#ִ��ϵͳ���ʵ��xml��rrd��ת���ָ�������޸�����
def xml_to_rrd(rrdfile,xmlfile,arr):
	os.rename(xmlfile,xmlfile + ".bak")
	print "\t debug1"
	f = open(xmlfile,"w")
	f.writelines(arr)
	f.close()
	print "\t debug2"
	os.rename(rrdfile,rrdfile + ".bak")
	print "\t debug3"
	cmd = r"rrdtool restore -f "+ xmlfile + " " + rrdfile
	print "\t debug4"
	os.system(cmd)
#

#�������
if __name__ == "__main__":
	(start,end,offset) = getUserInput()
	
	#file_array:rrd�ļ���Ӧ�б�	[('/root/work/1164.rrd', '/root/work/lax1-cr02_traffic_in_352.rrd')]
	file_array = GetFilelist()

	for x in file_array:
		#�����ļ�ת��
		#1.��:xml_file_a	��Ҫ�޸����ݵ��ļ�
		#2.��:ml_file_b		��Ҫ��ȡ���ݵ��ļ�
		(xml_file,rrd_data) = (rrd_to_xml(x[0]),fetch_data(x[1],start,end))
		print "step 1", os.system("date")
		#xml_file:[string]	��Ҫ�޸�rrdת���ɵ�xml�ļ�	/root/work/1164.xml
		#rrd_data:[dict]	��Ϊ�滻xml�ļ���ԭʼ����	{'1410411600': ['4.2562895157e+07', '7.4280305788e+08'],...}
		#offset:[int]		ʱ��ƫ����
		arr_replace_ok = date_replace(xml_file,rrd_data,offset)
		#arr_replace_ok = ["a","a","a","a"]
		print "step 2",os.system("date")
		xml_to_rrd(x[0],xml_file,arr_replace_ok)
		
		#a = raw_input()
print "step 3", os.system("date")
#
