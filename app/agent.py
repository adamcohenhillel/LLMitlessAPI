import os
import json
from typing import Dict

import openai
from openai.embeddings_utils import distances_from_embeddings
import pandas as pd
import tiktoken


openai.api_key = os.environ.get('OPENAI_APIKEY')
memory = pd.DataFrame([], columns = ['text', 'embeddings', 'n_tokens', 'distances'])

ACTIONS: dict = {
    "SAVE": "Save information to database, so you can retrieve it later",
    "FETCH": "Fetch information from database",
    "EVAL": "Execute a python expression that is present inside a string",
    "FINISHED": "Finish serving the request",
}


def fetch(memory: pd.DataFrame, to_retrieve: str, depth: int = 50) -> str:
    """Trying to retrieve information from memory

    :param memory: A dataframe of the texts and their embeddings
    :param retrieve: The information to retrieve from memory
    :param depth: How many results to return

    :return: The information retrieved from memory
    """
    to_retrieve = str(to_retrieve).replace("{", " ").replace("}", " ")
    info_embedded = openai.Embedding.create(
        input=to_retrieve,
        engine='text-embedding-ada-002'
    )['data'][0]['embedding']

    # Get the distances from the embeddings
    memory['distances'] = distances_from_embeddings(
        info_embedded,
        memory['embeddings'].values,
        distance_metric='cosine'
    )

    relevant_memories = []
    for _, row in memory.sort_values('distances', ascending=True).head(depth).iterrows():
        relevant_memories.append(row["text"])

    return "\n###\n".join(relevant_memories)


def save(memory: pd.DataFrame, information: str) -> pd.DataFrame:
    """Saving information to memory (embeddings)

    :param memory: A dataframe of the texts and their embeddings
    :param information: The information to save to memory

    :return: Updated dataframe of the memory with the new information
    """
    information = str(information).replace("{", " ").replace("}", " ")
    tokenizer: tiktoken.Encoding = tiktoken.get_encoding("cl100k_base")
    n_tokens = len(tokenizer.encode(information))
    embeddings = openai.Embedding.create(
        input=str(information),
        engine='text-embedding-ada-002'
    )['data'][0]['embedding']
    new_memory = pd.concat([
        memory,
        pd.DataFrame([{'text': information, 'n_tokens': n_tokens, 'embeddings': embeddings}])
    ], ignore_index=True)
    return new_memory


def thought_process(conversation_context: list, service: str, data: dict):
    """Uses to decide what to do next, based on the previous actions and the constraints of the agent's world.
    """

    meta_prompt = '''You are autonomus agent called "assistant" which act as an API service. You are given a service to act as, and a body data to act on.
To serve the request, you must choose one of following actions, one at a time, until you finish serving the request.
Actions:
<actions>

Rules:
1. As "assistant", you MUST response only with the following JSON format:\n{"action": "<ACTION>", "info": "<INFO_FOR_THE_ACTION>"}
2. Action must be one of the provided actions above.
3. The responses from "user" are the results of the action you performed. Use them to choose your next action.
4. When finished serving a request, include the end response to the user with the FINISHED action.
'''

    meta_prompt = meta_prompt.replace("<actions>", "\n".join([f"{i+1}. {k} - {v}" for i, (k, v) in enumerate(ACTIONS.items())]))

    conversation_context = [
        {"role": "system", "content": meta_prompt},
        {"role": "user", "content": f"Service: {service}\nBody Data: {data}"},
        *conversation_context
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=conversation_context,
        )
        message = response["choices"][0]["message"]
        return message
    except Exception as e:
        print(e)
        return ""


def agent_loop(task_id: str, tasks_status: Dict, service: str, data: str):
    """The main loop of the agent

    """
    global memory
    print(f'\33[36m\nBooting agent for task: {task_id}...\33[0m')

    conversation_context = []
    running = True

    while running:

        # Choose the next action:
        action = thought_process(
            conversation_context,
            service,
            data
        )
        conversation_context.append(action)

        try:
            action_content = json.loads(action["content"])

            # Execute the action:
            if action_content['action'] == 'SAVE':
                print(f"\33[0;37m\nSAVE: {action_content['info']}\33[0m")
                memory = save(memory, action_content['info'])
                conversation_context.append({"role": "user", "content": "SAVED."})

            elif action_content['action'] == 'FETCH':
                print(f"\33[0;37m\nFetch query: {action_content['info']}\33[0m")
                remembered = fetch(memory, action_content['info']) or "Nothing found."
                print(f"\nFecthed: {remembered}")
                conversation_context.append({"role": "user", "content": f"Remembered: {remembered}"})

            elif action_content['action'] == 'EXECUTE':
                print(f"\33[0;37m\nExecute: {action_content['info']}\33[0m")
                try:
                    result = eval(action_content['info'])
                    print(f"\nCode Result: {result}")
                    conversation_context.append({"role": "user", "content": result})
                except Exception as e:
                    print(e)

            elif action_content['action'] == 'FINISHED':
                tasks_status[task_id] = str(action_content['info'])
                print(f"\33[32m\nFinished: {action_content['info']}\33[0m")
                running = False
                break
            print('\n-----------------------------------')

        except Exception as e:
            tasks_status[task_id] = "ERRORED"
            print(f"\33[31m\nError: {e}\33[0m")
            raise e


if __name__ == "__main__":
    ## only for testing
    agent_loop(
        service = "Get all Adam's messages",
        data = "",
        task_id="1",
        tasks_status={}
    )
