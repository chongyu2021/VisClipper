from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_cosine_similarity(text1, text2):
    """
    计算两个文本之间的余弦相似度

    参数:
    text1 (str): 第一个文本
    text2 (str): 第二个文本

    返回:
    float: 两个文本之间的余弦相似度
    """
    # 使用CountVectorizer将文本转换为词袋向量
    vectorizer = CountVectorizer().fit_transform([text1, text2])

    # 计算余弦相似度
    cosine_sim = cosine_similarity(vectorizer)

    # 返回相似度
    return cosine_sim[0][1]


if __name__ == '__main__':
    # 测试函数
    text1 = "Python is a great programming language"
    text2 = "Programming in Python is awesome"
    similarity = calculate_cosine_similarity(text1, text2)
    print("Cosine Similarity:", similarity)
