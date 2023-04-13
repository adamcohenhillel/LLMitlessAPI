"""String utils
"""
import os
from typing import Tuple, List

import pandas as pd

from tasks.utils import remove_newlines


SKIP = ["node_modules", ".git"]


def load_text_from_path(path: str) -> pd.DataFrame:
    """Load text from a project path into Pandas dataframe

    :param path: path to the project
    """
    texts: List[Tuple[str, str]] = []
    for root, subdirs, files in os.walk(path):
        for filename in files:
            file_path = os.path.join(root, filename)
            if any(skip in file_path for skip in SKIP):
                print('Skipping', file_path)
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as fh:
                    text = fh.read()
                    cleaned_file_name = filename.replace('-',' ').replace('_', ' ')
                    texts.append((cleaned_file_name, text))
            except Exception as e:
                print(f'Skipping file {file_path}')
    for p in texts:
        print(p)
        print('********')
    data_frame = pd.DataFrame(texts, columns = ['fname', 'text'])
    data_frame['text'] = data_frame.fname + ". " + remove_newlines(data_frame.text)
    return data_frame