# cn_workday

Workday detection for the People's Republic of China.

# Installation

```shell
pip install -U cn_workday
```

# Usage

This package provides only a single function currently.

```python
>>> from cn_workday import is_workday
>>> from datetime import datetime
>>> is_workday(datetime.now())
>>> ...
```

# Data files

This package is based on data files in CSV formats. They are stored in `data`
 directory inside the package. Each file contains the official holidays
 and their tradeoffs (if any).

Currently we only have data files from 2017 to 2020. If you'd like
 to contribute, please take a look at the existing data files.

The official holiday definitions of the next year is usually published
 in November by Chinese government, you can find them [here][gov_cn_node_330].
 Each data file should also contain a link to the official announcement, as a
 comment at the end of file.

# Notice

This package is currently not compatible with `PyOxidizer` due to its using of
 `__file__` (to load data files). Until there is a recommended way to handle
 data files, this is likely to stay the same. Read more [here][py_oxidizer_i69].


  [gov_cn_node_330]: http://www.gov.cn/zhengce/content/node_330.htm
  [py_oxidizer_i69]: https://github.com/indygreg/PyOxidizer/issues/69

