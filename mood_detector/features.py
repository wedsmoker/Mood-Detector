import librosa
import numpy as np
from typing import Dict, List, Tuple


def extract_tempo(y: np.ndarray, sr: int) -> tuple:
    """Extract tempo (BPM) and confidence from audio signal."""
    try:
        # Use onset detection for better ambient/drone handling
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)

        # Convert tempo to scalar (librosa 0.11.0 returns array)
        tempo = float(np.atleast_1d(tempo)[0])

        # Calculate confidence based on beat strength variance
        # Low variance = likely not rhythmic (ambient/drone)
        beat_strength_variance = float(np.var(onset_env))

        # If very low variance, it's probably ambient (no clear beats)
        if beat_strength_variance < 0.01:
            # Return a safe "ambient" tempo
            return 60.0, beat_strength_variance

        # Check for half-tempo detection (common issue with fast electronic music)
        # If tempo is in the range where doubling would make more sense (80-140 BPM)
        # and the track has characteristics of fast music, double it
        # This will be refined later based on energy and other features
        # For now, just return the detected tempo - we'll handle doubling in classification

        return float(tempo), beat_strength_variance
    except Exception as e:
        # Fallback if beat detection fails
        print(f"Warning: Tempo detection failed: {e}")
        return 60.0, 0.0


def extract_energy(y: np.ndarray) -> float:
    """Extract energy level from audio signal (normalized 0-1)."""
    # Calculate root mean square (RMS) energy
    rms = librosa.feature.rms(y=y)[0]
    # Get mean RMS (typically 0.0-0.3 range for music)
    mean_rms = float(np.mean(rms))

    # Scale to 0-1 range
    # Most music falls in 0.05-0.3 RMS range
    # Scale by 2.5x to spread it to ~0.125-0.75 range
    energy = mean_rms * 2.5

    # Clip to ensure it's in valid 0-1 range
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
    # Get total duration first
    total_duration = librosa.get_duration(path=audio_path)

    # Load from middle of track (skip intro, get the "meat")
    # Use longer duration (30s) for better tempo detection accuracy
    if total_duration > 60:
        offset = 30.0
        duration = 30.0  # Analyze 30 seconds from the middle (increased from 15s)
    elif total_duration > 30:
        offset = total_duration * 0.25
        duration = min(30.0, total_duration - offset)
    else:
        offset = 0
        duration = min(30.0, total_duration)

    # Load the audio file from calculated offset
    y, sr = librosa.load(audio_path, offset=offset, duration=duration)

    # Extract tempo and confidence
    tempo, tempo_confidence = extract_tempo(y, sr)

    # Extract various features
    features = {
        'tempo': tempo,
        'tempo_confidence': tempo_confidence,
        'energy': extract_energy(y),
        'spectral_centroid': extract_spectral_centroid(y, sr),
        'spectral_rolloff': extract_spectral_rolloff(y, sr),
        'zero_crossing_rate': extract_zero_crossing_rate(y),
        'mfccs': extract_mfccs(y, sr),
        'chroma': extract_chroma(y, sr),
        'sample_rate': sr,
        'duration': total_duration
    }

    return features