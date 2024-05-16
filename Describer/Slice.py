import os
import cv2
import time
import numpy as np
from skimage.metrics import structural_similarity


class Timer:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        start_time = time.time()
        result = self.func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {self.func.__name__} executed in {(end_time - start_time):.4f} seconds")
        return result


def save_slice(video_path, start_frame, end_frame, save_path):
    """
    将视频的指定帧范围保存为新视频片段
    用于测试裁切效果

    输入:
    - video_path (str): 视频文件路径
    - start_frame (int): 起始帧索引
    - end_frame (int): 结束帧索引
    - save_path (str): 新视频片段保存路径
    """
    # 读取视频文件
    video_capture = cv2.VideoCapture(video_path)
    # 设置起始帧
    video_capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    # 获取视频帧率和尺寸
    fps = int(video_capture.get(cv2.CAP_PROP_FPS))
    width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 创建用于写入新视频的VideoWriter对象
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(save_path, fourcc, fps, (width, height))

    # 读取指定范围内的每一帧并将其写入新视频
    for i in range(start_frame, end_frame):
        ret, frame = video_capture.read()
        if ret:
            out.write(frame)

    # 释放资源
    out.release()
    video_capture.release()


def ssim(frame1, frame2):
    """
    计算两帧之间的结构相似度（SSIM）

    输入:
    - frame1 (numpy.ndarray): 第一帧图像
    - frame2 (numpy.ndarray): 第二帧图像

    输出:
    - ssim_val (float): 结构相似度值
    """
    frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    # 这一段是为了加速 会降低效果
    frame1 = cv2.resize(frame1, (256, 256))
    frame2 = cv2.resize(frame2, (256, 256))

    return structural_similarity(frame1, frame2)


# def ssim(frame1, frame2):
#     """
#     计算两帧之间的结构相似度（SSIM）
#     自己实现的版本，比调库快10%左右
#
#     输入:
#     - frame1 (numpy.ndarray): 第一帧图像
#     - frame2 (numpy.ndarray): 第二帧图像
#
#     输出:
#     - ssim_val (float): 结构相似度值
#     """
#     C1 = (0.01 * 255) ** 2
#     C2 = (0.03 * 255) ** 2
#
#     # 将图像转换为float32类型
#     img1 = frame1.astype(np.float32)
#     img2 = frame2.astype(np.float32)
#
#     # 计算均值
#     mu1 = cv2.GaussianBlur(img1, (11, 11), 1.5)
#     mu2 = cv2.GaussianBlur(img2, (11, 11), 1.5)
#
#     # 计算方差和协方差
#     mu1_sq = mu1 ** 2
#     mu2_sq = mu2 ** 2
#     mu1_mu2 = mu1 * mu2
#
#     sigma1_sq = cv2.GaussianBlur(img1 ** 2, (11, 11), 1.5) - mu1_sq
#     sigma2_sq = cv2.GaussianBlur(img2 ** 2, (11, 11), 1.5) - mu2_sq
#     sigma12 = cv2.GaussianBlur(img1 * img2, (11, 11), 1.5) - mu1_mu2
#
#     # 计算SSIM
#     ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
#
#     # 计算平均SSIM
#     return np.mean(ssim_map)


@Timer
def slice_video(video_path, ssim_threshold=0.75, min_frames_per_slice=30):
    """
    将视频切分为多个片段

    输入:
    - video_path (str): 视频文件路径
    - ssim_threshold (float): 结构相似度阈值，默认为0.75
    - min_frames_per_slice (int): 每个片段的最小帧数，默认为30

    输出:
    - borders (list): 包含每个片段起始和结束帧索引的列表
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("无法打开视频文件")
        return

    start = 0
    end = 0
    borders = []

    while True:
        # 设置下一帧要读取的位置
        cap.set(cv2.CAP_PROP_POS_FRAMES, end)
        ret, prev = cap.read()

        # 如果已到达视频结尾，则跳出循环
        if not ret:
            # 如果当前帧在视频末尾且仍然符合条件，则将其作为最后一个片段的结束帧
            slice_start = start
            slice_end = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 使用视频帧总数作为结束帧
            # 检查片段是否足够长
            if slice_end - slice_start > min_frames_per_slice:
                borders.append((slice_start, slice_end))
            break

        # 设置下一帧要读取的位置
        cap.set(cv2.CAP_PROP_POS_FRAMES, end + 10)
        ret, current = cap.read()

        # 如果已到达视频结尾，则跳出循环
        if not ret:
            break

        # 计算prev和current之间的SSIM
        ssim_val = ssim(prev, current)
        if ssim_val > ssim_threshold:
            end += 10
        else:
            # 查找当前片段的结束位置
            slice_start = start
            slice_end = start
            frames = []
            cap.set(cv2.CAP_PROP_POS_FRAMES, end)

            for i in range(10):
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)

            for i in range(len(frames)-1):
                ssim_val = ssim(frames[i], frames[i+1])
                if ssim_val < ssim_threshold:
                    slice_end = end+i
                    start = end+i+1
                    end = end+i+1
                    break

            if slice_start != slice_end:
                # 检查片段是否足够长
                if slice_end - slice_start > min_frames_per_slice:
                    borders.append((slice_start, slice_end))
                    print(f"{slice_start} to {slice_end}")
            else:
                end += 10

    cap.release()
    return borders


if __name__ == '__main__':
    video_path = 'test_input/test.mp4'
    output_path = 'test_output/'
    borders = slice_video(video_path)

    for i,(start,end) in enumerate(borders):
        save_slice(video_path, start, end, os.path.join(output_path, str(i)+'.mp4'))

    """
    一个5584帧的片段，执行slice指令花费了838.0469秒
    使用resize可以使速度变快，(256,256)大小下可使速度缩短至200秒左右
    裁切效果偶尔有不完美的地方（10%左右）
    后续可以考虑的优化方式：改用C++实现，并行等
    """