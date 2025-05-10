from pymongo import MongoClient
import gridfs
from PIL import Image
import io
from config import Config

config = Config()

client = MongoClient(config.mongo_uri)
db = client[config.db_name]
collection = db[config.collection_name]
fs = gridfs.GridFS(db)

def insert_video_frame(video_id, frame_index, timestamp, image, subtitle_text=None, 
                      subtitle_start_time=None, subtitle_end_time=None, metadata=None):
    """
    Inserts video frame data into MongoDB.
    
    Args:
    - video_id: Unique identifier for the video.
    - frame_index: Index of the frame in the original video.
    - timestamp: Timestamp of the frame in seconds.
    - image: PIL Image object or image path.
    - subtitle_text: Subtitle text corresponding to the frame.
    - subtitle_start_time: Subtitle start time.
    - subtitle_end_time: Subtitle end time.
    - metadata: Additional metadata dictionary.
    """
    # Convert image data to binary
    if isinstance(image, str):
        img = Image.open(image)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_data = img_bytes.getvalue()
    else:
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_data = img_bytes.getvalue()
    
    # Store image data in GridFS
    image_id = fs.put(img_data, filename=f"{video_id}_{frame_index}.jpg")
    
    # Create document
    document = {
        'video_id': video_id,
        'frame_index': frame_index,
        'timestamp': timestamp,
        'image_id': image_id,
        'subtitle_text': subtitle_text,
        'subtitle_start_time': subtitle_start_time,
        'subtitle_end_time': subtitle_end_time,
        'metadata': metadata or {}
    }
    
    return document

def batch_insert_frames(frames_data):
    """
    Batch insert multiple video frame data.
    
    Args:
    - frames_data: List containing multiple frame data, each element is a dictionary.
    """
    documents = []
    
    for frame in frames_data:
        doc = insert_video_frame(
            video_id=frame['video_id'],
            frame_index=frame['frame_index'],
            timestamp=frame['timestamp'],
            image=frame['image'],
            subtitle_text=frame.get('subtitle_text'),
            subtitle_start_time=frame.get('subtitle_start_time'),
            subtitle_end_time=frame.get('subtitle_end_time'),
            metadata=frame.get('metadata')
        )
        documents.append(doc)
    
    if documents:
        result = collection.insert_many(documents)
        return result.inserted_ids
    return []

def query_frames_by_video_id(video_id):
    """
    Query all related frame data by video ID.

    Args:
    - video_id: Unique identifier for the video.

    Returns:
    - List of query results.
    """
    query = {'video_id': video_id}
    results = collection.find(query)
    return list(results)

def get_all_video_ids():
    """
    Get all unique video IDs.

    Returns:
    - List containing all unique video_id.
    """
    video_ids = collection.distinct('video_id')
    return video_ids

if __name__ == "__main__":
    video_ids = get_all_video_ids()
    print("List of video IDs:", video_ids)
    video_id = 'video_lecture_0'
    frames = query_frames_by_video_id(video_id)
    for frame in frames:
        print(frame.keys())