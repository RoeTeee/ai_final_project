import vtt
import video
from pymongo import MongoClient
import gridfs
from PIL import Image
import io
import os
import numpy as np
from openai import OpenAI
from config import config  # 导入配置模块

def setup_mongodb():
    client = MongoClient(config.mongo_uri)
    db = client[config.db_name]
    collection = db[config.collection_name]
    fs = gridfs.GridFS(db)
    return db, collection, fs

def setup_vector_index():
    client = MongoClient(config.mongo_uri)
    db = client[config.db_name]
    collection = db[config.collection_name]
    
    index_definition = {
        'mappings': {
            'dynamic': True,
            'fields': {
                'text_embedding': {
                    'dimensions': 1024,
                    'similarity': 'cosine',
                    'type': 'knnVector'
                }
            }
        }
    }
    
    collection.create_index([('text_embedding', 'vector')], **index_definition)
    print("Vector index created")

def setup_embedding_client():
    client = OpenAI(
        api_key=config.api_key,
        base_url=config.base_url
    )
    return client

def get_text_embedding(client, text):
    if not text:
        return None
    
    try:
        completion = client.embeddings.create(
            model=config.embed_model,  # 使用配置或默认值
            input=text,
            dimensions=1024,
            encoding_format="float"
        )
        return completion.data[0].embedding
    except Exception as e:
        print(f"Error getting text embedding: {e}")
        return None

def insert_video_frame(collection, fs, video_id, frame_index, timestamp, image_path, 
                      subtitle_text=None, subtitle_start_time=None, subtitle_end_time=None, metadata=None,
                      embedding_client=None):
    try:
        img = Image.open(image_path)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_data = img_bytes.getvalue()
        
        image_id = fs.put(img_data, filename=f"{video_id}_{frame_index}.jpg")
        
        text_embedding = None
        if subtitle_text and embedding_client:
            text_embedding = get_text_embedding(embedding_client, subtitle_text)
        
        document = {
            'video_id': video_id,
            'frame_index': frame_index,
            'timestamp': timestamp,
            'image_id': image_id,
            'subtitle_text': subtitle_text,
            'subtitle_start_time': subtitle_start_time,
            'subtitle_end_time': subtitle_end_time,
            'text_embedding': text_embedding,
            'metadata': metadata or {}
        }
        
        result = collection.insert_one(document)
        return result.inserted_id
    except Exception as e:
        print(f"Error inserting frame: {e}")
        return None

def process_video_with_subtitles(vtt_file_path, video_path, output_folder, video_id):
    db, collection, fs = setup_mongodb()
    
    embedding_client = setup_embedding_client()
    
    captions = vtt.parse_vtt_file(vtt_file_path)
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    timestamps = []
    for cap in captions:
        timestamps.append(vtt.format_time(cap.start_time))
    
    frame_paths = video.extract_frames_by_timestamps(video_path, output_folder, timestamps)
    
    inserted_count = 0
    for i, (timestamp, frame_path) in enumerate(zip(timestamps, frame_paths)):
        if frame_path and os.path.exists(frame_path):
            caption = captions[i]
            
            inserted_id = insert_video_frame(
                collection, 
                fs,
                video_id=video_id,
                frame_index=i,
                timestamp=timestamp,
                image_path=frame_path,
                subtitle_text=caption.text,
                subtitle_start_time=caption.start_time,
                subtitle_end_time=caption.end_time,
                metadata={"source_file": os.path.basename(video_path)},
                embedding_client=embedding_client
            )
            
            if inserted_id:
                inserted_count += 1
                print(f"Successfully inserted frame {i} to MongoDB, ID: {inserted_id}")
    
    print(f"Processed {len(timestamps)} frames, successfully inserted {inserted_count} frames to MongoDB")
    return inserted_count

if __name__ == "__main__":
    data_dir = "data"
    
    for item in os.listdir(data_dir):
        item_path = os.path.join(data_dir, item)
        
        if os.path.isdir(item_path):
            vtt_file_path = os.path.join(item_path, f"{item}_en.vtt")
            video_path = os.path.join(item_path, f"{item}.mp4")
            output_folder = f"timestamp_frames_{item}"
            
            if os.path.exists(vtt_file_path) and os.path.exists(video_path):
                video_id = f"video_{item}"
                
                process_video_with_subtitles(vtt_file_path, video_path, output_folder, video_id)
            else:
                print(f"Skipping {item}: vtt or mp4 file missing.")
