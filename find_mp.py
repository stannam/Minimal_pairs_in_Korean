from os import path
import pandas as pd

CORPUS = pd.read_csv(path.join('assets', 'kor_raw.csv'))
# 절대빈도 20 이상, 단 고유명사는 1000 이상
# 포함된 품사: 부사 (M), 독립언(IC), 명사(N), 대명사(NP)

def filter_corpus(pair, filters, corpus=CORPUS):
    # filter_pos = filters['pos']
    filter_freq = filters['freq']

    pair = pair.split(',')
    pair = [p.strip() for p in pair]
    for_reg = f'[{"".join(pair)}]'

    to_analyze = corpus[corpus['ipa'].str.contains(for_reg)]
    to_analyze = to_analyze[to_analyze['abs_freq'] >= filter_freq]
    to_analyze = to_analyze.drop_duplicates(subset="ipa")

    return to_analyze


def neutralize(corpus, seg):
    res_dict = dict()
    for index, row in corpus.iterrows():
        sep = row['ipa'].split(' ')
        if seg not in sep:
            continue
        for i in range(len(sep)):
            if sep[i] == seg:
                neutralized_form = ''.join([sep[j] if j != i else '#' for j in range(len(sep))])
                res_dict[neutralized_form] = (row.hangul, row.ipa)

    return res_dict


def list_mp(pair, filters, corpus=CORPUS):
    corpus = filter_corpus(pair=pair, filters=filters)
    pair = pair.split(',')
    pair = [p.strip() for p in pair]

    result = list()

    neutralized_dict = {pair[0]: neutralize(corpus, pair[0]),
                        pair[1]: neutralize(corpus, pair[1])}

    mp_skeletons = list(neutralized_dict[pair[0]].keys() & neutralized_dict[pair[1]].keys())
    for mp_type in mp_skeletons:
        result.append((neutralized_dict[pair[0]][mp_type], neutralized_dict[pair[1]][mp_type]))

    return result

if __name__ == "__main__":
    fil = {'freq': 1}
    list_mp(pair='p, k', filters=fil)
