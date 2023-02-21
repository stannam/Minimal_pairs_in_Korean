import pandas as pd
from os import path

# standard.tsv = 표준국어대사전 발음형 및 어원 dump 통합 2018-11-22 (옛한글 들어간 부분 제거해야 함)
standard = pd.read_csv(path.join('assets', 'standard.tsv'), sep='\t')
old_hangul_regex = '(?![가-힣]|[ㄱ-ㅎ]).'
filter = standard['raw.entry'].str.contains(old_hangul_regex) # raw.entry에 옛한글이 포함되어 있으면 True, 아니면 False
standard = standard[~filter]  # remove 'Old_Korean = True' rows


# kor_raw.csv = 강범모 김흥규 리스트
# 절대빈도 20 이상, 단 고유명사는 1000 이상
# 포함된 품사: 부사 (M), 독립언(IC), 일반명사(NNG), 대명사(NP) + 각종 명사

kor_raw = pd.read_csv(path.join('assets', 'kor_raw.csv'), sep=',')

# iterate over kor_raw and test each pronunciation
for i in range(len(kor_raw)):
    kor_raw.loc[i, ]

