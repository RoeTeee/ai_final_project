# RAG Video QA System

## Project Overview
This project is a video question-answering system based on RAG (Retrieval-Augmented Generation) technology. By extracting video content, including video frames and subtitles, and storing them as vectors in a database, users can interact with video content through natural language queries.

## Features
- Automatic extraction and processing of video content
- Subtitle parsing and analysis
- Keyframe capture from videos
- Vectorized storage and retrieval
- Natural language-based intelligent Q&A

## Installation and Environment Setup

### Dependencies
```bash
pip install -r requirements.txt
```

### Environment Requirements
- Python 3.8+
- MongoDB
- CUDA support (optional, for accelerating vector computations)

## Usage

### Data Preparation
1. Download the sample dataset using `dataset_download.py`:
```bash
python dataset_download.py
```

### Data Processing Workflow
1. Process and store data:
```bash
python etl.py
```

### Q&A Query
Use the chat interface for interaction:
```bash
python chat.py
```

## Code Files
- `vtt.py`: Processes video subtitle files, extracting text content and timestamp information
- `video.py`: Video frame extraction tool, captures keyframes at specified intervals
- `etl.py`: Data processing pipeline, responsible for reading, vectorizing text and image data, and writing to MongoDB
- `dataset_download.py`: Script for downloading the sample dataset
- `query.py`: Vector database query testing tool, used to verify retrieval functionality
- `demonstration.ipynb`: Complete workflow demonstration notebook, covering all steps from data processing to querying
- `chat.py`: Interactive chat interface that allows users to interact with the system using natural language

## Project Structure
```
RAG/
├── data/              # Data storage directory
├── vtt.py             # Subtitle processing
├── video.py           # Video frame processing
├── etl.py             # Data processing pipeline
├── dataset_download.py # Dataset download
├── query.py           # Query testing
├── chat.py            # Chat interface
└── demonstration.ipynb # Demonstration notebook
```