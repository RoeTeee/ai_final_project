import time
import gradio as gr
from openai import OpenAI
import query
import yaml
from config import config

client = OpenAI(
    api_key=config.api_key,
    base_url=config.base_url,
)

def get_text_embedding(text):
    if not text:
        return None
    
    try:
        completion = client.embeddings.create(
            model=config.embed_model,
            input=text,
            dimensions=1024,
            encoding_format="float"
        )
        return completion.data[0].embedding
    except Exception as e:
        print(f"Error getting text embedding: {e}")
        return None

def chat(message, history):
    query_embed = get_text_embedding(message)
    query_vector = query_embed
    distances, indices, frames = query.search_similar_frames(query_vector, num_results=3)

    prompt = '''
    Use the following context information to answer the question at the end. If the context information is not sufficient to answer the question, please indicate that you cannot find relevant information.

    Context information:
    {context}

    Question:
    {question}

    Answer:
    '''
    context = ''
    for i in indices[0]:
        data = {
            'video_id': frames[i]['video_id'],
            'subtitle_start_time': frames[i]['subtitle_start_time'],
            'subtitle_end_time': frames[i]['subtitle_end_time'],
            'subtitle_text': frames[i]['subtitle_text']
        }
        yaml_str = yaml.dump(data, default_flow_style=False, allow_unicode=True)
        context += yaml_str + '\n'
    prompt = prompt.replace('{context}', context).replace('{question}', message)

    history.append({'role': 'user', 'content': prompt})
    completion = client.chat.completions.create(
        model=config.llm_model,
        messages=history,
        stream=True,
        stream_options={"include_usage": True}
    )
    s = ''
    for chunk in completion:
        if len(chunk.choices)>0:
            s += chunk.choices[0].delta.content
            yield s

gr.ChatInterface(
    fn=chat, 
    type="messages"
).launch()