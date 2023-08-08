import pandas as pd

 
df = pd.read_excel("../../ground_truth/pypimavennpmgo_component_tagging_2023_0417.xlsx")

 
df = df.dropna(subset=[df.columns[4]])
df = df[df.iloc[:, 1].str.contains('CVE-', na=False)]
 
df.to_excel("../../ground_truth/pypimavennpmgo_component_tagging_2023_0417.xlsx", index=False)