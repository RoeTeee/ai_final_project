import cv2
import os

def extract_frames_by_timestamps(video_path, output_folder, timestamps):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    video = cv2.VideoCapture(video_path)
    
    if not video.isOpened():
        print(f"Error: Could not open video {video_path}")
        return [None] * len(timestamps)
    
    fps = video.get(cv2.CAP_PROP_FPS)
    duration = video.get(cv2.CAP_PROP_FRAME_COUNT) / fps
    
    print(f"Video FPS: {fps} FPS")
    print(f"Video Duration: {duration:.2f} seconds")
    
    frame_paths = []
    
    for i, timestamp in enumerate(timestamps):
        if not (0 <= timestamp <= duration):
            print(f"Warning: Timestamp {timestamp:.3f}s is out of video duration range, it will be ignored")
            frame_paths.append(None)
            continue
        
        video.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
        
        ret, frame = video.read()
        
        if ret:
            frame_filename = os.path.join(output_folder, f"frame_{timestamp:.3f}s.jpg")
            cv2.imwrite(frame_filename, frame)
            print(f"Extracted frame at {timestamp:.3f}s")
            frame_paths.append(frame_filename)
        else:
            print(f"Error: Could not extract frame at {timestamp:.3f}s")
            frame_paths.append(None)
    
    video.release()
    print(f"Extraction complete. Extracted {len([p for p in frame_paths if p is not None])} frames to {output_folder}")
    
    return frame_paths


if __name__ == "__main__":
    video_path = "data/lecture_0/lecture_0.mp4"
    output_folder = "timestamp_frames"
    
    timestamps = [4*60+18]
    
    extract_frames_by_timestamps(video_path, output_folder, timestamps)
