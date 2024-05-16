import uuid
import time
import requests
from Blue_LM.auth_util import gen_sign_headers
import pandas as pd
import numpy as np

# 请替换APP_ID、APP_KEY
APP_ID = '3036418502'
APP_KEY = 'RuNbjtwaoSbEdWhf'
URI = '/vivogpt/completions'
DOMAIN = 'api-ai.vivo.com.cn'
METHOD = 'POST'



def sync_vivogpt(single_prompt):
    history_path = "historical_QA.csv"
    history_data = pd.read_csv(history_path)
    history_data = np.array(history_data.iloc[: , :])
    # single_prompt = '一个女人牵着狗在公园散步'
    query = []
    for i in range(len(history_data)):
        user_dict = {}
        user_dict["role"] = "user" 
        user_dict["content"] = history_data[i][0]
        assistant_dict = {}
        assistant_dict["role"] = "assistant" 
        assistant_dict["content"] = history_data[i][1]
        query.append(user_dict)
        query.append(assistant_dict)
    
    user_dict = {}
    user_dict["role"] = "user" 
    user_dict["content"] = single_prompt
    query.append(user_dict)
    params = {
        'requestId': str(uuid.uuid4())
    }
    print('requestId:', params['requestId'])

    data = {
        'messages': query,
        'model': 'vivo-BlueLM-TB',
        'sessionId': str(uuid.uuid4()),
        'extra': {
            'temperature': 0.9
        }
    }
    headers = gen_sign_headers(APP_ID, APP_KEY, METHOD, URI, params)
    headers['Content-Type'] = 'application/json'

    start_time = time.time()
    url = 'https://{}{}'.format(DOMAIN, URI)
    response = requests.post(url, json=data, headers=headers, params=params)

    if response.status_code == 200:
        res_obj = response.json()
        print(f'response:{res_obj}')
        if res_obj['code'] == 0 and res_obj.get('data'):
            content = res_obj['data']['content']
            print(f'final content:\n{content}')
    else:
        print(response.status_code, response.text)
    end_time = time.time()
    timecost = end_time - start_time
    print('请求耗时: %.2f秒' % timecost)
    return content


if __name__ == '__main__':
    prompt = '一个女人牵着狗在公园散步'
    sync_vivogpt(prompt)