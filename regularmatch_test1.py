import re

f = open("sina_news.html", 'r')
content = f.read()
f.close()
# 将文本变成轮播图的部分
pattern = r'([.\s\S]*?)<section class="swiper-container">'
#res = re.match(pattern, content)
#print(res.group())
content = re.sub(pattern, '', content)
pattern = r'([\s\S]*?)</section>'
res = re.match(pattern, content)
content = res.group()

# 将轮播图列表化
pattern = r'href="([\s\S]*?)"'
hrefs = re.findall(pattern, content) # 链接
pattern = r'<em[\s\S]*?>([\s\S]*?)</em>'
titles = re.findall(pattern, content) # 标题
pattern = r'data-src="([\s\S]*?)"'
imgs = re.findall(pattern, content) # 题图

arr = []
size = len(titles)
for i in range(size):
	item = {
		"title" : titles[i],
		"href" : hrefs[i],
		"img" : imgs[i]
	}
	arr.append(item)
	pass

print(arr)