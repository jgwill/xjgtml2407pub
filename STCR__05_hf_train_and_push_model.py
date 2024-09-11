"""
@STCGoal Relevant Storage for Datasets, why would we need a centralized, sharable location for Datasets ? How do we train using that datasets and also publish the model for reuse in observing reality and get an output from the inputs observed in reality ?

"""


#pip install datasets
#%%
from datasets import Dataset

import pandas as pd
#SPX500_H4_mxpto_2407_C03b_mfi_str_df_sell.csv
bs="S"
bs="B"

instrument = "SPX500"
timeframe = "H4"
timeframe = "D1"

for bs in ['B','S']:
    
  _bs="_sell" if bs=="S" else "_buy"

  x_namespace=f"{instrument}_{timeframe}_mxpto_2407_C03b_mfi_str_df{_bs}"
  src_ds_csv_path=f"data/{x_namespace}.csv"

  out_ds_filepath=f"output/{x_namespace}_dataset"

  repo="jgwill/xjgtml2407pub"

  # df=pd.read_csv(src_ds_csv_path,index_col=0)


  # mydata = df.to_dict(orient="list")
  
  # dataset = Dataset.from_dict(mydata)

  # dataset.save_to_disk(out_ds_filepath)

  from huggingface_hub import HfApi, HfFolder


  import os
  # Login to your HuggingFace account
  HfFolder.save_token(os.getenv("HUGGINGFACE_API_KEY"))

  # # Create a dataset repository and push the dataset
  # dataset.push_to_hub(repo,data_dir=x_namespace)

  from datasets import load_dataset

  # Load the dataset
  print("Reading dataset data_dir:",x_namespace, " from repo:",repo)
  dataset = load_dataset(repo, data_dir=x_namespace)

  # Example: Accessing the dataset
  print(dataset)


# %%
