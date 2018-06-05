__version__ = "0.0.2"
__log__ = """
0.0.1 2018年3月22日 创建模块。
0.0.2 健壮程序。
"""

import config
import requests
from datetime import date
from lxml import etree

def checkTugua(metaitem=None):
    headers = {
    "Accept-Encoding":"gzip, deflate",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
    "Accept-Language":"zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Content-Type":"text/html;charset=utf-8"}
    r = requests.get("http://www.dapenti.com/blog/index.asp",headers = headers)
    r.encoding='gb2312'
    if r.status_code != 200:
        raise BufferError("解析页面失败")
    selector = etree.HTML(r.text)
    title = selector.xpath('//*[@id="center"]/table[1]/tbody/tr[2]/td[1]/div/ul/li/a')
    if title:
        for x in title:
            if "喷嚏图卦" + date.today().isoformat().replace("-","") in x.text:
                result = x.get("title")
                notice = result + " " +"http://www.dapenti.com/blog/" + x.get("href")
                if not result in metaitem.data:
                    return [result],[notice],1
                else:
                    return [],[],1    
    return [],[],1

if __name__ == "__main__":
    r = checkTugua()
    print(r)