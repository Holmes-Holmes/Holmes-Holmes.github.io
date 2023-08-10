# How to start

## Evidence Gather
We use EvidenceGather to gather evidence, and there are the details our paper mentions, like the regular expression about [class name](EvidenceGather/RegularClaName.class) and [file path](EvidenceGather/RegularPathName.java).

## Relevance Calculation

We use Matchers to calculate relevance. 

1. First, we initialize the [Lucene](ApproachImp/Matchers/tools)(including the prerocess and improved BM25)

2. The, we have persisted the search engines as services and deployed them on four ports for invocation

## Rank

We use the [xgboost](https://github.com/dmlc/xgboost) to achieve lambdamark.

1. Use the [data preparation](Rank/xgboost_lambdarank/transfer_csv_2_train_test.py) to prepare your ten-fold dataset.
2. Then use the [validation](Rank/xgboost_lambdarank/eval_map.py) to traning and test your model. Then you can also get the map result for RQ3,4,6.