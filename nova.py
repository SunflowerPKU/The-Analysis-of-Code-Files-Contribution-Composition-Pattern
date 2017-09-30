#相关度量计算脚本
#Author: TAN XIN
#2017/9/30


#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import division
from datetime import datetime
import pymysql
import pylab
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import scipy.optimize as opt
import csv
from numpy import *
import math


conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='413372', db='openstack_sourcecode', charset='utf8')
cursor = conn.cursor()


version_date = ['2009-01-01', '2010-10-21', '2011-02-03','2011-04-15','2011-09-22','2012-04-05','2012-09-27','2013-04-04'
                ,'2013-10-17','2014-04-17','2014-10-16','2015-04-30','2015-10-16','2016-04-07','2016-10-06']


#量度一：贡献组成的集中度

for i in range(15):
    
    start_time = datetime.date(datetime.strptime(version_date[i], '%Y-%m-%d'))
    end_time = datetime.date(datetime.strptime(version_date[i + 1], '%Y-%m-%d'))
    print start_time, end_time

    cursor.execute("SELECT author_id, count(distinct id)"
                   "FROM commit_log "
                   "where author_date between %s and %s "
                   "and respository_id = 226 "
                   "group by author_id "
                   "order by count(distinct id) desc",
                   (start_time, end_time))
    res = cursor.fetchall()
    #print res

    cursor.execute("SELECT count(distinct id) "
                   "FROM commit_log "
                   "where respository_id = 226 "
                   "and author_date between %s and %s ", (start_time, end_time))
    all_commits = cursor.fetchall()[0][0]
    max_author = res[0][0]
    max_commits = res[0][1]/all_commits
    
    print res
    print '#####################################'
    print all_commits
    print max_author
    print max_commits

    cursor.execute("INSERT INTO max_commit(version, author_id, m1)"
                   "VALUES(%s, %s, %s)", (i + 1,max_author,max_commits))



 #量度二：贡献组成的复杂度

 for i in range(15):
    
    shang = 0
    start_time = datetime.date(datetime.strptime(version_date[i], '%Y-%m-%d'))
    end_time = datetime.date(datetime.strptime(version_date[i + 1], '%Y-%m-%d'))
    print start_time, end_time

    cursor.execute("SELECT author_id, count(distinct id)"
                   "FROM commit_log "
                   "where author_date between %s and %s "
                   "and respository_id = 226 "
                   "group by author_id "
                   "order by count(distinct id) desc",
                   (start_time, end_time))
    res = cursor.fetchall()
    #print res

    cursor.execute("SELECT count(distinct id) "
                   "FROM commit_log "
                   "where respository_id = 226 "
                   "and author_date between %s and %s ", (start_time, end_time))
    all_commits = cursor.fetchall()[0][0]
    
    for j in range(len(res)):
      p = res[j][1]/all_commits
      shang += -p*math.log(p, 2)

    
    print shang 
    print '#####################################'

    cursor.execute("INSERT INTO shang_commit(version, m2)"
                   "VALUES(%s, %s)", (i + 1, shang))


#度量三：贡献组成的稳定性

#1)计算新加入的志愿者数

tmp1 = []
start_time1 = datetime.date(datetime.strptime(version_date[0], '%Y-%m-%d'))
end_time1 = datetime.date(datetime.strptime(version_date[1], '%Y-%m-%d'))
cursor.execute("SELECT distinct author_id "
               "FROM commit_log "
               "where author_date between %s and %s" ,
               (start_time1, end_time1))
res = cursor.fetchall()
for j in range(len(res)):
  tmp1.append(res[j][0])
#print tmp1

for i in range(15):
  res = []
  tmp = []
  result = 0
  if i > 0:
      
    start_time = datetime.date(datetime.strptime(version_date[i], '%Y-%m-%d'))
    end_time = datetime.date(datetime.strptime(version_date[i + 1], '%Y-%m-%d'))
    cursor.execute("SELECT distinct author_id "
                  "FROM commit_log "
                  "where author_date between %s and %s",
                  (start_time, end_time))
    res = cursor.fetchall()
    for j in range(len(res)):
      tmp.append(res[j][0])
    for item in tmp:
      if item not in tmp1:
        result += 1
    tmp1 = tmp
    #print result
   
    cursor.execute("INSERT INTO newcomer(version, num)"
                   "VALUES(%s, %s)", (i + 1, result))
    

#2)计算离开的志愿者数

tmp1 = []
start_time1 = datetime.date(datetime.strptime(version_date[0], '%Y-%m-%d'))
end_time1 = datetime.date(datetime.strptime(version_date[1], '%Y-%m-%d'))
cursor.execute("SELECT distinct author_id "
               "FROM commit_log "
               "where author_date between %s and %s",
               (start_time1, end_time1))
res = cursor.fetchall()
for j in range(len(res)):
  tmp1.append(res[j][0])
#print tmp1

for i in range(15):
  res = []
  tmp = []
  result = 0
  if i > 0:
      
    start_time = datetime.date(datetime.strptime(version_date[i], '%Y-%m-%d'))
    end_time = datetime.date(datetime.strptime(version_date[i + 1], '%Y-%m-%d'))
    cursor.execute("SELECT distinct author_id "
                  "FROM commit_log "
                  "where author_date between %s and %s ",
                  (start_time, end_time))
    res = cursor.fetchall()
    for j in range(len(res)):
      tmp.append(res[j][0])
    for item in tmp:
      if item in tmp1:
        result += 1
    tmp1 = tmp
    #print result
   
    cursor.execute("INSERT INTO stayer(version, num)"
                   "VALUES(%s, %s)", (i + 1, result))

conn.commit()
cursor.close()
conn.close()
    