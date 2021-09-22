class Paper:
    global snippet_max_size
    snippet_max_size = 500

    def __init__(self):
        self._pmcid = None
        self._pmid = None
        self._doi = None
        self._title = None
        self._abstract = None
        self._keywords = []
        self._journal_issn = None
        self._journal_name = None
        self._date = None
        self._authors = []
        self._date_rank = -1
        self._author_rank = -1
        self._keyword_rank = -1
        self._total_rank = -1

    # PMCID
    @property
    def pmcid(self):
        return self._pmcid

    @pmcid.setter
    def pmcid(self, value):
        self._pmcid = value

    # PMID
    @property
    def pmid(self):
        return self._pmid

    @pmid.setter
    def pmid(self, value):
        self._pmid = value

    # PMID
    @property
    def doi(self):
        return self._doi

    @doi.setter
    def doi(self, value):
        self._doi = value

    # Title
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    # Abstract
    @property
    def abstract(self):
        return self._abstract

    @abstract.setter
    def abstract(self, value):
        self._abstract = value

    # Keywords
    @property
    def keywords(self):
        return self._keywords

    @keywords.setter
    def keywords(self, value):
        self._keywords = value

    # Journal ISSN
    @property
    def journal_issn(self):
        return self._journal_issn

    @journal_issn.setter
    def journal_issn(self, value):
        self._journal_issn = value

    # Journal Name
    @property
    def journal_name(self):
        return self._journal_name

    @journal_name.setter
    def journal_name(self, value):
        self._journal_name = value

    # Date
    @property
    def date(self):
        return self._date

    @property
    def date_str(self):
        return self._date.strftime("%m/%d/%Y")

    @date.setter
    def date(self, value):
        self._date = value

    # Authors
    @property
    def authors(self):
        return self._authors

    @property
    def authors_str(self):
        return ', '.join(self._authors)

    @authors.setter
    def authors(self, value):
        self._authors = value

    # Date Rank
    @property
    def date_rank(self):
        return self._date_rank

    @date_rank.setter
    def date_rank(self, value):
        self._date_rank = value

    # Author Rank
    @property
    def author_rank(self):
        return self._author_rank

    @author_rank.setter
    def author_rank(self, value):
        self._author_rank = value

    # Keyword Rank
    @property
    def keyword_rank(self):
        return self._keyword_rank

    @keyword_rank.setter
    def keyword_rank(self, value):
        self._keyword_rank = value

    # Total Rank
    @property
    def total_rank(self):
        return self._total_rank

    @total_rank.setter
    def total_rank(self, value):
        self._total_rank = value

    # URL
    @property
    def url(self):
        # Using DOI:
        # return 'https://www.doi.org/{}'.format(self._doi)

        # Using PubMed:
        return 'https://pubmed.ncbi.nlm.nih.gov/{}'.format(self._pmid)

    # Snippet (500 characters) of the abstract
    @property
    def snippet(self):
        # Return "" if astract is None
        if(self.abstract is None):
            return ""
        # Return abstract if len(abstract) < 500
        elif(len(self.abstract) < snippet_max_size):
            return self.abstract
        # Return snippet
        else:
            return "{}...".format("%.500s" % self.abstract)

    # String representation of Paper object
    def __repr__(self):
        return self._pmcid

    def __str__(self):
        return self._pmcid
