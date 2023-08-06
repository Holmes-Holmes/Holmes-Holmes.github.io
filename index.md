---
layout: default
---

![Octocat](approach.png)


Software composition analysis (SCA) tools have been widely adopted to identify vulnerable libraries used in software applications. Such SCA tools depend on a vulnerability database to know affected libraries of each vulnerability. However, it is labor-intensive and error-prone for a security team to manually maintain the vulnerability database. While
several approaches adopt extreme multi-label learning to predict affected libraries for vulnerabilities, they are practically ineffective due to the limited library labels and the unawareness of ecosystems. To address these problems, we first conduct an empirical study to assess the quality of two fields, i.e., affected libraries and their ecosystems, for four vulnerability databases. Our study reveals notable inconsistency and inaccuracy in these two fields. Then, we propose
Holmes to identify affected libraries and their ecosystems for vulnerabilities via a learning-to-rank technique. The key idea of Holmes is to gather various evidences about affected libraries and their ecosystems from multiple sources, and learn to rank a pool of libraries based on their relevance to evidences. Our extensive experiments haveshown the effectiveness, efficiency and usefulness of Holmes.

# Dataset

* large scale dataset
    > [xxx](https://github.com/)
    
    > [large scale dataset with same eco](https://github.com/)
* GroundTruth
    > [Ground Truth](https://github.com/)

# Empirical Study

To replicate our results for RQ1, please use:
```
python xx/xx/xx eco_consistency
python xx/xx/xx name_consistency  
```
To replicate our results for RQ2, please use:
```
python xx/xx/xx accuracy
```

# Approach Implement


## Evidence Gathering


## Lucene

# Evaluation
The evaluation contains RQ3, RQ4, RQ5, RQ6 and RQ7

## RQ3 Effectiveness Evaluation

* Random-Order
```
./run.sh random_order
```

* Chronological-Order
```
./run.sh chronological-order
```

## RQ4 Ablation Study

* Random-Order
```
./run.sh Ablation_Random
```

* Chronological-Order
```
./run.sh Ablation_Chronological
```

## RQ5 Efficiency Evaluation

We count the time costs in evidence gathering, relevance calculation and library ranking.
To replicate our results for RQ5, please use:

```
./run.sh Efficiency
```

## RQ6 Generality Evaluation

```
./run.sh Generality
```

## RQ7 Usefulness Evaluation

* Human Study

    ```
    ./run.sh HumanStudy
    ```

* Vendor Reporting

    > xxx inaccurate CVEs for GitHub: [Inaccurate-Affected-Components-in-GitHub]()
    > xxx inaccurate CVEs for GitLab: [Inaccurate-Affected-Components-in-GitHub]()
    > xxx inaccurate CVEs for Snyk: [Inaccurate-Affected-Components-in-GitHub]()
    > xxx inaccurate CVEs for Veracode: [Inaccurate-Affected-Components-in-GitHub]()


# Chronos Lightxml Fastxml

## Dataset
- data preparing
    We follow [chronos], [lightxml] and [fastxml], and replace the dataset with our's. 
    - The script of full list of veracode libraries mentioned in xxx.

    - The website of the referenced data's script is released in xxx.

    To be convenient, we copyed their code into our repo for fastxml and lightxml. And pull a docker image for chronos, then we create a table for you to reproducce the tranging and testing data for random, chrono and geneal dataset


| head1        | Random-Order        | chronological-order   | Generality | 
|:-------------|:-------------|:-------------|:-------------| 
| Chronos      | path   | path          | path    | 
| Lightxml     | data/tenfold     | data/chronological           | data/general_data    | 
| Fastxml      | dataset/tenfold_generate/       | dataset/chronological               | dataset/general   |

To train FastXML, you can use the following command:<br>
```
python baseline.py model/model_name.model {training_data_path} --verbose train --iters 200 --gamma 30 --trees 64 --min-label-count 1 --blend-factor 0.5  --re_split 0 --leaf-probs
```
You can change the third parameter to change the path of training data, for example: <br>
```
python baseline.py model/model_name.model dataset/tenfold_generate/fold_0/train.json --verbose train --iters 200 --gamma 30 --trees 64 --min-label-count 1 --blend-factor 0.5  --re_split 0 --leaf-probs
```

To test the model, you can use the following command: <br>
```
python baseline.py model/model_name.model {test_data_path} inference --score
python util.py
```
Also, you can change the third parameter to change the path of test data. <br>
For generality test, we use `FastXML/dataset/tenfold_generate/fold_0/train.json` to train the model, and `FastXML/dataset/general/deepvul_test_total_general.json` to test the model. <br>
Please refer to https://github.com/soarsmu/ICPC_2022_Automated-Identification-of-Libraries-from-Vulnerability-Data-Can-We-Do-Better/tree/master for more details. <br>

For LightXML, you can manually change the path of training and test data in `/LightXML/src/dataset.py`, line 30, 36, 42, 49. <br>
After changing the data path, you can use the following command to train and test the model. <br>
```
./run.sh cve_data
```
For generality test, we use `/data/tenfold/fold_0/train_general_texts.txt` and `/data/tenfold/fold_0/train_general_labels.txt` to train the model, and test the model on `/data/general_data/general_test_texts.txt` and `/data/general_data/general_test_labels.txt`. <br>
Please refer to https://github.com/soarsmu/ICPC_2022_Automated-Identification-of-Libraries-from-Vulnerability-Data-Can-We-Do-Better/tree/master for more details. <br>
