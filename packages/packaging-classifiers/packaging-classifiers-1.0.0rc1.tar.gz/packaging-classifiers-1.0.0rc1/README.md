# `packaging-classifiers`
Cannonical source for classifiers on PyPI (pypi.org).

# Usage
Check if a classifier is valid:

```
>>> from packaging_classifiers import classifiers
>>> 'License :: OSI Approved' in classifiers
True
>>> 'Fuzzy Wuzzy :: Was :: A :: Bear' in classifiers
False
>>>
```

Determine if a classifier is deprecated:

```
>>> classifiers['License :: OSI Approved'].deprecated
False
>>> classifiers["Natural Language :: Ukranian"].deprecated
True
>>> classifiers["Natural Language :: Ukranian"].deprecated_by
['Natural Language :: Ukrainian']
```
