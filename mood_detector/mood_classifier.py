import numpy as np
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class MoodResult:
    mood: str
    energy: float
    tempo: float
    key: str
    similarity_scores: Dict[str, float]
    explanation: str


def classify_mood(features: Dict) -> MoodResult:
    """Classify the mood of audio based on extracted features."""

    tempo = features['tempo']
    energy = features['energy']
    spectral_centroid = features['spectral_centroid']
    zero_crossing_rate = features['zero_crossing_rate']

    # Advanced mood classification algorithm with spectral features
    mood = detect_mood(energy, tempo, features['chroma'], spectral_centroid, zero_crossing_rate)
    key = determine_key(features['chroma'])

    # Generate similarity scores for related moods
    similarity_scores = calculate_similarity_scores(energy, tempo, spectral_centroid)

    # Create explanation
    explanation = generate_explanation(energy, tempo, spectral_centroid, key)

    return MoodResult(
        mood=mood,
        energy=energy,
        tempo=tempo,
        key=key,
        similarity_scores=similarity_scores,
        explanation=explanation
    )


def detect_mood(energy: float, tempo: float, chroma: List[float], spectral_centroid: float, zero_crossing_rate: float) -> str:
    """
    Advanced mood detection with DJ-relevant categories.
    Uses energy, tempo, brightness (spectral centroid), and timbre (zero crossing rate).
    """

    # Normalize spectral centroid to 0-1 range (typical range is 0-8000 Hz)
    brightness = min(spectral_centroid / 5000.0, 1.0)

    # Determine if major or minor key (affects mood)
    is_major = determine_major_minor(chroma)

    # === CLUB/DANCE MUSIC (110-130 BPM) ===
    if 110 <= tempo <= 130:
        if energy > 0.15 and brightness > 0.5:
            return "House/Dance" if is_major else "Dark House"
        elif energy > 0.12 and brightness > 0.4:
            return "Disco/Funk"
        elif energy > 0.1:
            return "Club/Groovy"

    # === TECHNO/ELECTRONIC (120-145 BPM) ===
    if 120 <= tempo <= 145:
        if energy > 0.15 and brightness < 0.4:
            return "Techno/Dark"
        elif energy > 0.15:
            return "Techno/Industrial"
        elif energy > 0.1:
            return "Driving Electronic"

    # === DRUM & BASS / FAST (160-180 BPM) ===
    if 160 <= tempo <= 180:
        if energy > 0.15:
            return "Drum & Bass"
        elif energy > 0.1:
            return "Breakbeat/Fast"

    # === DOWNTEMPO/CHILL (80-110 BPM) ===
    if 80 <= tempo < 110:
        if energy < 0.08 and brightness < 0.4:
            return "Downtempo/Dark"
        elif energy < 0.1 and brightness > 0.5:
            return "Chill/Bright"
        elif energy < 0.1:
            return "Chill/Groovy"
        elif energy < 0.15:
            return "Midtempo Groove"

    # === AMBIENT/SLOW (< 80 BPM) ===
    if tempo < 80:
        if energy < 0.05:
            return "Ambient/Atmospheric"
        elif energy < 0.08 and not is_major:
            return "Melancholic/Sad"
        elif energy < 0.08:
            return "Downtempo/Relaxed"
        elif energy < 0.12:
            return "Slow Burn"

    # === HIGH ENERGY (> 145 BPM) ===
    if tempo > 145:
        if energy > 0.15:
            return "Hard/Aggressive"
        elif energy > 0.1:
            return "Energetic/Fast"

    # === MODERATE (everything else) ===
    if energy > 0.12:
        return "Moderate Energy"
    elif energy < 0.08:
        return "Low Energy"
    else:
        return "Balanced/Moderate"


def determine_major_minor(chroma_features: List[float]) -> bool:
    """
    Determine if key is major or minor based on chroma distribution.
    Major keys have strong 1st, 3rd (major third), and 5th intervals.
    Minor keys have strong 1st, 3rd (minor third), and 5th intervals.
    Returns True for major, False for minor.
    """
    chroma_array = np.array(chroma_features)
    root_idx = np.argmax(chroma_array)

    # Major third is 4 semitones from root
    major_third_idx = (root_idx + 4) % 12
    # Minor third is 3 semitones from root
    minor_third_idx = (root_idx + 3) % 12

    # Compare strength of major vs minor third
    major_strength = chroma_array[major_third_idx]
    minor_strength = chroma_array[minor_third_idx]

    return major_strength > minor_strength


def determine_key(chroma_features: List[float]) -> str:
    """Determine the musical key based on chroma features."""
    # Find the strongest chroma value
    max_idx = np.argmax(chroma_features)
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    base_note = notes[max_idx]

    # Determine major or minor
    is_major = determine_major_minor(chroma_features)

    return f"{base_note} {'major' if is_major else 'minor'}"


def calculate_similarity_scores(energy: float, tempo: float, brightness: float) -> Dict[str, float]:
    """Calculate similarity scores to reference genres/moods."""
    similarities = {}

    # DJ-relevant reference points
    reference_moods = {
        "House": {"energy": 0.15, "tempo": 125, "brightness": 0.6},
        "Techno": {"energy": 0.16, "tempo": 130, "brightness": 0.4},
        "Disco": {"energy": 0.14, "tempo": 115, "brightness": 0.7},
        "Ambient": {"energy": 0.04, "tempo": 70, "brightness": 0.5},
        "DnB": {"energy": 0.18, "tempo": 170, "brightness": 0.5},
        "Downtempo": {"energy": 0.08, "tempo": 90, "brightness": 0.4}
    }

    # Normalize brightness
    norm_brightness = min(brightness / 5000.0, 1.0)

    for mood, ref in reference_moods.items():
        # Calculate weighted Euclidean distance
        energy_diff = abs(energy - ref["energy"])
        tempo_diff = abs(tempo - ref["tempo"]) / 100  # Normalize tempo
        brightness_diff = abs(norm_brightness - ref["brightness"])

        # Weighted distance (tempo matters most for genre)
        distance = np.sqrt((energy_diff * 2)**2 + (tempo_diff * 3)**2 + (brightness_diff * 1)**2)

        # Convert to similarity (0-1, higher = more similar)
        similarity = max(0.0, 1.0 - (distance / 3.0))
        similarities[mood] = round(similarity, 2)

    return similarities


def generate_explanation(energy: float, tempo: float, brightness: float, key: str) -> str:
    """Generate detailed explanation of the mood analysis."""

    # Normalize brightness
    norm_brightness = min(brightness / 5000.0, 1.0)

    # Energy description
    if energy < 0.05:
        energy_desc = "very low"
    elif energy < 0.1:
        energy_desc = "low"
    elif energy < 0.15:
        energy_desc = "moderate"
    elif energy < 0.2:
        energy_desc = "high"
    else:
        energy_desc = "very high"

    # Brightness description
    if norm_brightness < 0.3:
        bright_desc = "dark/mellow"
    elif norm_brightness < 0.6:
        bright_desc = "balanced"
    else:
        bright_desc = "bright/sharp"

    # Tempo description
    if tempo < 80:
        tempo_desc = "slow"
    elif tempo < 110:
        tempo_desc = "moderate"
    elif tempo < 130:
        tempo_desc = "dance"
    elif tempo < 150:
        tempo_desc = "fast"
    else:
        tempo_desc = "very fast"

    return (f"{energy_desc.capitalize()} energy ({energy:.3f}), "
            f"{tempo_desc} tempo ({tempo:.1f} BPM), "
            f"{bright_desc} timbre, "
            f"key of {key}")