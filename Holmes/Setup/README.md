# Chronos Lightxml Fastxml


We follow chronos, lightxml and fastxml, replace the dataset with our's. 

To be convenient, we copyed their code into our repo for fastxml and lightxml. And pull a docker image for chronos, then we create a table for you to reproducce the tranging and testing data for random, chrono and geneal dataset. 

Chronos Run PATH:

    Random-Order: ./zero_shot_dataset/tenfold/
    Chronological-Order: ./zero_shot_dataset/chronological/
    Generality:   (mentioned below)

Light XML Run PATH:

    Random-Order: data/tenfold/ 
    Chronological-Order: data/chronological/ 
    Generality: data/general/    

Light XML Run PATH:

    Random-Order: dataset/tenfold_generate/
    Chronological-Order: dataset/chronological/
    Generality: dataset/general

(Please  `cd workspace/Chronos` before getting chronos's data. )

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
For generality test, we use `FastXML/dataset/general/general_train.json` to train the model, and `FastXML/dataset/general/deepvul_test_general1105.json` to test the model. <br>
Please refer to https://github.com/soarsmu/ICPC_2022_Automated-Identification-of-Libraries-from-Vulnerability-Data-Can-We-Do-Better/tree/master for more details. <br>

For LightXML, you can manually change the path of training and test data in `/LightXML/src/dataset.py`, line 30, 36, 42, 49. <br>
After changing the data path, you can use the following command to train and test the model. <br>
```
./run.sh cve_data
```
For generality test, we use `./data/general_696/train_text.txt` and `./data/general_696/train_label.txt` to train the model, and test the model on `./data/general1105/test_text.txt` and `./data/general1105/test_label.txt`. <br>
Please refer to https://github.com/soarsmu/ICPC_2022_Automated-Identification-of-Libraries-from-Vulnerability-Data-Can-We-Do-Better/tree/master for more details. <br>

For CHRONOS, you can train and test the model by the following command after pulling the docker file ```docker pull holmes00/chronos_reproduce:v2```: <br> 
```
bash auto_run.sh -d [description data: "merged" or "description_and_reference"]
                 -t [type of data used in training and testing progress: 'general' or 'chronological' or 'random' or 'fold_X'(X = 0, 1, ..., 9)]
                 -l [label processing: "splitting" or "none"]
                 -m [the M parameter on Equation (6) for adjustment] 
                 -i [top-i highest labels for adjustment]
``` 
For example, to reproduce the general test, you can use the following command: <br>
```
bash auto_run.sh -d 'description_and_reference' -t'general' -l 'splitting' -m 0 -i 0
```
Our source data are: `/workspace/Chronos/dataset/description_data/dataset_merged_cleaned_total_general_1105.csv` and `/workspace/Chronos/dataset/reference_data/reference_data_raw_general_1105.csv`. You can generate the test data from scrach by steps below: 
1. Run `/workspace/Chronos/reference_processing/generate_new_csv.py` and copy the output file `/workspace/Chronos/reference_processing/reference_data_raw_0.5_15_general_1105.csv` to `/workspace/Chronos/dataset/reference_data/`. 
2. Run functions `zero_shot_data_splitting`, `zero_shot_data_splitting_chronological` and `zero_shot_data_splitting_general` in `/workspace/Chronos/prepare_data.py` to process data. 
3. Use the commands mentioned before to get certain results. 

The output of all the reproductions are `MAP_result.json` files.