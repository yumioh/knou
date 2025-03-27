import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

med = pd.read_csv("D:\knou\Multivariate\data\medFactor.csv")
#print(med)

# 요약 통계량
print(med.describe())