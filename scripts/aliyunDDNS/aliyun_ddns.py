#!/usr/bin/env python3
#coding=utf-8

import os
import time
import json
import urllib

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkalidns.request.v20150109 import DescribeSubDomainRecordsRequest, AddDomainRecordRequest, UpdateDomainRecordRequest, DeleteDomainRecordRequest
 
configPath = '/home/user/data/script/aliyunDDNS/ddns_config.json'
logFilePath = '/home/user/data/script/aliyunDDNS/operation_ddns.log'
  
# 初始化阿里云配置
with open(configPath, 'r', encoding='utf-8') as file:  
    envConfig = json.load(file)  
print(envConfig)  

## 建议使用 RAM 子账户的 KEY 和 SECRET 增加安全性
AccessKey = envConfig['access_key_id']
Secret = envConfig['access_key_secret']
RegionId = envConfig['region_id']
DomainName = envConfig['domain_name']

client = AcsClient(AccessKey, Secret, RegionId)

 
# 子域名列表
SubDomainList = ['www','@']
 
# 获取Ipv4公网地址
def getIPv4():
  ipv4 = json.load(urllib.request.urlopen('https://api.ipify.org/?format=json'))['ip']
  return ipv4

# 获取Ipv6公网地址
def getIPv6():
  ipv6 = json.load(urllib.request.urlopen('https://ipv6.lookup.test-ipv6.com'))['ip']
  return ipv6
 
# 查询DNS记录
def getDomainInfo(SubDomain):
  request = DescribeSubDomainRecordsRequest.DescribeSubDomainRecordsRequest()
  request.set_accept_format('json')
 
  # 设置要查询的记录类型为 A记录
  request.set_Type("A")
  request.set_SubDomain(SubDomain)
 
  response = client.do_action_with_exception(request)
  response = str(response, encoding='utf-8')
 
  return json.loads(response)
 
# 新增DNS记录 (默认都设置为A记录，通过配置set_Type可设置为其他记录)
def addDomainRecord(client,value,rr,domainname):
  request = AddDomainRecordRequest.AddDomainRecordRequest()
  request.set_accept_format('json')
 
  # request.set_Priority('1') # MX 记录时的必选参数
  request.set_TTL('600')    # 可选值的范围取决于你的阿里云账户等级，免费版为 600 - 86400 单位为秒 
  request.set_Value(value)   # 新增的 ip 地址
  request.set_Type('A')    # 记录类型
  request.set_RR(rr)      # 子域名名称 
  request.set_DomainName(domainname) #主域名
 
  # 获取记录信息，返回信息中包含 TotalCount 字段，表示获取到的记录条数 0 表示没有记录， 其他数字为多少表示有多少条相同记录，正常有记录的值应该为1，如果值大于1则应该检查是不是重复添加了相同的记录
  response = client.do_action_with_exception(request)
  response = str(response, encoding='utf-8')
  relsult = json.loads(response)
  return relsult
 
# 更新DNS记录
def updateDomainRecord(client,value,rr,record_id):
  request = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
  request.set_accept_format('json')
 
  # request.set_Priority('1')
  request.set_TTL('600')
  request.set_Value(value) # 新的ip地址
  request.set_Type('A')
  request.set_RR(rr)
  request.set_RecordId(record_id) # 更新记录需要指定 record_id ，该字段为记录的唯一标识，可以在获取方法的返回信息中得到该字段的值
 
  response = client.do_action_with_exception(request)
  response = str(response, encoding='utf-8')
  return response
 
# 删除DNS记录
def delDomainRecord(client,subdomain):
  info = getDomainInfo(subdomain)
  if info['TotalCount'] == 0:
    print('没有相关的记录信息，删除失败！')
  elif info["TotalCount"] == 1:
    print('准备删除记录')
    request = DeleteDomainRecordRequest.DeleteDomainRecordRequest()
    request.set_accept_format('json')
 
    record_id = info["DomainRecords"]["Record"][0]["RecordId"]
    request.set_RecordId(record_id) # 删除记录需要指定 record_id ，该字段为记录的唯一标识，可以在获取方法的返回信息中得到该字段的值
    result = client.do_action_with_exception(request)
    print('删除成功，返回信息：')
    print(result)
  else:
    # 正常不应该有多条相同的记录，如果存在这种情况，应该手动去网站检查核实是否有操作失误
    print("存在多个相同子域名解析记录值，请核查后再操作！")
 
# 有记录则更新，没有记录则新增
def setDomainRecord(client,value,rr,domainname):

  logPrefix = '操作时间：' + time.asctime(time.localtime(time.time())) + '\n'
  logContent = '操作结果：'

  info = getDomainInfo(rr + '.' + domainname)
  if info['TotalCount'] == 0:
    print('准备添加新记录')
    add_result = addDomainRecord(client,value,rr,domainname)
    print(add_result)
    logContent = logContent + '准备添加新记录 -> ' + add_result
  elif info["TotalCount"] == 1:
    print('准备更新已有记录')
    record_id = info["DomainRecords"]["Record"][0]["RecordId"]
    cur_ip = getIPv4()
    old_ip = info["DomainRecords"]["Record"][0]["Value"]
    if cur_ip == old_ip:
      print ("新ip与原ip相同，无法更新！")
      logContent = logContent + '准备更新已有记录 -> 新ip与原ip相同，无法更新！'
    else:
      update_result = updateDomainRecord(client,value,rr,record_id)
      print('更新成功，返回信息：')
      print(update_result)
      logContent = logContent + '准备更新已有记录 -> ' + update_result
  else:
    # 正常不应该有多条相同的记录，如果存在这种情况，应该手动去网站检查核实是否有操作失误
    print("存在多个相同子域名解析记录值，请核查删除后再操作！")
    logContent = logContent + "存在多个相同子域名解析记录值，请核查删除后再操作！"

  return logPrefix + logContent


#### 执行相关操作

IPv4 = getIPv4()
 
# 循环子域名列表进行批量操作
lines = 'DomainName=' + DomainName
for subdomain in SubDomainList:
  recordLog = setDomainRecord(client,IPv4,subdomain,DomainName)
  lines = lines + '\n subdomain=' + subdomain + '\n' + recordLog

# 将操作记录到本地
with open(logFilePath, 'w', encoding='utf-8') as logFile:
  logFile.writelines(lines)
 
# 删除记录测试
# delDomainRecord(client,subdomain)
 
# 新增或更新记录测试
# setDomainRecord(client,'192.168.1.123','recordId',DomainName)
 
# 批量获取记录测试
# for x in SubDomainList:
#   print (getDomainInfo(DomainName, x))
 
# 获取外网ip地址测试
# print ('(' + getIPv4() + ')')
