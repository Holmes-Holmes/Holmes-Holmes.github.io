---
layout: default
---

Software composition analysis (SCA) tools have been widely adopted to identify vulnerable libraries used in software applications. Such SCA tools depend on a vulnerability database to know affected libraries of each vulnerability. However, it is labor-intensive and error-prone for a security team to manually maintain the vulnerability database. While
several approaches adopt extreme multi-label learning to predict affected libraries for vulnerabilities, they are practically ineffective due to the limited library labels and the unawareness of ecosystems. To address these problems, we first conduct an empirical study to assess the quality of two fields, i.e., affected libraries and their ecosystems, for four vulnerability databases. Our study reveals notable inconsistency and inaccuracy in these two fields. Then, we propose
Holmes to identify affected libraries and their ecosystems for vulnerabilities via a learning-to-rank technique. The key idea of Holmes is to gather various evidences about affected libraries and their ecosystems from multiple sources, and learn to rank a pool of libraries based on their relevance to evidences. Our extensive experiments haveshown the effectiveness, efficiency and usefulness of Holmes.

# Empirical Study
The large scale of our component_dataset are releaed in [GroundTruth](https://github.com) and [GroundTruth](https://github.com)
There are three parts of our component_dataset:
  1. [large scale dataset](https://github.com/)
  2. [large scale dataset with same eco](https://github.com/)
  3. [Ground Truth](https://github.com/)
To replicate our results for RQ1, please use:
```
python xx/xx/xx eco_consistency
python xx/xx/xx name_consistency  
```
To replicate our results for RQ2, please use:
```
python xx/xx/xx accuracy
```

# Approach

# Evaluation
