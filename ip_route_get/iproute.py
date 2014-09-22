#! /usr/bin/env python
# -*- coding:utf8 -*-

from urllib import urlopen
import re
import math
import os
import threading
from time import sleep
def networks():
    f = urlopen('http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest')
    if f.getcode() == 200:
        ipmask = [((re.split('\|', network)[3]) + '/' + str(32 - int(math.log(float(re.split('\|', network)[4]), 2)))) \
               for network in f.readlines() if 'apnic|CN|ipv4|' in network]
        num = int(len(ipmask) / 30 + 1)
        #需要优化
        return [ipmask[(30 * i):((30 * i) + 30)] for i in range(num)]

    else:
        print '打开http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest网页失败！！！'

def ipList(sec, ipmasks):
    ipFiles = ['unicom.txt', 'telecom.txt', 'cmcc.txt', 'other.txt']
    for ipFile in ipFiles:
        while os.path.isfile(ipFile):
            os.remove(ipFile)

    for ipmask in ipmasks:
        fil = urlopen('http://wq.apnic.net/apnic-bin/whois.pl?searchtext=' \
                      + str(re.split('/', ipmask)[0]) + '&form_type=advanced')
        if fil.getcode() == 200:
            fl = fil.read()

            if re.search('UNICOM|Unicom|unicom|cnc|CNC', fl)is not None:
                unicom = open('unicom.txt', 'a')
                unicom.write(ipmask + '\n')
                unicom.close()

            elif re.search('CHINANET|Telecom|TELECOM|chinanet|telecom', fl) is not None:
                telecom = open('telecom.txt', 'a')
                telecom.write(ipmask + '\n')
                telecom.close()

            elif re.search('CMCC|cmcc|CRTC|crtc', fl) is not None:
                cmcc = open('cmcc.txt', 'a')
                cmcc.write(ipmask + '\n')
                cmcc.close()
            else:
                other = open('other.txt', 'a')
                other.write(ipmask + '\n')
                other.close()

        else:
            print '打开' + fil.geturl() + '网页失败！！！'

        fil.close()
        sleep(10)
    sleep(sec)

def main():
    threads = []
    ipmasks = networks()
    nipmasks = range(len(ipmasks))
    for i in nipmasks:
        t = threading.Thread(target=ipList, args=(10, ipmasks[i]))
        threads.append(t)
    for i in nipmasks:
        threads[i].start()
    for i in nipmasks:
        threads[i].join()

if __name__ == '__main__':
        main()
