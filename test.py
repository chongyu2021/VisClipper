import os
import cv2
from Describer import *
from py_c_neo4j.Neo4j import *

if __name__ == '__main__':
    # 实例化 BLIP 模型
    blip_model = BLIP(model_path=r"../BLIP_2")

    # 定义视频路径
    video_path = r'../autodl-tmp/material/gjk/盗梦空间1.mp4'

    # 生成场景描述
    descriptions = describe_scenes(video_path=video_path, blip_model=blip_model)

    # 定义保存 JSON 文件的路径
    json_file_path = 'scene_descriptions.json'

    # 将描述保存到 JSON 文件中
    with open(json_file_path, 'w') as json_file:
        json.dump(descriptions, json_file, indent=4, ensure_ascii=False)

    print(f"场景描述已保存至 {json_file_path}")