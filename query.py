from pymongo import MongoClient
import numpy as np
import faiss
from config import Config

config = Config()

MONGO_URI = config.mongo_uri
DB_NAME = config.db_name
COLLECTION_NAME = config.collection_name

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


def query_frames_by_video_id(video_id):
    """
    Queries all related frame data by video ID.

    Args:
        video_id (str): Unique identifier for the video.

    Returns:
        list: List of query results.
    """
    query = {'video_id': video_id}
    results = collection.find(query)
    return list(results)


def get_all_video_ids():
    """
    Retrieves all unique video IDs.

    Returns:
        list: List containing all unique video_ids.
    """
    return collection.distinct('video_id')


def clear_collection():
    """
    Clears all documents in the collection.

    Returns:
        int: Number of deleted documents.
    """
    result = collection.delete_many({})
    return result.deleted_count


def search_similar_frames(query_vector, num_results=3, video_id=None):
    if not isinstance(query_vector, np.ndarray):
        query_vector = np.array([query_vector])
    
    if len(query_vector.shape) == 1:
        query_vector = query_vector.reshape(1, -1)
    
    embed_data = []
    frames = []
    
    if video_id:
        frames = query_frames_by_video_id(video_id)
    else:
        frames = list(collection.find({}))
    
    if not frames:
        return np.array([]), np.array([]), []
    
    for frame in frames:
        embed_data.append(frame['text_embedding'])
    
    vector_dim = len(embed_data[0])
    index = faiss.IndexFlatL2(vector_dim)
    index.add(np.array(embed_data))
    
    distances, indices = index.search(query_vector, min(num_results, len(embed_data)))
    return distances, indices, frames


if __name__ == "__main__":
    # clear_collection()
    
    video_ids = get_all_video_ids()
    print("List of Video IDs:", video_ids)
    
    query_vector = np.zeros((1, 1024))
    distances, indices, frames = search_similar_frames(query_vector, num_results=3)
    
    print("Nearest neighbor indices for the query vector:\n", indices)
    print("Nearest neighbor distances for the query vector:\n", distances)
    
    for i in indices[0]:
        print('ID:', frames[i]['subtitle_text'])