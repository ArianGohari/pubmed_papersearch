from Bio import Entrez
import datetime
import logging
from model.paper import Paper

# Initialization: Set loggger, set Entrez email
logger = logging.getLogger("paper_repository")
Entrez.email = "papersearch.gruppe3@gmail.com"


# E-search pmc database for query -> return 20 results
def pmc_search(query, n):
    logger.info('pmc_search | {}'.format(query))

    handle = Entrez.esearch(db='pmc', sort='relevance', retmax=str(n), retmode='xml', term=query)
    results = Entrez.read(handle)
    return results


# E-summary for a list of pmcids
def pmc_summaries(pmcids):
    logger.info('pmc_summaries | {}'.format(pmcids))

    if not pmcids:
        return []

    ids = ','.join(pmcids)
    handle = Entrez.esummary(db='pmc', retmode='xml', id=ids)
    results = Entrez.read(handle)
    return results


# Get amount of citations of paper pmcid using E-Link
def pmc_citedby(pmcid):
    logger.info('pmc_citedby | {}'.format(pmcid))

    handle = Entrez.elink(dbfrom='pubmed', retmode='xml', linkname='pmc_pmc_citedby', id=id)
    results = Entrez.read(handle)
    link_set = results[0].get('LinkSetDb', [])

    if not link_set:
        return 0
    else:
        return len(link_set[0].get('Link'))


# E-Fetch paper details from pubmed database for a list of pmids
def pubmed_details(pmids):
    logger.info('pubmed_details | {}'.format(pmids))

    if not pmids:
        return {}

    ids = ','.join(pmids)
    handle = Entrez.efetch(db='pubmed', retmode='xml', id=ids)
    results = Entrez.read(handle)
    return results


# Returns a dict with each paper object assigned to its pmcid
def init_papers_by_pmcid(pmcids):
    logger.info('init_papers_by_pmcid')

    papers_by_pmcid = {}

    for pmcid in pmcids:
        paper = Paper()
        paper.pmcid = pmcid
        papers_by_pmcid[pmcid] = paper

    return papers_by_pmcid


# Adds pmc summaries to each paper in papers_by_pmcid dict
# Returns a dict with each pmcid assigned to its pmid
def add_pmc_data(papers_by_pmcid, summary_results):
    logger.info('add_pmc_data')

    pmcid_by_pmid = {}

    for result in summary_results:
        # Read ids from JSON
        pmcid = result.get('Id')
        pmid = result.get('ArticleIds', {}).get('pmid')
        doi = result.get('ArticleIds', {}).get('doi')

        # Read title from JSON
        title = result.get('Title')

        # Assign pmid to pmcid
        pmcid_by_pmid[pmid] = pmcid

        # Get paper by pmcid
        paper = papers_by_pmcid[pmcid]

        # Add data to paper
        paper.pmid = pmid
        paper.doi = doi
        paper.title = title

    return pmcid_by_pmid


# Adds pubmed detail data to each paper from papers_by_pmcid dict
def add_pubmed_data(papers_by_pmcid, pmcid_by_pmid, detail_results):
    logger.info('add_pubmed_data')

    for result in detail_results:
        medline_citation = result.get('MedlineCitation', {})
        article = medline_citation.get('Article', {})

        # Read abstract from JSON
        abstract_list = article.get('Abstract', {}).get('AbstractText')
        abstract = abstract_list[0] if abstract_list else ''

        # Read date from JSON
        article_date = article.get('ArticleDate', [])
        if article_date:
            day = int(article_date[0].get('Day'))
            month = int(article_date[0].get('Month'))
            year = int(article_date[0].get('Year'))
            date = datetime.datetime(year, month, day)
        else:
            date = None

        # Read authors from JSON
        author_list = article.get('AuthorList', [])
        authors = ["{} {}".format(author.get('ForeName', ''), author.get('LastName', '')) for author in author_list]

        # Read journal data from JSON
        journal = article.get('Journal', {})
        journal_issn = journal.get('ISSN')
        journal_name = journal.get('Title')

        # Read keywords from JSON
        keyword_list = medline_citation.get('KeywordList', [])
        keywords = keyword_list[0] if len(keyword_list) > 0 else []

        # Read pmid from JSON
        pmid = medline_citation.get('PMID')

        # Get paper by pmid
        pmcid = pmcid_by_pmid[pmid]
        paper = papers_by_pmcid[pmcid]

        # Add data to paper
        paper.abstract = abstract
        paper.date = date
        paper.authors = authors
        paper.journal_issn = journal_issn
        paper.journal_name = journal_name
        paper.keywords = keywords
        paper.pmid = pmid


# Search in pmc and pubmed databases for n papers by query using E-eutils
# Returns list of fetched papers (paper objects)
def get_papers(query, n):
    logger.info('get_papers | {}'.format(query))

    # Return empty list if query empty
    if not query or query == "":
        return []

    # Get pmcids for query
    search_results = pmc_search(query, n)
    pmcids = search_results.get('IdList', [])

    # Initialize papers_by_pmcid
    papers_by_pmcid = init_papers_by_pmcid(pmcids)

    # Get summaries and add to data to papers
    summary_results = pmc_summaries(pmcids)
    pmcid_by_pmid = add_pmc_data(papers_by_pmcid, summary_results)

    # Get pmids from papers_by_pmcid
    pmids = [paper.pmid for paper in papers_by_pmcid.values()]

    # Get details for pmids and add to papers
    detail_results = pubmed_details(pmids).get("PubmedArticle", [])
    add_pubmed_data(papers_by_pmcid, pmcid_by_pmid, detail_results)

    # All data is now added to papers in papers_by_pmcid -> return values
    return papers_by_pmcid.values()
