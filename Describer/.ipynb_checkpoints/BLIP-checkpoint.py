import torch
from transformers import Blip2Processor, Blip2ForConditionalGeneration


class BLIP:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model_path):
        """
        初始化BLIP类的实例

        参数：
        - model_path (str): 模型路径，用于载入BLIP模型

        返回：
        无返回值
        """
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.processor = Blip2Processor.from_pretrained(model_path)  # 载入BLIP模型的处理器
            self.model = Blip2ForConditionalGeneration.from_pretrained(model_path)  # 载入BLIP模型
            self.device = "cuda" if torch.cuda.is_available() else "cpu"  # 设置运行设备为GPU或CPU
            self.model.to(self.device)  # 将模型移动到指定设备上

    def generate_text(self, image, prompt="This is a photo of", max_length=50):
        """
        使用BLIP模型生成文本描述

        参数：
        - image (PIL.Image.Image): 输入图像，用于生成文本描述
        - prompt (str): 提示文本，指导文本生成过程。默认为"This is a photo of"

        返回：
        - generated_text (str): 生成的文本描述
        """
        try:
            inputs = self.processor(images=image, text=prompt, return_tensors="pt").to(self.device)  # 将图像转换为模型输入格式
            generated_ids = self.model.generate(**inputs, max_length=max_length)  # 使用模型生成文本
            generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()  # 解码生成的文本

            return generated_text  # 返回生成的文本描述
        except Exception as e:
            print(f"Error during text generation: {e}")  # 打印异常信息
            return None  # 返回空值表示文本生成失败
