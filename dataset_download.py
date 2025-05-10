import os
import json
from datasets import load_dataset
from huggingface_hub import login
from config import config

hf_token = config.hf_token
if not hf_token:
    raise ValueError("Hugging Face token not found in config. Please add 'hf_token' to your config file.")

login(hf_token)

dataset_name = config.get("dataset_name", "aegean-ai/ai-lectures-spring-24")
data_dir = config.get("data_dir", "data")

dataset = load_dataset(dataset_name)

os.makedirs(data_dir, exist_ok=True)

train_dataset = dataset['train']

for i, example in enumerate(train_dataset):
    lecture_folder = os.path.join(data_dir, f"lecture_{i}")
    os.makedirs(lecture_folder, exist_ok=True)
    
    print(f"Processing lecture {i}...")
    
    if 'mp4' in example:
        with open(os.path.join(lecture_folder, f"lecture_{i}.mp4"), 'wb') as f:
            f.write(example['mp4'])
    
    if 'en.vtt' in example:
        with open(os.path.join(lecture_folder, f"lecture_{i}_en.vtt"), 'w', encoding='utf-8') as f:
            f.write(example['en.vtt'].decode('utf-8'))
    
    if 'info.json' in example:
        with open(os.path.join(lecture_folder, f"info.json"), 'w', encoding='utf-8') as f:
            json.dump(example['info.json'], f, indent=4)
    
    if 'json' in example:
        with open(os.path.join(lecture_folder, f"data.json"), 'w', encoding='utf-8') as f:
            json.dump(example['json'], f, indent=4)

print(f"All data saved to '{data_dir}' folder.")