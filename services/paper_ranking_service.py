from datetime import datetime
import difflib
# import logging
from itertools import chain
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

import logging
import csv

logger = logging.getLogger("paper_ranking_service")
lemmatizer = WordNetLemmatizer()


def read_the_journal_for_ranking():
    with open('scimagojr 2019.csv', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        dic_for_srj = {}

        for row in reader:
            journal_issn = row['Issn']
            srj_rank = row['SJR']

            if srj_rank == '':
                srj_rank = None
                dic_for_srj[journal_issn] = srj_rank
            else:
                srj_rank = float(srj_rank.replace(',', '.'))
                dic_for_srj[journal_issn] = srj_rank

        return dic_for_srj


dict = read_the_journal_for_ranking()

# Get lemma words
# Transform to 1-dimensional list
# Replaces '-' and '_' by ' '
# Lowercase
def _preprocess_words(words):
    logger.info('_preprocess_words | {}'.format(words))
    synsets = [[ss.lemma_names() for ss in wn.synsets(word)] for word in words]
    words = words + list(set(chain.from_iterable(chain.from_iterable(synsets))))
    words = [word.replace('-', ' ') for word in words]
    words = [word.replace('_', ' ') for word in words]
    words = [word.lower() for word in words]
    words = word_tokenize(' '.join(words))

    return words

#made by
# Normalize all ranks for a list of papers
def normalize_papers(papers):

    # Create rank lists
    journal_ranks = [paper.journal_rank for paper in papers]
    date_ranks = [paper.date_rank for paper in papers]
    title_ranks = [paper.date_rank for paper in papers]
    author_ranks = [paper.author_rank for paper in papers]
    keyword_ranks = [paper.keyword_rank for paper in papers]
    abstract_ranks = [paper.abstract_rank for paper in papers]

    # Calculate max and min for each rank
    max_journal_rank = max(journal_ranks)
    min_journal_rank = min(journal_ranks)

    max_date_rank = max(date_ranks)
    min_date_rank = min(date_ranks)

    max_title_rank = max(title_ranks)
    min_title_rank = min(title_ranks)

    max_author_rank = max(author_ranks)
    min_author_rank = min(author_ranks)
    max_keyword_rank = max(keyword_ranks)
    min_keyword_rank = min(keyword_ranks)

    max_abstract_rank = max(abstract_ranks)
    min_abstract_rank = min(abstract_ranks)

    # Normalize each rank for each paper
    for paper in papers:
        paper.journal_rank = _normalize(paper.journal_rank, max=max_journal_rank, min=min_journal_rank)
        paper.date_rank = _normalize(paper.date_rank, max=max_date_rank, min=min_date_rank)
        paper.title_rank = _normalize(paper.title_rank, max=max_title_rank, min=min_title_rank)
        paper.author_rank = _normalize(paper.author_rank, max=max_author_rank, min=min_author_rank)
        paper.keyword_rank = _normalize(paper.keyword_rank, max=max_keyword_rank, min=min_keyword_rank)
        paper.abstract_rank = _normalize(paper.abstract_rank, max=max_abstract_rank, min=min_abstract_rank)


# Normalizing x by min and max
def _normalize(x, max, min):
    # Handle special cases to avoid division by zero
    if max == min:
        return x
    if max == 0:
        return 0
    else:
        return (x - min) / (max - min)

#was written by Arian
# Calculate each rank, normalize, calculate total rank and return sorted papers
def rank_by_relevance(papers, query):
    logger.info('rank_by_relevance | {} | {}'.format(papers, query))

    if not papers:
        return []

    # Calculate and set each rank
    for paper in papers:
        paper.journal_rank = rank_by_journal(paper.journal_issn)
        paper.date_rank = rank_by_date(paper.date)
        paper.title_rank = rank_by_title(paper.title, query)
        paper.author_rank = rank_by_authors(paper.authors, query)
        paper.keyword_rank = rank_by_keywords(paper.keywords, query)
        paper.abstract_rank = rank_by_abstract(paper.abstract, query)

        logger.info(
            'rank_by_relevance | raw ranks | paper.journal_rank: {}, date_rank: {}, title_rank: {}, author_rank: {}, keyword_rank: {}, abstract_rank: {}'.format(paper.journal_rank, paper.date_rank, paper.title_rank, paper.author_rank, paper.keyword_rank, paper.abstract_rank))

    # Normalize
    normalize_papers(papers)
    for paper in papers:
        logger.info(
            'rank_by_relevance | normalized ranks | paper.journal_rank: {}, date_rank: {}, title_rank: {}, author_rank: {}, keyword_rank: {}, abstract_rank: {}'.format(paper.journal_rank, paper.date_rank, paper.title_rank, paper.author_rank, paper.keyword_rank, paper.abstract_rank))

        # Calculate and set total_rank
        total_rank = (paper.journal_rank + paper.date_rank + paper.title_rank + paper.author_rank + paper.keyword_rank + paper.abstract_rank) / 6
        paper.total_rank = total_rank
        logger.info('rank_by_relevance | paper: {}, rank: {}'.format(paper, total_rank))

    # Return papers sorted by total_rank
    return sorted(papers, key=lambda p: p.total_rank, reverse=True)

#was written by Sabrina
def rank_by_title(title, query):
    logger.info('rank_by_title | keywords: {}, query: {}'.format(title, query))

    if not title:
        return 0

    # Preprocess keywords -> tokenize, lowercase and lemmatize keywords
    tokenized_title = word_tokenize(title)
    tokenized_title = [word.lower() for word in tokenized_title]
    tokenized_title = [lemmatizer.lemmatize(word) for word in tokenized_title]
    logger.info('rank_by_title | tokenized_title | {}'.format(tokenized_title))

    # Preprocess query -> _preprocess_words: get lemma words etc
    tokenized_query = word_tokenize(query)
    tokenized_query = _preprocess_words(tokenized_query)
    logger.info('rank_by_title | tokenized_query | {}'.format(tokenized_query))

    # Unnormalized score for query
    query_score = 0

    # Iterate through each word in query
    for word in tokenized_query:
        word_score = 0

        # Get matches for word in tokenized_keywords
        matches = difflib.get_close_matches(word, tokenized_title)
        l_matches = len(matches)

        # If matches exist -> Calculate word_score by l_matches * ratio(best_match)
        # Increment query_score by word_score
        if l_matches > 0:
            word_score = l_matches * difflib.SequenceMatcher(None, word, matches[0]).ratio()
            query_score = query_score + word_score

        logger.info('rank_by_title | matches for word {}: {}, score: {}'.format(word, matches, word_score))

    return query_score

#was written by Arian
# Preprocess query and keywords and search matches using difflib
def rank_by_keywords(keywords, query):
    logger.info('rank_by_keywords | keywords: {}, query: {}'.format(keywords, query))

    if not keywords:
        return 0

    # Preprocess keywords -> join, tokenize, lowercase and lemmatize keywords
    keywords = ' '.join(keyword for keyword in keywords)
    tokenized_keywords = word_tokenize(keywords)
    tokenized_keywords = [word.lower() for word in tokenized_keywords]
    tokenized_keywords = [lemmatizer.lemmatize(word) for word in tokenized_keywords]
    logger.info('rank_by_keywords | tokenized_keywords | {}'.format(tokenized_keywords))

    # Preprocess query -> _preprocess_words: get lemma words etc
    tokenized_query = word_tokenize(query)
    tokenized_query = _preprocess_words(tokenized_query)
    logger.info('rank_by_keywords | tokenized_query | {}'.format(tokenized_query))

    # Unnormalized score for query
    query_score = 0

    # Iterate through each word in query
    for word in tokenized_query:
        word_score = 0

        # Get matches for word in tokenized_keywords
        matches = difflib.get_close_matches(word, tokenized_keywords)
        l_matches = len(matches)

        # If matches exist -> Calculate word_score by l_matches * ratio(best_match)
        # Increment query_score by word_score
        if l_matches > 0:
            word_score = l_matches * difflib.SequenceMatcher(None, word, matches[0]).ratio()
            query_score = query_score + word_score

        logger.info('rank_by_keywords | matches for word {}: {}, score: {}'.format(word, matches, word_score))

    return query_score

#was written by Arian
def rank_by_date(date):
    logger.info('rank_by_date')

    if not date:
        return 0

    timestamp = datetime.timestamp(date)
    logger.info('rank_by_date | timestamp: {}'.format(timestamp))

    return timestamp

#was written by Arian
# Preprocess query and search matches with authors using difflib
def rank_by_authors(authors, query):
    logger.info('rank_by_authors')

    if not authors:
        return 0

    # Preprocess query -> tokenize and lowercase
    tokenized_query = word_tokenize(query)
    tokenized_query = [word.lower() for word in tokenized_query]

    # Unnormalized score for query
    query_score = 0

    # Iterate through each word in query
    for word in tokenized_query:
        word_score = 0

        # Get matches for word in tokenized_keywords
        matches = difflib.get_close_matches(word, authors)
        l_matches = len(matches)

        # If matches exist -> Calculate word_score by l_matches * ratio(best_match)
        # Increment query_score by word_score
        if l_matches > 0:
            word_score = l_matches * difflib.SequenceMatcher(None, word, matches[0]).ratio()
            query_score = query_score + word_score

        # logger.info('rank_by_authors | matches for word {}: {}, score: {}'.format(word, matches, word_score))

    return query_score

#was written by Andrea
def rank_by_abstract(abstract, query):
    logger.info('rank_by_abstract | keywords: {}, query: {}'.format(abstract, query))

    if not abstract:
        return 0

    # Preprocess keywords -> join, tokenize, lowercase and lemmatize keywords
    tokenized_abstract = word_tokenize(abstract)
    tokenized_abstract = [word.lower() for word in tokenized_abstract]
    tokenized_abstract = [lemmatizer.lemmatize(word) for word in tokenized_abstract]
    logger.info('rank_by_abstract | tokenized_abstract | {}'.format(tokenized_abstract))

    # Preprocess query -> _preprocess_words: get lemma words etc
    tokenized_query = word_tokenize(query)
    tokenized_query = _preprocess_words(tokenized_query)
    logger.info('rank_by_abstract | tokenized_query | {}'.format(tokenized_query))

    # Unnormalized score for query
    query_score = 0

    # Iterate through each word in query
    for word in tokenized_query:
        word_score = 0

        # Get matches for word in tokenized_keywords
        matches = difflib.get_close_matches(word, tokenized_abstract)
        l_matches = len(matches)

        # If matches exist -> Calculate word_score by l_matches * ratio(best_match)
        # Increment query_score by word_score
        if l_matches > 0:
            word_score = l_matches * difflib.SequenceMatcher(None, word, matches[0]).ratio()
            query_score = query_score + word_score

        logger.info('rank_by_abstract | matches for word {}: {}, score: {}'.format(word, matches, word_score))

    return query_score

#was written by Nikita
def rank_by_journal(journal_issn):
    if journal_issn is not None:

        journal_issn = journal_issn.replace('-', '')
        logger.info('relevance_by_journal_rank | {}'.format(journal_issn))
        rank = dict.get(journal_issn)
        logger.info('relevance_by_journal_rank | {} | {}'.format(journal_issn, rank))

        if not rank:
            return 0
        else:
            return rank
    else:
        return 0
