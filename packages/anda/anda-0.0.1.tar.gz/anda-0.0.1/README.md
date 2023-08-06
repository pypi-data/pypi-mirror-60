# anda

This is a Python package to collecting, manipulation and visualizing ancient Mediterranean data. It focus on their temporal, textual and spatial elements.

It is structured into several gradually evolving parts, mainly `gr`, `concs`, `textnet`, and `imda`

### gr

This module is dedicated to preprocessing of ancient Greek textual data. It contains functions for lemmatization, posttagging and translation. It relies heavely on Morhesus Dictionary.

On the top is the function `get_lemmatized_sentences(string)`.

(1) `get_lemmatized_sentences(string, all_lemmata=False, filter_by_postag=None, involve_unknown=False)`:  it receives a raw Greek text of any kind and extent as its input  Such input is  processed by a series of subsequent functions embedded within each other, which might be also used independently

(1) `get_sentences()` splits the string into sentences by common sentence separators.

(2) `lemmatize_string(sentence)`  first calls `tokenize_string()`, which makes a basic cleaning and stopwords filtering for the sentence, and returns a list of words. Subsequently, each word from the tokenized sentence is sent either to `return_first_lemma()` or to `return_all_unique_lemmata()`, on the basis of the value of the parameter `all_lemmata=` (set to `False` by default). 

(4) `return_all_unique_lemmata()`goes to the `morpheus_dict` values and returns all unique lemmata.

(5) Parameter `filter_by_postag=` (default `None`) enables to sub-select  chosen word types from the tokens, on the basis of first character in the tag "p" . Thus, to choose only  nouns, adjectives, and verbs, you can set  `filter_by_postag=["n", "a", "v"].`

Next to the lemmatization, there is also a series of functions for translations, like `return_all_unique_translations(word, filter_by_postag=None, involve_unknown=False)`, useful for any wordform, and `lemma_translator(word)`, where we already have a lemma.

As a next step, I will put these functions into a package. Perhaps some of my functions could also be implemented into the cltk package. Hopefully I will soon update this post with a link to a repo containing its code and refs.

### concs

This module contains functions for working

### textnet

This module contains functions for generating, analyzing and visualizing word co-occurrence networks. It has been designed especially for working with textual data in ancient Greek. 

### imda

This module will serve for importing various ancient Mediterranean resources. Most of them will be imported directly from open third-party online resources. However, some of them have been preprocessed as part of the SDAM project.

The ideal is that it will work like this:

```
imda.list_datasets()
>>> ['roman_provinces_117', 'EDH', 'roman_cities_hanson', 'orbis_network']
```

And:

```python
rp = imda.import_dataset("roman_provinces_117", "gdf")
type(rp)
>>>geopandas.geodataframe
```

### Versions history

* 0.0.1 - initial installation
