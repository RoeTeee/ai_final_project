import re
from dataclasses import dataclass
from typing import List


@dataclass
class Caption:
    start_time: str
    end_time: str
    text: str


def parse_vtt_file(file_path: str) -> List[Caption]:
    captions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        if not content.strip().startswith('WEBVTT'):
            print("Error: This is not a valid WebVTT file")
            return []
        
        time_pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})'
        matches = re.finditer(time_pattern, content)
        
        for match in matches:
            start_time = match.group(1)
            end_time = match.group(2)
            
            start_pos = match.end()
            next_match = re.search(time_pattern, content[start_pos:])
            
            if next_match:
                text_content = content[start_pos:start_pos + next_match.start()]
            else:
                text_content = content[start_pos:]
            
            text_content = text_content.strip()
            
            caption = Caption(start_time, end_time, text_content)
            captions.append(caption)
        
        return captions
    
    except Exception as e:
        print(f"Error parsing VTT file: {e}")
        return []


def format_time(time_str: str) -> float:
    h, m, s = time_str.split(':')
    hours = int(h)
    minutes = int(m)
    seconds = float(s)
    return hours * 3600 + minutes * 60 + seconds


def display_captions(captions: List[Caption]) -> None:
    print(f"Found {len(captions)} captions\n")
    
    for i, cap in enumerate(captions, 1):
        print(f"Caption #{i}")
        print(f"Time: {cap.start_time} --> {cap.end_time}")
        print(f"Duration: {format_time(cap.end_time) - format_time(cap.start_time):.3f} seconds")
        print(f"Content: {cap.text}")
        print("-" * 50)


if __name__ == "__main__":
    vtt_file_path = "data/lecture_0/lecture_0_en.vtt"
    
    captions = parse_vtt_file(vtt_file_path)
    
    if captions:
        display_captions(captions)
        
        with open("extracted_subtitles.txt", "w", encoding="utf-8") as out_file:
            for cap in captions:
                out_file.write(f"[{cap.start_time} --> {cap.end_time}]\n{cap.text}\n\n")
        
        print("Subtitles saved to extracted_subtitles.txt")
