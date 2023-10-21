import requests
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
import re
from tqdm import tqdm

'''
    适用于古诗文网的全书书籍译文爬虫
    第一步：ShuJiurl = "这里替换为你想要采集的书籍的网址"
    最终会生成一个文件名为"书籍名.txt"的文件，内容为所有章节原文和译文的合集，每一章之间以"章节名：……"隔断
    原创：Xiangrui Kong，修改请引用
'''

# ShuJiurl = "https://so.gushiwen.cn/guwen/book_46653FD803893E4F699E8628DEAEE3C0.aspx" # 在这里替换方才有效
ShuJiurl = "https://so.gushiwen.cn/guwen/book_46653FD803893E4F9B29D6AEC1BFD4EA.aspx" # 在这里替换方才有效

# ShuJiurl = 'https://so.gushiwen.cn/guwen/book_46653FD803893E4F9B29D6AEC1BFD4EA.aspx'
# 第一大步：通过目录页，获取每一章的url
# 加载目录页，变成一个pyquery对象
def get_urls(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15'
    }
    response = requests.get(url, headers=headers)
    soup = pq(response.text)
    return soup
# 用pq获取每一章的链接、名称和id，以及用于文件名的书名
def detail_url(soup):
    LINKS, NAMES, IDS = [], [], []
    links = soup('div.sons div a') # 通过pq，搜索div为sons的所有层级的子节点，获得所有名称为a
    bookname = soup('#sonsyuanwen > div.cont > h1 > span:nth-child(1) > b').text()
    for link in links:
        url = link.attrib['href']
        name = link.text_content()
        cid = re.search(r'book(?:v_)?([A-F0-9]+)\.aspx', url).group(1)
        LINKS.append(url)
        NAMES.append(name)
        IDS.append(cid)
    return LINKS, NAMES, IDS, bookname


# 基于id，装载为带着译文的网页的url
# 这里隐去的步骤是获得包含段译的url，这是通过分析ajax得到的
def pinzhuang(cid):
    DETAIL_URL = 'https://so.gushiwen.cn/guwen/ajaxbfanyiYuanchuang.aspx?id={id}&state=duanyi'
    url = DETAIL_URL.format(id=cid)
    return url


# 从每一个带译文的页，获取文本
def text_get(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    # 找到所有的文本内容
    text_content = []
    for p_tag in soup.find_all('p'):
        text = p_tag.get_text(separator='\n', strip=True)  # 使用'\n'作为不同行的分隔符
        text_content.append(text)
    # 将所有文本内容合并为一个字符串，每个段落之间用两个换行符分隔
    result_text = '\n\n'.join(text_content)
    return result_text

# 主程序：把各模块拼装到一起
def main(url):
    soup = get_urls(ShuJiurl)
    LINKS, NAMES, IDS ,bookname = detail_url(soup)
    allnum = len(LINKS)
    with open(f'{bookname}.txt', 'w', encoding='utf-8') as file:  # 打开文件以写入，指定编码为utf-8
        for i in tqdm(range(0, allnum), desc='Processing chapters'):  # 使用tqdm包装range对象
            id = IDS[i]
            suburl = pinzhuang(id)
            text = text_get(suburl)
            file.write(f'章节名: {NAMES[i]}\n')  # 写入章节名
            file.write(text + '\n\n')  # 写入文本，并在每章之间添加两个换行符作为分隔

if __name__ == '__main__':
    main(ShuJiurl)



# 如果不用tqdm，手动做一个类似的进度条的话，可以这样
# def main(url):
#     soup = get_urls(ShuJiurl)
#     LINKS, NAMES, IDS = detail_url(soup)
#     allnum = len(LINKS)
#     with open(f'{bookname}.txt', 'w', encoding='utf-8') as file:  # 打开文件以写入，指定编码为utf-8
#         for i in range(0, allnum):
#             id = IDS[i]
#             suburl = pinzhuang(id)
#             text = text_get(suburl)
#             file.write(f'Chapter: {NAMES[i]}\n')  # 写入章节名
#             file.write(text + '\n\n')  # 写入文本，并在每章之间添加两个换行符作为分隔
#             print(f'Processed chapter {i + 1}/{allnum}: {NAMES[i]}')  # 输出进度信息
