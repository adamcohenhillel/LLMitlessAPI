"""Onboardy.dev - POC
"""
import os

import openai
from openai.embeddings_utils import distances_from_embeddings
import pandas as pd
import tiktoken

from tasks.utils import split_into_many


openai.api_key = os.environ.get('OPENAI_APIKEY')

    
def add_embeddings_to_dataframe(
    data_frame: pd.DataFrame,
    max_tokens: int = 1000,
) -> pd.DataFrame:
    """Process a project and return a dataframe of the texts and their embeddings

    :param data_frame: A dataframe of the texts
    :param max_tokens: Maximum number of tokens to allow in a single text

    :return: A dataframe of the texts and their embeddings
    """
    tokenizer: tiktoken.Encoding = tiktoken.get_encoding("cl100k_base")

    data_frame['n_tokens'] = data_frame.text.apply(lambda x: len(tokenizer.encode(x)))

    shortened = []
    for row in data_frame.iterrows():
        if row[1]['text'] is None:
            print('Skipping row', row[0])
            continue
        if row[1]['n_tokens'] > max_tokens:
            shortened += split_into_many(row[1]['text'], tokenizer=tokenizer)
        else:
            shortened.append(row[1]['text'])

    data_frame = pd.DataFrame(shortened, columns = ['text'])
    data_frame['n_tokens'] = data_frame.text.apply(lambda x: len(tokenizer.encode(x)))

    data_frame['embeddings'] = data_frame.text.apply(
        lambda x: openai.Embedding.create(
            input=x,
            engine='text-embedding-ada-002'
        )['data'][0]['embedding']
    )

    return data_frame



def create_context(
    question: str,
    data_frame: pd.DataFrame,
    max_len: int = 1800,
) -> str:
    """Create a context for a question by finding the most similar context from the dataframe
    """
    q_embeddings = openai.Embedding.create(
        input=question,
        engine='text-embedding-ada-002'
    )['data'][0]['embedding']

    # Get the distances from the embeddings
    data_frame['distances'] = distances_from_embeddings(
        q_embeddings,
        data_frame['embeddings'].values,
        distance_metric='cosine'
    )


    returns = []
    current_len = 0

    # Sort by distance and add the text to the context until the context is too long
    for _, row in data_frame.sort_values('distances', ascending=True).iterrows():
        # Add the length of the text to the current length
        current_len += row['n_tokens'] + 4
        # If the context is too long, break
        if current_len > max_len:
            break
        returns.append(row["text"])

    # Return the context
    return "\n\n###\n\n".join(returns)


def generate_readme(question: str, context: str) -> str:
    """Generate a readme tutorial based on given question and context

    :param question: Question to answer
    :param context: Context to use
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                    {"role": "system", "content": "You are generating readme file to explain code based on a user question and code snippets"},
                    {"role": "user", "content": f"Using code snippets from the context, create readme file that explains the question: \"{question}\" \nContext:\n\n{context}"}
                ]
        )
        return response["choices"][0]["message"]["content"]

    except Exception as e:
        print(e)
        return ""