from flask import Flask
from flask import render_template
from flask import request
import logging
from services import paper_repository
from services import paper_ranking_service
import timeit

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
n_papers = 100


@app.route('/')
def search_papers():
    # Get keyword param from http GET request
    keyword = request.args.get('keyword')

    # Set keyword to empty string if None for searchbar to show empty string
    if keyword is None:
        keyword = ""

    app.logger.info('search_papers | {}'.format(keyword))

    # Get papers
    t_before_get_papers = timeit.default_timer()
    papers = paper_repository.get_papers(keyword, n_papers)

    # Rank papers
    t_before_rank_papers = timeit.default_timer()
    ranked_papers = paper_ranking_service.rank_by_relevance(papers, keyword)

    # Evaluation
    # Calculate and log time for getting and ranking papers
    t_end = timeit.default_timer()
    t_get_papers = t_before_rank_papers - t_before_get_papers
    t_rank_papers = t_end - t_before_rank_papers
    app.logger.info('search_papers | t getting papers: {} s'.format(t_get_papers))
    app.logger.info('search_papers | t ranking papers: {} s'.format(t_rank_papers))

    # Evaluation
    # Calculate and log average ranking
    n_papers_found = len(papers)
    rank_sum = sum([paper.total_rank for paper in ranked_papers])
    avg_rank = (rank_sum / n_papers_found) if n_papers_found != 0 else 0
    app.logger.info('search_papers | found {} papers'.format(n_papers_found))
    app.logger.info('search_papers | avg_rank: {}'.format(avg_rank))

    return render_template('index.html', keyword=keyword, papers=ranked_papers)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
