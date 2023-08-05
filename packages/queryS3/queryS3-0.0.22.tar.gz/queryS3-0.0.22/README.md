# queryS3 API
## Introduction
This API enable users to query images from AI Testing database, currently implementing on AWS S3, with natural English description. A string of keywords also works if users want to put more restrictions onto the picture. The main functionality of this API can be treated in a blackbox manner. That it takes is a string of description and returns a list of S3 object URL of the images.

## Dependencies
**[- nltk](https://www.nltk.org/): Natural Language Toolkit** [github link](https://github.com/nltk/nltk)

**[- pandas](https://pandas.pydata.org/pandas-docs/stable/): powerful Python data analysis toolkit** [github link](https://github.com/pandas-dev/pandas)

## Installation
```bash
pip install queryS3
```

## Example usage
```python
from queryS3 import QS3

qs = QS3.QS3()

# this line will retrieve all images that have single husky
# the return type will be a python list
qs.query('single husky')
```

## API details

**QS.query(in_q: str): -> List[str]**: "query" is a function in the class QS. It takes a english description(or a string of keywords needed) as input and returns a list of S3 object URL strings

**QS.set_label_list(self, label_list: List[str])**: This function will replace the original label list in the database with a new list of labels only for this object instance of QS. By doing so, the whole "extract label from description" and "label matching search" process will then based on the new set of labels. Duplicated labels will be removed.

**QS.add_label_list(self, label_list: List[str])**: This function will append the label list with the newly added list. Duplicated labels will be removed.

## Author
**[Qiao Liu](https://github.com/qiaol)**
, **[Everette Li](https://github.com/everetteli)**

## Copyright
Copyright © 2020, The AITestResourceLibrary Authority. Released under the MIT License.
