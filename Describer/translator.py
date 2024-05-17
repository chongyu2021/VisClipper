import urllib
import urllib.parse
import hashlib
import random
import http
import http.client
import json


def baiduTranslate(translate_text, flag='en'):
    '''
    :param translate_text: 待翻译的句子，len(q)<2000
    :param flag: en:原句子翻译成英文；zh:原句子翻译成中文
    :return: 返回翻译结果。
    For example:
    q=我今天好开心啊！
    result = {'from': 'zh', 'to': 'en', 'trans_result': [{'src': '我今天好开心啊！', 'dst': "I'm so happy today!"}]}
    '''

    app_id = '20240427002036778'  # 填写你的appid
    secret_key = 'JrsHjcOM9QVE0m6iNveS'  # 填写你的密钥
    httpClient = None
    myurl = '/api/trans/vip/translate'  # 通用翻译API HTTP地址
    fromLang = 'auto'  # 原文语种

    if flag == 'en':
        toLang = 'en'  # 译文语种
    else:
        toLang = 'zh'  # 译文语种

    salt = random.randint(3276, 65536)

    sign = app_id + translate_text + str(salt) + secret_key
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + app_id + '&q=' + urllib.parse.quote(translate_text) + '&from=' + fromLang + \
            '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign

    # 建立会话，返回结果
    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)
        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)

        # return result
        return result['trans_result'][0]['dst']

    except Exception as e:
        print(e)
    finally:
        if httpClient:
            httpClient.close()


if __name__ == '__main__':
    # 手动录入翻译内容，q存放
    # q = raw_input("please input the word you want to translate:")
    # q = "介绍一下整本书，比如是传主的人生，或者作者写这本书的特色。可参看目录、序言或简介等资料。"
    q = "this is a english sentence."
    '''
    flag=zh 输入的句子翻译成中文
    flag=en 输入的句子翻译成英文
    '''
    result = baiduTranslate(q, flag='zh')  # 百度翻译
    print("原句:"+q)
    print(result)
