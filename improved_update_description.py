import os
import re
import shutil

from pathlib import Path

import pandas as pd

def get_list_files_path(folder_path, pattern='.*(zip|rar|7z).*'):
    """
        By default return a list of path containing zip, rar or 7z files.
    """

    list_file_path= []
    archives_list = Path(folder_path).rglob('*.*')
    for path_ in archives_list:
        if re.match(pattern, path_.name):
            list_file_path.append(path_)

    return list_file_path

def get_list_dict(list_file_path : list[Path], document_hashtag=None):
    
    l = []
    if document_hashtag:
        for index, file_path in enumerate(list_file_path):
            d = {}
            index_str = f"{index+1:03}"
            file_name = file_path.stem
            d["file_output"] = str(file_path)
            d["description"] = f"#{document_hashtag}{index_str}\n\n{file_name}"
            d["warning"] = ""
            l.append(d)
    else: 
        for file_path in list_file_path:
            d = {}
            file_name = file_path.stem
            d["file_output"] = str(file_path)
            d["description"] = file_name
            d["warning"] = ""
            l.append(d)

    return l

def get_df_desc_docs(dict_description_docs):

    df = pd.DataFrame(dict_description_docs)
    return df


def get_df_description_original(folder_path_output):

    path_file_description = os.path.join(folder_path_output, "upload_plan.csv")
    df_desc = pd.read_csv(path_file_description)
    return df_desc


def save_desc_updated(folder_path_output, df_desc_update):

    path_file_description = os.path.join(folder_path_output, "upload_plan.csv")
    # backup
    path_file_description_to = os.path.join(
        folder_path_output, "upload_plan-only_videos.csv"
    )
    shutil.copy(path_file_description, path_file_description_to)

    # save
    df_desc_update.to_csv(path_file_description, index=False)


def descriptions_report_update_with_docs(
    folder_path_output, list_file_path, document_hashtag=None, **kwargs
):
    dict_description_docs = get_list_dict(list_file_path, document_hashtag=document_hashtag)
    print(dict_description_docs)
    df_desc_docs = get_df_desc_docs(dict_description_docs)
    df_desc = get_df_description_original(folder_path_output)

    if 'axis' in kwargs:
        df_desc_update = pd.concat([df_desc_docs, df_desc], axis=kwargs.get('axis')).reset_index(drop=True)
    else:
        df_desc_update = pd.concat([df_desc_docs, df_desc]).reset_index(drop=True)

    if 'sort' in kwargs:
        df_desc_update = df_desc_update.sort_values(by='file_output').reset_index(drop=True)

    save_desc_updated(folder_path_output, df_desc_update)

def get_list_file_path_zip(folder_path_output):

    folder_path_output_files = os.path.join(
        folder_path_output, "output_videos"
    )
    list_file_path_zip = get_list_files_path(folder_path_output_files)
    return list_file_path_zip
