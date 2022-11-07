import pandas as pd
import streamlit as st
from config import required_col,rename_col
import numpy as np
import wget
import os
import zipfile
import json
from collections import ChainMap
import tqdm


###Functions

def check_download_format(n:int)->pd.DataFrame:
    """Function to process and download clinicaltrial Gov Files,Currenty it process n requests

    Returns:
        pd.DataFrame: Selected columns from clincalTrial Gov
    """
    if 'AllAPIJSON.zip' not in os.listdir():    
        url = 'https://ClinicalTrials.gov/AllAPIJSON.zip'
        filename = wget.download(url)
    else:
        print('file already present')
    zip = zipfile.ZipFile('AllAPIJSON.zip', "r")
    all_trials = [f for f in zip.namelist() if f.endswith('.json')]
    print('Total Number of Trials is '+str(len(all_trials)))
    ## Reading
    all_files = pd.DataFrame()
    for f in tqdm.tqdm(all_trials[:n]):
        with zip.open(f) as file:
            data_file = file.read()
            d = json.loads(data_file.decode("utf-8"))
            data_file_pd = pd.json_normalize(d)
            all_files = pd.concat([all_files,data_file_pd],ignore_index=True)
    list_col = []
    for col in all_files.columns:
        if any(isinstance(f,list) for f in all_files[col].tolist()):
            list_col.append(col)
    return all_files[[col for col in all_files.columns if col not in list_col]]


@st.experimental_memo
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

st.set_page_config(page_title="Clinical Trial Explorer", layout="centered")

st.title("Clincial Trial Report")

form = st.form(key="annotation")

with form:
    cols = st.columns((1, 1))
    trial_source = cols[0].text_input("Provide Trial Link:")
    num_trials = cols[1].number_input("Select Number of trials to Display",min_value=1, max_value=1000, value=5, step=1)
    submitted = st.form_submit_button(label="Submit")

if submitted:
    with st.spinner('Wait for it...'):
        output_data = check_download_format(n=num_trials)
        output_data = output_data[required_col]
        output_data = output_data.rename(rename_col,axis = 1)
    st.success("The Trial report is Ready")
    st.balloons()

    expander = st.expander("See Selected records")
    with expander:
        st.write("Record of Selected Trials")
        st.dataframe(output_data)
        csv = convert_df(output_data)
        st.download_button("Press to Download",csv,"file.csv","text/csv",key='download-csv')




