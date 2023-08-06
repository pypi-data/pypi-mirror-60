# ST-DBSCAN

**Simple and effective tool for spatial-temporal clustering**

*st_dbscan* is an open-source software package for the spatial-temporal clustering of movement data:

- Implemnted using `numpy` and `sklearn`
- Enables to also scale to memory - with splitting the data into frames
- __Usage:__ can view a demo of common features in this
[this Jupyter Notebook](/demo/demo.ipynb).

## Installation
The easiest way to install *st_dbscan* is by using `pip` :

    pip install st_dbscan

## Description

A package to perform the ST_DBSCAN clustering. For more details please see the following papers: 

*     Ester, M., H. P. Kriegel, J. Sander, and X. Xu, "A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise". In: Proceedings of the 2nd International Conference on Knowledge Discovery and Data Mining, Portland, OR, AAAI Press, pp. 226-231. 1996
*     Birant, Derya, and Alp Kut. "ST-DBSCAN: An algorithm for clustering spatial–temporal data." Data & Knowledge Engineering 60.1 (2007): 208-221.
*     Peca, I., Fuchs, G., Vrotsou, K., Andrienko, N. V., & Andrienko, G. L. (2012). Scalable Cluster Analysis of Spatial Events. In EuroVA@ EuroVis.

## License
This package was developed by Eren Cakmak from the [Data Analysis and Visualization Group](https://www.vis.uni-konstanz.de/) and the [Department of Collective Behaviour](http://collectivebehaviour.com) at the University Konstanz, with funding from the DFG Centre of Excellence 2117 "Centre for the Advanced Study of Collective Behaviour" (ID: 422037984).

Released under MIT License. See the [LICENSE](LICENSE) file for details.
