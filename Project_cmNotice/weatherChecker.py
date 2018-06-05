__version__ = "0.0.2"
__log__ = """
0.0.1 创建模块，用以早上提醒下雨状态。
0.0.2 2018年3月16日 修复Bug，改进标点符号错误，添加详细下雨时间推送。
"""

import config
import json,requests

def checkWeather(metaitem=None):
    host = 'http://jisutqybmf.market.alicloudapi.com'
    path = '/weather/query'
    method = 'GET'
    appcode = config.data["model"]["weather"]["appcode"]
    querys = 'cityid=%s'%metaitem.info[0]
    bodys = {}
    url = host + path + '?' + querys

    headers = {"Authorization":"APPCODE %s"%appcode}
    r = requests.get(url,headers=headers)
    data = json.loads(r.text)
    if not "msg" in data or data["msg"] != "ok":
        raise TypeError("checkWeather: no Data")

    info = []
    raindict = {}
    for item in data["result"]["hourly"]:
        if item["time"] in ["6:00","7:00","8:00","9:00","10:00","11:00","12:00"]:
            noon = "上午"
        elif item["time"] in ["13:00","14:00","15:00","16:00","17:00","18:00"]:
            noon = "下午"
        elif item["time"] in ["19:00","20:00","21:00","22:00","23:00","24:00"]:
            noon = "晚上"

        if "雨" in item["weather"]:
            if not noon+"有雨" in info:
                if noon in raindict and str(raindict[noon]) > str(item["time"].split(":")[0]):
                    raindict[noon] = str(item["time"].split(":")[0])
                elif noon in raindict and str(raindict[noon]) <= str(item["time"].split(":")[0]):
                    pass
                elif not noon in raindict:
                    raindict[noon] = str(item["time"].split(":")[0])
                info.append("%s有雨"%noon)

    result = ""
    if info != []:
        for noon in ["上午","下午","晚上"]:
            if noon+"有雨" in info:
                result += "%s有雨，大概开始时间：%s点。"%(noon,raindict[noon])
        result = "今天天气不太好。" + result
        result = [result]
    else:
        result = [] 
    return [], result, 1


if __name__ == "__main__":
    print(checkWeather())