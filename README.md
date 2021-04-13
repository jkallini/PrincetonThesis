# PrincetonThesis

The git repository for my Princeton University senior thesis project.

## Install

You will first need to install the required packages. Certain requirements must be installed before others.

The Berkeley Neural Parser (benepar) depends on cython and numpy. Install these packages first:
```
pip install cython numpy
```

Then you may install the remaining packages in `requirements.txt`:
```
pip install -r requirements.txt
```

Next, install spaCy's large English model:
```
python -m spacy download en
```

Next, install the required NLTK packages:
```
python nltk_download.py
```
You may select the packages manually, or download the entire NLTK library using the NLTK GUI.


The required NLTK packages are:
- punkt
- stopwords
- wordnet  

Next, download benepar's English parsing model:
```
python benepar_download.py
```

Finally, there are some manual changes that need to be made to the benepar code in order for it to be compatible with tensorflow 2.x. If you named your python environment `env`, you should be able to find the benepar code in your environment's `env/lib/pythonX.X/site-packages/` directory. In the `benepar` directory, the file `base_parser.py` contains the relevant code that must be fixed.

In `base_parser.py`, change all occurrences of...
- `tf.Graph()` to `tf.compat.v1.Graph()`
- `tf.GraphDef()` to `tf.compat.v1.GraphDef()`
- `tf.Session()` to `tf.compat.v1.Session()`
