import numpy as np
import cv2
import os
from typing import List, Tuple, Dict, Optional
import re

def interpolate_temperatures(start_temp: float, end_temp: float, frame_count: int) -> List[float]:
    """
    Linearly interpolate temperatures between start and end temperatures.
    
    Args:
        start_temp: Starting temperature in Celsius
        end_temp: Ending temperature in Celsius
        frame_count: Number of frames to generate temperatures for
    
    Returns:
        List of interpolated temperatures
    """
    if frame_count <= 0:
        return []
    
    if start_temp == end_temp:
        # If temperatures are the same, assign all frames that value
        return [start_temp] * frame_count
    
    # Linear interpolation
    temperatures = np.linspace(start_temp, end_temp, frame_count)
    return temperatures.tolist()

def extract_frames_from_video(video_path: str, frame_count: Optional[int] = None, 
                            frame_interval: Optional[int] = None) -> List[np.ndarray]:
    """
    Extract frames from a video file.
    
    Args:
        video_path: Path to the video file
        frame_count: Number of frames to extract (if None, extract all)
        frame_interval: Extract every Nth frame (if None, extract all)
    
    Returns:
        List of frame arrays
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    frames = []
    frame_idx = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Apply frame interval if specified
        if frame_interval is not None and frame_idx % frame_interval != 0:
            frame_idx += 1
            continue
        
        frames.append(frame)
        frame_idx += 1
        
        # Stop if we have enough frames
        if frame_count is not None and len(frames) >= frame_count:
            break
    
    cap.release()
    return frames

def process_video_with_temperature_range(video_path: str, start_temp: float, end_temp: float,
                                       frame_count: Optional[int] = None,
                                       frame_interval: Optional[int] = None) -> Tuple[List[np.ndarray], List[float]]:
    """
    Extract frames from video and assign interpolated temperatures.
    
    Args:
        video_path: Path to the video file
        start_temp: Starting temperature in Celsius
        end_temp: Ending temperature in Celsius
        frame_count: Number of frames to extract
        frame_interval: Extract every Nth frame
    
    Returns:
        Tuple of (frames, temperatures)
    """
    frames = extract_frames_from_video(video_path, frame_count, frame_interval)
    
    if not frames:
        raise ValueError("No frames extracted from video")
    
    # Interpolate temperatures for the extracted frames
    temperatures = interpolate_temperatures(start_temp, end_temp, len(frames))
    
    return frames, temperatures

def save_frames_with_temperatures(frames: List[np.ndarray], temperatures: List[float], 
                                output_folder: str) -> List[str]:
    """
    Save frames to disk with temperature information in filenames.
    
    Args:
        frames: List of frame arrays
        temperatures: List of temperature values
        output_folder: Folder to save frames in
    
    Returns:
        List of saved file paths
    """
    saved_files = []
    
    for idx, (frame, temp) in enumerate(zip(frames, temperatures)):
        # Create filename with temperature information
        filename = f"frame_{idx+1:03d}_{temp:.1f}C.jpg"
        filepath = os.path.join(output_folder, filename)
        
        # Save frame
        cv2.imwrite(filepath, frame)
        saved_files.append(filepath)
    
    return saved_files

def process_batch_images_with_temperature_range(image_folder: str, start_temp: float, 
                                             end_temp: float) -> List[str]:
    """
    Process batch images and assign interpolated temperatures.
    
    Args:
        image_folder: Folder containing images
        start_temp: Starting temperature in Celsius
        end_temp: Ending temperature in Celsius
    
    Returns:
        List of file paths with temperature information
    """
    # Get all image files
    image_files = sorted([
        f for f in os.listdir(image_folder)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ])
    
    if not image_files:
        raise ValueError("No image files found in folder")
    
    # Interpolate temperatures
    temperatures = interpolate_temperatures(start_temp, end_temp, len(image_files))
    
    # Rename files with temperature information
    renamed_files = []
    
    for idx, (filename, temp) in enumerate(zip(image_files, temperatures)):
        # Get file extension
        name, ext = os.path.splitext(filename)
        
        # Create new filename with temperature
        new_filename = f"{name}_{temp:.1f}C{ext}"
        old_path = os.path.join(image_folder, filename)
        new_path = os.path.join(image_folder, new_filename)
        
        # Rename file
        os.rename(old_path, new_path)
        renamed_files.append(new_path)
    
    return renamed_files

def extract_temperature_from_filename(filename: str) -> Optional[float]:
    """
    Extract temperature from filename that contains temperature information.
    
    Args:
        filename: Filename that may contain temperature info
    
    Returns:
        Temperature value if found, None otherwise
    """
    # Look for temperature patterns like "118.2C", "117.3C", etc.
    match = re.search(r'(\d+\.\d+|\d+)C', filename)
    if match:
        return float(match.group(1))
    return None

def validate_temperature_range(start_temp: float, end_temp: float) -> bool:
    """
    Validate temperature range parameters.
    
    Args:
        start_temp: Starting temperature
        end_temp: Ending temperature
    
    Returns:
        True if valid, False otherwise
    """
    # Basic validation
    if start_temp < -273.15 or end_temp < -273.15:  # Below absolute zero
        return False
    
    if start_temp > 1000 or end_temp > 1000:  # Unreasonably high
        return False
    
    return True

def get_default_frame_count(video_path: str) -> int:
    """
    Get default frame count for video analysis.
    
    Args:
        video_path: Path to video file
    
    Returns:
        Default number of frames to extract
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 30  # Default fallback
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    
    # Return reasonable default based on video length
    if total_frames <= 30:
        return total_frames
    elif total_frames <= 300:
        return min(30, total_frames)
    else:
        return min(50, total_frames)
