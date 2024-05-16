import os
import cv2
from Describer import *
from py_c_neo4j.Neo4j import *

# blip = BLIP(model_path='../BLIP_2')

class VideoImporter:
    def __init__(self,blip_model_path):
        self.blip = BLIP(model_path=blip_model_path)

    def import_video(self, video_path,tag=None):
        if os.path.isdir(video_path):
            self._import_videos_from_directory(video_path,tag)
        else:
            self._import_single_video(video_path,tag)

    def _import_videos_from_directory(self, directory, tag):
        video_files = [os.path.join(directory, file_name) for file_name in os.listdir(directory) if file_name.endswith(('.mp4', '.avi', '.mov'))]
        for video_file in video_files:
            self._import_single_video(video_file,tag)

    def _import_single_video(self, video_file, tag):
        try:
            # 检查视频文件属性
            video_capture = cv2.VideoCapture(video_file)
            frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_rate = int(video_capture.get(cv2.CAP_PROP_FPS))
            width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"Imported video: {video_file}, Frames: {frame_count}, FPS: {frame_rate}, Resolution: {width}x{height}")

            # 生成场景描述
            descriptions = describe_scenes(video_path=video_file, blip_model=self.blip)
            # 解析JSON数据
            descriptions_data = json.loads(descriptions)
            # 遍历键值对
            for key, value in descriptions_data.items():
                start_frame, end_frame = key.split("_")
                # ["tag", "name", "location", "start_frame", "end_frame", "description"]
                data = {}
                data['tag'] = tag
                data['name'] = os.path.splitext(os.path.basename(video_file))[0]
                data['location'] = os.path.dirname(video_file)
                data['start_frame'] = start_frame
                data['end_frame'] = end_frame
                data['description'] = value
                Insert_materials(json.dumps(data))

        except Exception as e:
            print(f"Error importing video {video_file}: {e}")

# vi = VideoImporter(blip_model_path='../BLIP_2')
# vi.import_video('../autodl-tmp/material/gjk/盗梦空间1.mp4')

class PromptProcessor:
    def __init__(self,topk=5):
        self.topk = topk

    def match(self,prompt,tag):
        materials = self._get_materials(tag)
        prompt = baiduTranslate(prompt, flag='en')
        similarities = []
        for material in materials:
            description = material['description']
            similarity = calculate_cosine_similarity(prompt, description)
            similarities.append((material, similarity))
        # 根据相似度降序排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        # 取出topk个相似度最高的字典
        topk_materials = [material for material, similarity in similarities[:self.topk]]
        return topk_materials

    def _get_materials(self,tag):
        if tag is None:
            return all_materials()
        else:
            return find_materials_by_tag(tag,BELONG_ANYTAG)

    def generate_output(self, prompt, tag):
        topk_materials = self.match(prompt, tag)
        output = ""
        for i, material in enumerate(topk_materials, 1):
            name = material.get("name", "Unknown")
            start_frame = material.get("start_frame", "Unknown")
            end_frame = material.get("end_frame", "Unknown")
            description = material.get("description", "No description")
            location = material.get("location", "Unknown")
            output += f"{i}.{name}的第{start_frame}帧到第{end_frame}帧，内容为{description}\n"
            output += f"  位置：{location}\n"
        return output

prompt = "一个帅气的男人"
tag = "盗梦空间"
processor = PromptProcessor(topk=5)
output = processor.generate_output(prompt, tag)
print(output)