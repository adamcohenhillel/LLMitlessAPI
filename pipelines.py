"""Deeper 2022, All Rights Reserved
"""
from tasks.openai import create_context, generate_readme, add_embeddings_to_dataframe
from tasks.tasks import load_text_from_path


async def process_project(path: str) -> None:
    """
    """
    questions = [  # Need to be modified by user/automatically generated?
        "How the authentication works?",
        "How to add a new page?",
        "How the insights page works?"
    ]
    data_frame = load_text_from_path(path)
    data_frame = add_embeddings_to_dataframe(data_frame)
    for question in questions:
        context = create_context(question, data_frame)
        readme = generate_readme(question, context)
        print('************************************************************')
        print(readme)