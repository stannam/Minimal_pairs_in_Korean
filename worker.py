from os import path
import pandas as pd

CORPUS = pd.read_csv(path.join('assets', 'kor_raw2.csv'))
# 강범모 김흥규에서 표준국어대사전 발음형으로 보정한 db

def clean_seg_pair(pair):
    # returns a list of clean segments. For example, str: "(p, t)" to list: ["p","t"]
    segs = pair.split(',')
    return [s.strip() for s in segs]


def update_pair(pair, new_seg):
    # update minimal pair. used when user selects a segment from the inventory
    if '(' in pair:  # first selecting a segment
        return new_seg
    segs = clean_seg_pair(pair)

    if new_seg in segs:
        return pair

    pair = segs[-1], new_seg
    return ', '.join(pair)


def filter_corpus(pair, filters, corpus=CORPUS):
    filter_pos = filters['pos']
    filter_freq = filters['freq']
    filter_etymology = filters['etymology']

    pair = clean_seg_pair(pair)
    for_reg = f'[{"".join(pair)}]'

    to_analyze = corpus[corpus['ipa'].str.contains(for_reg)]  # only consider words that contain target segs
    to_analyze = to_analyze[to_analyze['abs_freq'] >= filter_freq]  # filter by frequency

    # filter by etymology (optional)
    to_analyze = corpus[corpus['ipa'].str.contains(for_reg)]


    # remove duplicates
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
    pair = clean_seg_pair(pair)

    result = list()

    neutralized_dict = {pair[0]: neutralize(corpus, pair[0]),
                        pair[1]: neutralize(corpus, pair[1])}

    mp_skeletons = list(neutralized_dict[pair[0]].keys() & neutralized_dict[pair[1]].keys())
    for mp_type in mp_skeletons:
        result.append((neutralized_dict[pair[0]][mp_type], neutralized_dict[pair[1]][mp_type]))

    return result


def batch_btn_operation(btn_options, option_disabled):
    pass
    values = [option['value'] for option in btn_options]
    for option in btn_options:
        option['disabled'] = option_disabled
    if option_disabled:
        values = []
    return values, btn_options







if __name__ == "__main__":
    batch_btn_operation([
            {"label": "Common nouns (일반명사)", "value": 'NNG'},
            {"label": "Proper nouns (고유명사)", "value": 'NNP'},
            {"label": "Counting words (수사)", "value": 'NR'},
            {"label": "Pronouns (대명사)", "value": 'NP'},
            {"label": "Bound nouns (의존명사)", "value": 'NNB'},
        ],True)
    pass
