# -*- coding: utf-8 -*-
import os
import re
import sys
import math
import logging
import string
import random
import json
from collections import defaultdict, Counter
from functools import lru_cache
from shove import Shove

import jinja2


sys.path.append(os.getcwd())
from constants import *

def load_abbr(abbr_file=ABBREVIATION_FILE):
    """
    Load the abbr2long from file
    """
    abbr2long = dict()
    with open(abbr_file) as f:
        lines = f.read().split('\n')
        for line in lines:
            m = re.match(r'(\w+)\t(.+)', line)
            if m:
                abbr2long[m.group(1)] = m.group(2)
    return abbr2long


def load_spelling(spell_file=SPELLING_FILE):
    """
    Load the term_freq from spell_file
    """
    with open(spell_file) as f:
        tokens = f.read().split('\n')
        size = len(tokens)
        term_freq = {token: size - i for i, token in enumerate(tokens)}
    return term_freq


def load_search_freq(fp=SEARCH_FREQ_JSON):
    """
    Load the search_freq from JSON file
    """
    try:
        with open(fp) as f:
            return Counter(json.load(f))
    except FileNotFoundError:
        return Counter()


# Load abbreviation.txt
abbr2long = load_abbr(abbr_file=ABBREVIATION_FILE)

# Load search_freq
search_freq = load_search_freq(SEARCH_FREQ_JSON)

def gen_path(base, code):
    """
    Generate a path for give base path and code used in data generation
    """
    #return os.path.join(base, code[:2], code[:3])
    return base


def clean(s):
    output = re.sub(r'without .*?(,|$)', '', s)
    return output


def tokenize(s):
    """
    A simple tokneizer
    """
    s = re.sub(r'(?a)(\w+)\'s', r'\1', s) # clean the 's from Crohn's disease
    #s = re.sub(r'(?a)\b', ' ', s) # split the borders of chinese and english chars

    split_pattern = r'[{} ]+'.format(re.escape(STOPCHARS))
    tokens = [token for token in re.split(split_pattern, s) if not set(token) <= set(string.punctuation)]
    tokens.extend([unit for tk in tokens if '-' in tk for unit in tk.split('-')])
    return tokens


def lemmatize(tokens):
    """
    A simple lemmatizer
    """
    return [token.lower() for token in tokens]


def filterout(tokens, stopwords=STOPWORDS):
    """
    Filter removes stopwords
    """
    return [token for token in tokens if token not in stopwords]


def invert_index(source_dir, index_url=INDEX_URL, init=False):
    """
    Build the invert index from give source_dir
    Output a Shove object built on the store_path
    Input:
        source_dir: a directory on the filesystem
        index_url: the store_path for the Shove object
        init: clear the old index and rebuild from scratch
    Output:
        index: a Shove object
    """
    raw_index = defaultdict(list)
    for base, dir_list, fn_list in os.walk(source_dir):
        for fn in fn_list:
            fp = os.path.join(base, fn)
            code = fn
            with open(fp) as f:
                try:
                    tokens = f.read().strip().split('\n')
                except:
                    print(fp)
                    continue
                for token in tokens:
                    raw_index[token].append(code)
    index = Shove(store=index_url)
    if init:
        index.clear()
    if '' in raw_index:
        del raw_index['']
    index.update(raw_index)
    index.sync()
    return index


def write_spelling(token_folder, spelling_file):
    """
    Generate the spelling correction file form token_folder and save to spelling_file
    """
    tokens = []
    for base, dirlist, fnlist in os.walk(token_folder):
        for fn in fnlist:
            fp = os.path.join(base, fn)
            with open(fp) as f:
                tokens.extend(f.read().split('\n'))

    token_ranked, _ = zip(*Counter(tokens).most_common())
    with open(spelling_file, 'w') as f:
        f.write('\n'.join(token_ranked))


def get_hints(code_list, k=10, hint_folder=HINT_FOLDER, current_tokens=None):
    """
    Fetch first k hints for given code_list
    """

    def hint_score(v, size):
        """
        The formula for hint score
        """
        if v == size or v == 0:
            return 0
        return 1.0 - abs(v / (size + 1) - 0.5)

    if len(code_list) <= 1:
        return [], []

    if current_tokens is None:
        current_tokens = []

    size = min(len(code_list), MAX_HINT_SMAPLING_SIZE)
    sample = random.sample(code_list, size)
    hint_list = []
    capital_dict = {}

    for code in sample:
        path = gen_path(hint_folder, code)
        fp = os.path.join(path, code)
        try:
            with open(fp) as f:
                hints = set(f.read().strip().split('\n'))
                hint_list.extend([h.lower() for h in hints])
                capital_dict.update({hint.lower(): hint for hint in hints})
        except FileNotFoundError:
            logging.warning("FileNotFoundError: No such file: %r" % fp )
    document_freq = Counter(hint_list)
    score = []
    for k_, v in document_freq.items():
        _score = hint_score(v, size)
        if k_ not in current_tokens and _score > 0:
            score.append((capital_dict[k_], _score))

    if len(score) == 0:
        return [], []
    score.sort(key=lambda x: x[1], reverse=True)

    hints, scores = tuple(list(zip(*score[:k])))
    return hints, scores

def fetch(index, tokens):
    """
    Fetch the codes from given tokens
    """
    if len(tokens) == 0:
        return set()
    return set.intersection(*[set(index.get(token, [])) for token in tokens])

@lru_cache(maxsize=65536)
def _get_snippet(code, base):
    path = gen_path(base, code)
    fp = os.path.join(path, code)
    try:
        with open(fp) as f:
            return f.read()
    except FileNotFoundError:
        output.append('')
        logging.warning("FileNotFoundError: No such file: %r" % fp )
        return ''


def get_snippets(code_list, base=SNIPPET_FOLDER):
    """
    Get the snippets
    """
    output = [_get_snippet(code, base) for code in code_list]
    return output


def abbr_expand(tokens):
    log = []
    output = []
    for token in tokens:
        if token in abbr2long:
            long = abbr2long[token]
            log.append((token, long))
            output.extend(tokenize(long))
        else:
            output.append(token)
    return output, log


def _ed1(token):
    """
    Return tokens the edit distance of which is one from the given token
    """
    insertion = {letter.join([token[:i], token[i:]]) for letter in string.ascii_lowercase for i in range(1, len(token) + 1)}
    deletion = {''.join([token[:i], token[i+1:]]) for i in range(1, len(token) + 1)}
    substitution = {letter.join([token[:i], token[i+1:]]) for letter in string.ascii_lowercase for i in range(1, len(token) + 1)}
    transposition = {''.join([token[:i], token[i+1:i+2],  token[i:i+1], token[i+2:]]) for i in range(1, len(token)-1)}
    return set.union(insertion, deletion, substitution, transposition)


def _ed2(token):
    """
    Return tokens the edit distance of which is two from the given token
    """
    return {e2 for e1 in _ed1(token) for e2 in _ed1(e1)}


def _correct(token, term_freq):
    """
    Correct a single token according to the term_freq
    """
    if token.lower() in term_freq:
        return token
    e1 = [t for t in _ed1(token) if t in term_freq]
    if len(e1) > 0:
        e1.sort(key=term_freq.get)
        return e1[0]
    e2 = [t for t in _ed2(token) if t in term_freq]
    if len(e2) > 0:
        e2.sort(key=term_freq.get)
        return e2[0]
    return token


def correct(tokens, term_freq):
    """
    Correct a list of tokens, according to the term_freq
    """
    log = []
    output = []
    for token in tokens:
        corrected = _correct(token, term_freq)
        if corrected != token:
            log.append((token, corrected))
        output.append(corrected)
    return output, log


def result_sort_key(tokens):
    """
    The sort key function for the search results
    Input:
        response_item: the tuple of (code, snippet)
    output:
        sortable value, the greatest first
    """
    def similarity(tokens, snippet):
        target_tokens = lemmatize(tokenize(jinja2.filters.do_striptags(snippet)))
        jaccard = len(set(tokens) & set(target_tokens)) / len(set(tokens) | set(target_tokens))
        return jaccard

    def raw_result_sort_key(response_item):
        code, snippet = response_item

        snippet_length = len(snippet)
        freq = search_freq.get(code, 0)
        beta = 0.05
        score = similarity(tokens, snippet)\
                - math.log(len(code))\
                - math.log(snippet_length)\
                + math.log(freq * beta + 1)

        return score


def search(index, query, term_freq,
        snippet_folder=SNIPPET_FOLDER,
        hint_folder=HINT_FOLDER):
    """
    The highest level of search function
    """

    fallback_log = []
    code_list = []
    tokens = lemmatize(tokenize(query))
    tokens, abbr_log = abbr_expand(tokens)
    tokens, correct_log = correct(tokens, term_freq)
    tokens = lemmatize(tokens)
    tokens = filterout(tokens)
    while len(tokens) > 0: # Fallback mechanism
        code_list = fetch(index, tokens)
        if len(code_list) > 0:
            break
        tokens.sort(key=lambda tk:len(index.get(tk, [])))
        remove = tokens.pop()
        fallback_log.append(remove)
    snippets = get_snippets(code_list, snippet_folder)
    hints, hint_scores = get_hints(code_list, hint_folder=hint_folder, current_tokens=tokens)
    response = list(zip(code_list, snippets))
    response.sort(key=result_sort_key(tokens), reverse=True)

    # Count search_frequency
    if len(response) <= MAX_RESULT: # the respone can be shown in one page
        search_freq.update(code_list)
        with open(SEARCH_FREQ_JSON, 'w') as f:
            json.dump(search_freq, f, indent=2)

    return response, tokens, hints, hint_scores, \
           abbr_log, correct_log, fallback_log


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="`newindex` or `updateindex`")
    args = parser.parse_args()
    if args.action == 'newindex':
        init = True
        index = invert_index(TOKEN_FOLDER, INDEX_URL, init=init)
        write_spelling(TOKEN_FOLDER, SPELLING_FILE)
    elif args.action == 'updateindex':
        init = False
        index = invert_index(TOKEN_FOLDER, INDEX_URL, init=init)
        write_spelling(TOKEN_FOLDER, SPELLING_FILE)

if __name__ == '__main__':
    main()
