from .features import extract_features
from .mood_classifier import classify_mood, MoodResult
from pathlib import Path
import librosa
from typing import Union


def is_valid_audio(filepath: Union[str, Path]) -> bool:
    """
    Check if a file is a valid audio file by trying to read a small portion.
    
    Args:
        filepath: Path to the file to validate
        
    Returns:
        bool: True if the file is a valid audio file, False otherwise
    """
    filepath = Path(filepath)
    ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'}
    
    # First check the extension
    if filepath.suffix.lower() not in ALLOWED_EXTENSIONS:
        return False
    
    # Then try to load a small portion to verify it's actually an audio file
    try:
        # Try to load just a small part of the file to verify it's actually audio
        y, sr = librosa.load(str(filepath), duration=1)  # Only load 1 sec to verify
        # If the audio is completely empty or invalid, librosa might return an empty array
        return len(y) > 0
    except Exception:
        # If we can't load it, it's not a valid audio file
        return False


def analyze_audio(audio_path: Union[str, Path], detailed: bool = False, similarity_search: bool = False) -> MoodResult:
    """
    Analyze the mood of an audio file.
    
    Args:
        audio_path: Path to the audio file to analyze
        detailed: Whether to return detailed analysis
        similarity_search: Whether to include similarity scores
    
    Returns:
        MoodResult: Object containing mood analysis results
    """
    # Convert to Path object if needed
    audio_path = Path(audio_path)
    
    # Validate audio file exists
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    # Validate that the file is actually an audio file
    if not is_valid_audio(audio_path):
        raise ValueError(f"Invalid or unsupported audio file: {audio_path}")
    
    # Extract features from the audio
    features = extract_features(str(audio_path))
    
    # Classify the mood
    mood_result = classify_mood(features)
    
    # If detailed analysis is requested, we could add more information here
    if detailed:
        # Add more detailed analysis if needed
        mood_result.explanation += f". Duration: {features['duration']:.2f} seconds"
    
    # If similarity search is requested, ensure similarity scores are included
    if similarity_search and not mood_result.similarity_scores:
        # Recalculate if not already done
        from .mood_classifier import calculate_similarity_scores
        mood_result.similarity_scores = calculate_similarity_scores(features)
    
    return mood_result


def batch_analyze(audio_paths, detailed: bool = False, similarity_search: bool = False):
    """
    Analyze multiple audio files.
    
    Args:
        audio_paths: List of paths to audio files to analyze
        detailed: Whether to return detailed analysis
        similarity_search: Whether to include similarity scores
    
    Returns:
        List[MoodResult]: List of mood analysis results
    """
    results = []
    for path in audio_paths:
        try:
            result = analyze_audio(path, detailed, similarity_search)
            results.append(result)
        except Exception as e:
            # Add error handling for individual files
            print(f"Error analyzing {path}: {str(e)}")
            continue
    
    return results