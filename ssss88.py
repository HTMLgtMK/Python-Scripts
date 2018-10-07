#!/usr/bin/python3
# -*- coding:utf-8 -*-

'''
下载网址http://www.ssss88.com/p02/index.html中的全部图片
author:GT
time: 2018/10/04
'''

'''
1. 首先链接首页, 获取总的页数
2. 从最后一页到第一页, 依次抓取页面, 分析
3. 将已经抓取的图片链接保存到数据库中
4. 将每个页面按照 /日期/文件夹名/图片名存储

表1 图片表
-------------------------------------------
链接 | 文件夹名称 | 上传日期 | 下载状态
-------------------------------------------

'''

import urllib3
import re
import os
import pymongo

class Downloader(object):
	"下载器"
	def __init__(self):
		pass

	@staticmethod
	def download(url):
		manager = urllib3.PoolManager()
		response = manager.request('GET', url)
		if 200 == response.status:
			content = response.data.decode('utf-8')
			return content
		else:
			return response
		pass
	pass

class Parser(object):
	"解析器"
	def __init__(self):
		pass

	def getPageCounts(self, content):
		'''
		获取页面总数
		'''
		searchObj = re.search(r'<div id="page" class="bord mtop">[\s\S]*?</font>/([\d]*?)</strong>', content)
		if searchObj == None:
			return 0
		else:
			return int(searchObj.group(1))
		pass

	def getNext(self, content):
		'''
		获取下一页的链接
		'''
		searchObj = re.search(r'</span><a href=\'([\s\S]*?)\'title="下一页" class="PageBox">', content)
		if searchObj == None:
			return None
		nextUrl = searchObj.group(1)
		if nextUrl.startswith('http') :
			return nextUrl
		else:
			return 'http://www.ssss88.com'+nextUrl
		pass

	def parsePage(self, content):
		'''
		返回该页面下所有图片集链接等信息
		数据结构:{'link':url, 'name':name, 'date':date}
		'''
		searchObj = re.search(r'<div class="typelist">([\s\S]*?)</div>', content)
		if searchObj == None:
			return [] # 该页图片集列表
		content = searchObj.group(1)
		pattern = r'<a[\s\S]*?href="([\s\S]*?)"[\s\S]*?>([\s\S]*?)</a>[\s\S]*?<font[\s\S]*?>([\s\S]*?)</font>'
		lists = re.findall(pattern, content)
		return lists
		pass

	def parseImgs(self, content):
		'''
		解析详情页面的图片信息, 返回图片链接列表
		爬取得到的链接省略了域名:http://9tmz.8iwvsl.com/110C0D/p02/
		'''
		searchObj = re.search(r'<div id="view1" class="mtop">([\s\S]*?)</div>', content)
		if searchObj == None:
			return [] # 该页图片为空
		content = searchObj.group(1)
		lists = re.findall(r'src="([\s\S]*?)"', content)
		return lists
		pass

	pass

class DBHelper(object):
	"数据库帮助类"
	def __init__(self):
		'''初始化数据库连接'''
		self.__myclient = pymongo.MongoClient('mongodb://localhost:27017/')
		self.__mydb = self.__myclient['db_ssss88']
		self.__mytable = self.__mydb['tb_items']
		pass

	def addItems(self, items):
		'''
		添加一项('link', 'name', 'date') insert_one
		添加多项[items] insert_many()
		'''
		data = []
		for item in items:
			mdict = {'link': item[0], 'name':item[1], 'date':item[2], 'status': 0 }
			data.append(mdict)
			pass
		return self.__mytable.insert_many(data)
		pass

	def findItems(self, page=1, limit=30):
		'''
		查找数据
		'''
		cursor = self.__mytable.find({'status':{"$eq":0}}).limit(limit).skip((page-1)*limit)
		data = []
		for c in cursor:
			data.append(c)
		return data
		pass

	def updateItem(self, link, status=1):
		'''
		修改数据状态
		'''
		where = {'link':link}
		update = { "$set" : {"status" : 1}}
		self.__mytable.update(where, update)
		pass

	pass

class Main(object):
	"主要流程控制类"

	def __init__(self):
		self.__parser = Parser()
		self.__dbHelper = DBHelper()
		pass

	def getAllPages(self):
		"先获取全部图片集"
		url = "http://www.ssss88.com/p02/index.html"
		count = 1
		while url != None :
			print("%d >>  download %s" %(count, url))
			content = Downloader.download(url)
			url = None
			# print(content)
			url = self.__parser.getNext(content)
			print("%d >> get Next : %s" %(count, url))
			lists = self.__parser.parsePage(content)
			self.__dbHelper.addItems(lists)
			print("%d : add %s to db" %(count, url))
			count = count + 1
			pass
		pass

	def getAllItems(self):
		'''
		获取全部的图片
		每次从数据库中取出30条数据到内存中
		下载完成后,修改数据库中对应状态值为1
		并且讲该项数据从内存中移除
		'''
		page = 1 # 当前页数
		limit = 30 # 每页的条数
		path = 'ssss88_files'
		manager = urllib3.PoolManager()
		try:
			os.mkdir(path)
		except:
			pass
		while True:
			datas = self.__dbHelper.findItems(page, limit)
			page = page+1
			for item in datas:
				# 先创建文件夹
				try:
					os.mkdir(path + '/' + item['date'])
				except:
					pass
				try:
					os.mkdir(path + '/' + item['date'] + '/' + item['name'])
				except:
					pass
				# 获取图片集链接
				if item['link'].startswith('http') :
					url = item['link']
				else:
					url = 'http://www.ssss88.com' + item['link']
				content = Downloader.download(url)
				lists = self.__parser.parseImgs(content)
				# 依次爬取图片保存成图片文件
				flag = False
				for index, href in enumerate(lists):
					print(href)
					# filename = re.search(r'\/([\s\S]*?)', href).group(1)
					filename = str(index) + '.jpg'
					print(filename)
					# href = 'http://9tmz.8iwvsl.com/110C0D/p02/' + href
					with open(path + '/' + item['date'] + '/' + item['name'] + '/' + filename, 'wb') as handle:
						res = manager.request('GET', href)
						if res.status != 200:
							flag = True
							continue
						else:
							handle.write(res.data)
				# 标记本项目已经爬取成功
				if flag: # 存在图片保存失败
					continue
				self.__dbHelper.updateItem(item['link'], 1)
				print("%s download success !" %(item['link']))
				pass
			if len(datas) == 0:
				break
		pass

	def start(self):
		# self.getAllPages()
		self.getAllItems()
		pass

	pass

class Test(object):

	def __init__(self):
		pass

	@staticmethod
	def testGetPageCount():
		f = open("亚洲色图 - 1插菊花综合网.html", 'r')
		content = f.read()
		f.close()
		parser = Parser()
		print(parser.getPageCounts(content))
		pass

	@staticmethod
	def testGetNext():
		f = open("list_187.html", 'r')
		content = f.read()
		f.close()
		parser = Parser()
		print(parser.getNext(content))
		pass

	@staticmethod
	def testParsePage():
		f = open("亚洲色图 - 1插菊花综合网.html", 'r')
		content = f.read()
		f.close()
		parser = Parser()
		print(parser.parsePage(content))
		pass

	@staticmethod
	def testParseImgs():
		f = open("中出成熟的酒店经理[24P] - 1插菊花综合网.html", 'r')
		content = f.read()
		f.close()
		parser = Parser()
		print(parser.parseImgs(content))
		pass
	pass

main = Main()
main.start()
# Test.testGetNext()