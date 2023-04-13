"""
"""
import pandas as pd


def remove_newlines(serie: pd.Series) -> pd.Series:
    """Remove newlines from a pandas series

    :param serie: pandas series
    """
    serie = serie.str.replace('\n', ' ')
    serie = serie.str.replace('\\n', ' ')
    serie = serie.str.replace('  ', ' ')
    serie = serie.str.replace('  ', ' ')
    return serie


def split_into_many(text: str, tokenizer, max_tokens: int = 1000) -> list:
    """Split the text into chunks of a maximum number of tokens
    """
    sentences = text.split('. ')
    n_tokens = [len(tokenizer.encode(" " + sentence)) for sentence in sentences]
    
    chunks = []
    tokens_so_far = 0
    chunk = []

    for sentence, token in zip(sentences, n_tokens):
        if tokens_so_far + token > max_tokens:
            chunks.append(". ".join(chunk) + ".")
            chunk = []
            tokens_so_far = 0

        if token > max_tokens:
            print("***DOPE")

        chunk.append(sentence)
        tokens_so_far += token + 1

    return chunks
