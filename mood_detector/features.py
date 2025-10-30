import librosa
import numpy as np
from typing import Dict, List, Tuple


def extract_tempo(y: np.ndarray, sr: int) -> float:
    """Extract tempo (BPM) from audio signal."""
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return float(tempo)


def extract_energy(y: np.ndarray) -> float:
    """Extract energy level from audio signal (normalized 0-1)."""
    # Calculate root mean square (RMS) energy
    rms = librosa.feature.rms(y=y)[0]
    # Normalize to 0-1 range
    energy = float(np.mean(rms))
    # Clip to ensure it's in valid range
    return min(max(energy, 0.0), 1.0)


def extract_spectral_centroid(y: np.ndarray, sr: int) -> float:
    """Extract spectral centroid (brightness) from audio signal."""
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    return float(np.mean(spectral_centroids))


def extract_spectral_rolloff(y: np.ndarray, sr: int) -> float:
    """Extract spectral rolloff from audio signal."""
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    return float(np.mean(spectral_rolloff))


def extract_zero_crossing_rate(y: np.ndarray) -> float:
    """Extract zero crossing rate from audio signal."""
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    return float(np.mean(zcr))


def extract_mfccs(y: np.ndarray, sr: int, n_mfcc: int = 13) -> List[float]:
    """Extract MFCCs (Mel-frequency cepstral coefficients) from audio signal."""
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    # Return mean of each MFCC coefficient
    return [float(np.mean(mfccs[i])) for i in range(n_mfcc)]


def extract_chroma(y: np.ndarray, sr: int, n_chroma: int = 12) -> List[float]:
    """Extract chroma features from audio signal."""
    chroma = librosa.feature.chroma_stft(y=y, sr=sr, n_chroma=n_chroma)
    # Return mean of each chroma coefficient
    return [float(np.mean(chroma[i])) for i in range(n_chroma)]


def extract_features(audio_path: str) -> Dict:
    """Extract all relevant features from an audio file."""
    # Load the audio file
    y, sr = librosa.load(audio_path, duration=30)  # Limit to first 30 seconds
    
    # Extract various features
    features = {
        'tempo': extract_tempo(y, sr),
        'energy': extract_energy(y),
        'spectral_centroid': extract_spectral_centroid(y, sr),
        'spectral_rolloff': extract_spectral_rolloff(y, sr),
        'zero_crossing_rate': extract_zero_crossing_rate(y),
        'mfccs': extract_mfccs(y, sr),
        'chroma': extract_chroma(y, sr),
        'sample_rate': sr,
        'duration': librosa.get_duration(y=y, sr=sr)
    }
    
    return features