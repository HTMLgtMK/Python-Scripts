#/usr/bin/python3
# -*- coding:utf-8 -*-

'''
抓取国科大的联系方式
author: GT
time: 2018/09/30
'''

import urllib3
import re

class Downloader(object):

	def __init__(self):
		pass

	@staticmethod
	def download(url):
		manager = urllib3.PoolManager()
		conn = manager.request("GET",url)
		if conn.status == 200 :
			data = conn.data.decode("utf-8")
			return data
		else:
			return conn
		pass
	pass

class Parser(object):
	'''解析学校的联系方式'''
	def __init__(self):
		pass

	@staticmethod
	def parse(content):
		pattern = r'<div class="gksq[\s\S]*?"><h1>[\s\S]*?</h1>([\s\S]*?)</div>'
		iterObj = re.finditer(pattern, content)
		allContacts = []
		for it in iterObj:
			contacts = it.group(1)
			contacts = re.sub(r'\s', '', contacts) # 去掉（疑似）空白
			pattern = r'<p>([\s\S]*?)</p>'
			contacts = re.findall(pattern, contacts)
			pattern = r'：' # 中文冒号
			pattern = re.compile(pattern)
			arr = []
			for item in contacts[1:]:
				item = re.split(pattern, item)
				if len(item) != 2 :
					continue
				item = {item[0] : item[1]}
				arr.append(item)
				pass
			contacts = { contacts[0] : arr }
			allContacts.append(contacts)
			pass
		# print(allContacts)
		return allContacts
		pass
	pass


base = 'http://www.ucas.ac.cn/XXGK'
data = Downloader.download(base)
if isinstance(data, urllib3.HTTPResponse):
	print("download text failed %d" %(data.status))
	exit(0)
else:
	attach = Parser.parse(data)
	print(attach)

