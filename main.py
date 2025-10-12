import pandas as pd
import numpy as np
import random
from gensim.models import Word2Vec
import json

# scikit-learn 데이터 사주

# 데이터 생성을 위한 기본 요소 정의
num_samples = 1000  # 생성할 데이터 샘플 수

with open("./data_stars.json", 'r') as f:
    data = json.load(f)

print(data)
