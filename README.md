# PubTrends Task

1. I have a list of unique identifiers assigned to scientific publications by the PubMed database (PMID). You can download it [here](https://drive.google.com/file/d/1VGQ9BW99ekx4_LIHbeEx2z0VGqbUxWM6/view).
2. Each PMID can be linked to open datasets stored in the [GEO database](https://www.ncbi.nlm.nih.gov/gds/). I retrieve the GEO (or GSE) identifiers corresponding to each PMID using the e-utils API.
    * Example API Call for PMID=[25404168](https://pubmed.ncbi.nlm.nih.gov/25404168/):
      [eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&db=gds&linkname=pubmed_gds&id=25404168&retmode=xml](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&db=gds&linkname=pubmed_gds&id=25404168&retmode=xml)
    * [eutils API documentation](https://www.ncbi.nlm.nih.gov/books/NBK25497/)
3. I am interested in the following text fields of the resulting GEO datasets: Title, Experiment type, Summary, Organism, Overall design. I'm using [tf-idf](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) to build a vector representation of these fields merged together.
4. As a result I have a service that takes a list of PMIDs and returns result.json of corresponding dataset clusters based on tf-idf vectors.
