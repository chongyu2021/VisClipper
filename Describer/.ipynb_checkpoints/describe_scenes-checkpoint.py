import cv2
import json
from PIL import Image
from Slice import slice_video
from BLIP import BLIP


def extract_frame(video_path, frame_index):
    """
    从视频中提取指定索引的帧。

    参数：
    - video_path (str): 视频文件路径。
    - frame_index (int): 要提取的帧的索引。

    返回：
    - frame (numpy.ndarray): 提取的帧。
    """
    # 打开视频文件
    cap = cv2.VideoCapture(video_path)

    # 设置帧位置
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)

    # 读取帧
    ret, frame = cap.read()

    # 释放视频捕获对象
    cap.release()

    return frame


def describe_scenes(video_path, blip_model, ssim_threshold=0.75, min_frames_per_slice=30):
    """
    为视频中的每个场景生成描述，并将它们存储在字典中。

    参数：
    - video_path (str): 视频文件路径。
    - blip_model (BLIP): 已经加载好的BLIP模型
    - ssim_threshold (float): 场景检测的SSIM阈值。
    - min_frames_per_slice (int): 每个场景的最小帧数。

    返回：
    - scene_descriptions (dict): 包含场景描述的字典，键为元组 (start_index, end_index)。
    """
    # 对视频进行切割以检测场景
    scenes = slice_video(video_path, ssim_threshold=ssim_threshold, min_frames_per_slice=min_frames_per_slice)

    # 初始化一个空字典来存储场景描述
    scene_descriptions = {}

    # 处理每个场景
    for start_index, end_index in scenes:
        # 确定中间帧的索引
        midpoint_index = (start_index + end_index) // 2

        # 获取中间索引处的帧
        frame = extract_frame(video_path, midpoint_index)

        # 为帧生成描述
        description = blip_model.generate_text(Image.fromarray(frame))  # 将帧转换为PIL Image

        # 将键转换为字符串类型并存储描述
        key = f"{start_index}_{end_index}"
        scene_descriptions[key] = description

    # 将字典转换为JSON字符串
    scene_descriptions_json = json.dumps(scene_descriptions)

    return scene_descriptions_json


if __name__ == '__main__':
    # 实例化 BLIP 模型
    blip_model = BLIP(model_path=r"D:\Models\BLIP")

    # 定义视频路径
    video_path = r'test_input/test.mp4'

    # 生成场景描述
    descriptions = describe_scenes(video_path=video_path, blip_model=blip_model)

    # 定义保存 JSON 文件的路径
    json_file_path = 'scene_descriptions.json'

    # 将描述保存到 JSON 文件中
    with open(json_file_path, 'w') as json_file:
        json.dump(descriptions, json_file, indent=4, ensure_ascii=False)

    print(f"场景描述已保存至 {json_file_path}")
