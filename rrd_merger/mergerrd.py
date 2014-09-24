#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import sys

#判断用户输入的字符串
def str_decide(in_str):
	if (len(in_str) == 10) and in_str.isdigit():
		return True
	else:
		return False
#

#获取用户输入参数
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
		while (not str_decide(start)):
			start = raw_input("Bad file mode, Please input start time again:")
	
	if (len(sys.argv) >2) and (sys.argv[2].isdigit()):
		end = sys.argv[2]
	else:
		while (end == ""):
			end = raw_input("Please input end time:")
		while (not str_decide(end)):
			end = raw_input("Bad file mode, Please input end time again:")
			
	if (len(sys.argv) >3) and (sys.argv[3].isdigit()):
		offset = sys.argv[3]
	else:
		print "The offset default is 0"

	return start,end,offset
#

#获取需要修改的rrd文件列表
def GetFilelist():
	file_list = []
	file = open("filelist.txt")
	f = file.readlines()
	for x in f:
		#通过正则去过滤掉:1.文件列表中'#'号开头的注释 2.空白行
		if re.match(r'(^#|^$)',x):
			continue
		file_list.append((x.split()[0],x.split()[1]))
	file.close()
	return file_list
#

#执行系统命令，实现从备份数据中提取需要的数据
def fetch_data(rrdfile,start_time,end_time):
	cmd = "rrdtool fetch " + rrdfile + " AVERAGE --start " + start_time + " --end " + end_time + " > rrd_data.tmp"
	#print cmd
	a = os.system(cmd)
	f = open("rrd_data.tmp")
	rrd_data_array = f.readlines()
	f.close()
	rrd_data_dict = {}
	for x in rrd_data_array:
		#去除"rrdtool fetch"获取数据的非必要数据：1.空行 2.空白开头
		if re.match(r'(^\s|^$)',x):
			continue
		arr_a = x.split(":")
		rrd_data_dict[arr_a[0]] = arr_a[1].split()
	return rrd_data_dict
#

#The master core
#xml数据替换
def date_replace(xml_file,rrd_data,offset):
	f = open(xml_file)
	alllines = f.readlines()
	f.close()
	#遍历rrd_data，获取每个时间节点的数据值，去替换读xml生成的list
	for x in rrd_data:
		#x为获取到的时间点：1410425100
		i = 0
		while i < len(alllines):
			y = alllines[i]
			#print "y",y
			#y为需要进行替换的行：<!-- 2014-09-11 18:20:00 CST / 1410430800 --> <row><v>NaN</v><v>NaN</v></row>
			if (y.find(str(int(x) + offset)) >= 0):
				p1 = re.compile(r'<row><v>(\d.\.\d*.e\+\d*.|NaN)</v>')
				p2 = re.compile(r'<v>(\d.\.\d*.e\+\d*.|NaN)</v></row>')
				
				replace1 = "<row><v>" + rrd_data[x][0] + "</v>"
				replace2 = "<v>" + rrd_data[x][1] + "</v></row>"
				
				y = re.sub( p1, replace1, y)
				y = re.sub( p2, replace2, y)
				alllines[i] = y
				#通过正则替换后，生成新的准确的xml行：<!-- 2014-09-11 18:20:00 CST / 1410430800 --> <row><v>5.8968040288e+07</v><v>6.8763777241e+08</v></row>
			i += 1
	return alllines
#

#执行系统命令，实现rrd到xml的转换
def rrd_to_xml(rrdfile):
	(filepath,filename)=os.path.split(rrdfile)
	to_xml_file = filepath + os.sep + filename.split('.')[0] + ".xml"
	cmd = r"rrdtool dump "+ rrdfile + r" > " + to_xml_file
	os.system(cmd)
	return to_xml_file
#

#执行系统命令，实现xml到rrd的转换恢复，完成修改任务
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

#程序入口
if __name__ == "__main__":
	(start,end,offset) = getUserInput()
	
	#file_array:rrd文件对应列表	[('/root/work/1164.rrd', '/root/work/lax1-cr02_traffic_in_352.rrd')]
	file_array = GetFilelist()

	for x in file_array:
		#进行文件转换
		#1.主:xml_file_a	需要修改数据的文件
		#2.备:ml_file_b		需要提取数据的文件
		(xml_file,rrd_data) = (rrd_to_xml(x[0]),fetch_data(x[1],start,end))
		print "step 1", os.system("date")
		#xml_file:[string]	需要修改rrd转换成的xml文件	/root/work/1164.xml
		#rrd_data:[dict]	作为替换xml文件的原始数据	{'1410411600': ['4.2562895157e+07', '7.4280305788e+08'],...}
		#offset:[int]		时间偏移量
		arr_replace_ok = date_replace(xml_file,rrd_data,offset)
		#arr_replace_ok = ["a","a","a","a"]
		print "step 2",os.system("date")
		xml_to_rrd(x[0],xml_file,arr_replace_ok)
		
		#a = raw_input()
print "step 3", os.system("date")
#
