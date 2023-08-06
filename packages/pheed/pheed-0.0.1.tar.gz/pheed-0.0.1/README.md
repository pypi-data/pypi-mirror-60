# Python tools for aggregating physics literature

The `pheed` (PHysics fEED) package collects physics literature meta data from various online sources and normalizes
the resulting data into a standard format. The package provides three principal data structures. A simplified summary, 
a `Source` produces and `Article` which has an `Author`. It is possible to search for new articles from a source given
some temporal and categorial information, such as "new this week" or "quantum gravity", as well as search for new 
articles by particular authors. Where official APIs exist, we use them, else we resort to web-scraping. As a 
consequence, the pdf form of the articles may not always be available. We aim to add these features where possible
while respecting the Terms and Conditions of the sources involved. The package hasn't added explicit support for 
non-peer-reviewed sources, such as Blogs, though we realize that these can be quite popular in the community and 
may add support in the future.


## Principal Structure

The below outlines the key components of the `pheed` package, and defines some of the relevant attributes or purposes
of each. Examples below will explain usage of each of these components.

- `Source`: An online origin for physics articles
- `Article`: A peer-reviewed publication, typically consisting of a pdf and some meta-data
- `Author`: Contributor to an `Article`, with the expected attributes (name, etc.)


## Wrapped Sources

Though the `pheed` package contains all the tools necessary to wrap additonal sources,
it comes with several sources already wrapped out of the box:

- APS Journals
- IOP Journals
- Arxiv
