import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    rank_map = {}
    corpus_len = len(corpus)

    for link in corpus:
        rank_map[link] = (1 - damping_factor) / corpus_len
    
    if corpus[page]:
        links = corpus[page]
    else:
        links = corpus.keys()

    for p in corpus:
        if p in links:
            rank_map[p] += damping_factor / len(links)

    return rank_map


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = {}
    
    for page in corpus:
        pagerank[page] = 0
    
    page = random.choice(list(corpus.keys()))
    for _ in range(n):
        pagerank[page] += 1

        sample = transition_model(corpus, page, damping_factor)
        page = random.choices(list(sample.keys()), list(sample.values()))[0]
    
    # Normalize the page_rank counts to sum to 1
    return {page: count / n for page, count in pagerank.items()}


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    corpus_len = len(corpus)

    pagerank = {}
    for page in corpus:
        pagerank[page] = 1 / corpus_len
    
    threshold = 0.001
    new_pagerank = pagerank.copy()

    while True:
        for page in corpus:
            total = (1 - damping_factor) / corpus_len
            for p in corpus:
                if corpus[p]:
                    if page in corpus[p]:
                        total += damping_factor * (
                            pagerank[p] / len(corpus[p])
                        )
                else:
                    total += damping_factor * (pagerank[p] / corpus_len)
            new_pagerank[page] = total
        
        next = True
        for p in pagerank:
            diff = abs(new_pagerank[p] - pagerank[p])
            if diff >= threshold:
                next = False
                break
        
        if next:
            return new_pagerank
        pagerank = new_pagerank.copy()
        

if __name__ == "__main__":
    main()
