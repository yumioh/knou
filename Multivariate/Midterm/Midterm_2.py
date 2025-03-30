import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#from spicy.stats import t

#2. 자유도가 5인 t분포를 따르는 난수 1000개를 만들어 분석.
#1) 난수를 생성하라
rng = np.random.RandomState(32) # 난수 생성시 동일한 난수 시퀸스 생성을 위함
random_t_values = rng.standard_t(df= 5,size=1000)

#2) 히스토그램을 그리고 설명하라 
df = pd.DataFrame(random_t_values, columns=['T_values'])
# 3) x축 범위 지정
#df.hist(bins=30, color="skyblue")
#plt.title("Histogram of Random T Values")
#plt.xlabel("Values")
#plt.ylabel("Frequency")
#plt.show()


#3) 상자그림을 그리고 설명하라 

# 분위수 계산
q1 = np.percentile(random_t_values, 25)
q2 = np.percentile(random_t_values, 50)  # 중간값
q3 = np.percentile(random_t_values, 75)


# 분위수 값 넣기
# plt.text(1.3, q1, f"Q1: {q1:.2f}", ha='center', color='red')
# plt.text(1.3, q2, f"Q2: {q2:.2f}", ha='center', color='red')
# plt.text(1.3, q3, f"Q3: {q3:.2f}", ha='center', color='red')
# plt.boxplot(random_t_values)
# plt.title("Boxplot of Random T Values")
# plt.grid(True)
# plt.show()


#4 ) 줄기잎그림을 그리고 설명하라
import stemgraphic
stemgraphic.stem_graphic(df['T_values'])
plt.title("Stem of Random T Values")
plt.show()

