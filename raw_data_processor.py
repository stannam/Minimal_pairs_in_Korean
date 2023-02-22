import pandas as pd
import re
from os import path

# The idea is that the freqeuncy lexicon (KANG & KIM 2009) should be the base
# and refer to STANDARD KOREAN DICTIONARY for (irregular) pronunciations and etymology

def get_pronunciation(row):
    # function that retrieve irregular pronunciation information from
    # Standard Korean Dictionary
    p = row['pronounce'].values[0]
    if pd.isnull(p):
        return ''  # if nan then ''
    p = re.sub('/.*', '', p)  # remove alternative pronunciations. e.g., '-회/-훼' ==> '-회'

    if '-' in p:
        orth = row['raw.entry'].values[0]  # pronunciations in Standard contain '-' for transparent syllables
        matches = re.finditer('-', p)      # therefore, I inherit orthographic form as the syllable pronunciation
        orth = list(orth)
        p = list(p)

        for match in matches:
            dash_loc = match.start()
            p[dash_loc] = orth[dash_loc]

        p = ''.join(p)

    return p


def get_etymology(row):
    # function that retrieve etymology information from
    # Standard Korean Dictionary
    # return either 'native', 'foreign' or 'sino'
    ety_list = ['sino', 'native', 'foreign']
    ety_info = [row['sino'].values[0],
                row['native'].values[0],
                row['foreign'].values[0]]
    try:
        etymology = ety_list[ety_info.index(1)]
    except ValueError:
        etymology = 'Unknown'

    return etymology


def find_info(term, db):
    # find the term in DB(i.e., Standard Korean Dictionary) and return pronunciation and etymology.
    row_in_db = db.loc[db['ID'] == term]  # find search entry in Standard

    if len(row_in_db) < 1:
        if "_" not in term:
            # Kang and Kim (2009) takes a lazy approach where '__01' is dropped if
            # it does not disambiguate.
            term_with_index = term + "__01"
            row_in_db = db.loc[db['ID'] == term_with_index]  # find search entry + __01 in Standard

    if len(row_in_db) < 1:
        # if still has no hit, then return nothing
        return "", ""

    pronunciation = get_pronunciation(row_in_db)

    etymology = get_etymology(row_in_db)

    return pronunciation, etymology


def clean_load_standard(assets_dir, standard_filepath, sep="\t"):
    # function that loads Standard Korean Dictionary and removes old_korean entries
    file = pd.read_csv(path.join(assets_dir, standard_filepath), sep=sep)
    old_hangul_regex = '(?![가-힣]|[ㄱ-ㅎ]).'
    filter = file['raw.entry'].str.contains(old_hangul_regex)  # raw.entry에 옛한글이 포함되어 있으면 True, 아니면 False
    file = file[~filter]  # remove 'Old_Korean = True' rows
    return file


def main(reference_db, kor_raw):
    # add placeholders for retrieved (irregular) pronunciations and etymology
    kor_raw["pron"] = ""
    kor_raw["etymology"] = ""
    for i in range(len(kor_raw)):
        search_entry = kor_raw.loc[i, "indexed"]  # entry form to search in Standard
        POS_entry = kor_raw.loc[i, "POS"]

        if POS_entry == "NNP":
            # do not find Standard pronunciation / etymology for proper nouns
            continue

        pronunciation, etymology = find_info(term=search_entry, db=reference_db)

        kor_raw.loc[i, "pron"] = pronunciation
        kor_raw.loc[i, "etymology"] = etymology

    return kor_raw

if __name__ == "__main__":
    # standard.tsv = 표준국어대사전 발음형 및 어원 dump 통합 2018-11-22 (옛한글 들어간 부분 제거해야 함)
    standard = clean_load_standard(assets_dir="assets", standard_filepath="standard.tsv")

    # kor_raw.csv = 강범모 김흥규 wordlist
    # 절대빈도 20 이상, 단 고유명사는 1000 이상
    # 포함된 품사: 부사 (M), 독립언(IC), 일반명사(NNG), 대명사(NP) + 각종 명사
    kor_raw = pd.read_csv(path.join('assets', 'kor_raw.csv'), sep=',')

    kor_raw = main(standard, kor_raw)
    kor_raw.to_csv(path.join('assets', 'kor_raw_plus.csv'), index=False)
