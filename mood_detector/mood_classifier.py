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
    tempo_confidence = features.get('tempo_confidence', 1.0)
    energy = features['energy']
    spectral_centroid = features['spectral_centroid']
    zero_crossing_rate = features['zero_crossing_rate']

    # Advanced mood classification algorithm with spectral features
    mood = detect_mood(energy, tempo, tempo_confidence, features['chroma'], spectral_centroid, zero_crossing_rate)
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


def detect_mood(energy: float, tempo: float, tempo_confidence: float, chroma: List[float], spectral_centroid: float, zero_crossing_rate: float) -> str:
    """
    Advanced mood detection with DJ-relevant categories.
    Uses energy, tempo, brightness (spectral centroid), and timbre (zero crossing rate).
    Tempo confidence helps identify drones/ambient (which have unreliable tempo detection).
    """

    # Normalize spectral centroid to 0-1 range (typical range is 0-8000 Hz)
    brightness = min(spectral_centroid / 5000.0, 1.0)

    # Determine if major or minor key (affects mood)
    is_major = determine_major_minor(chroma)

    # === DRONES/AMBIENT (Very low tempo confidence = no clear beat) ===
    # Binaural beats, sine waves, drones have unreliable tempo detection
    if tempo_confidence < 0.1:
        if energy < 0.15:
            return "Ambient/Drone"
        elif energy < 0.25:
            return "Atmospheric/Textural"
        else:
            return "Noise/Experimental"

    # === EXPERIMENTAL/NOISE (High zero-crossing rate = lots of high-freq noise/chaos) ===
    # Catches glitchy experimental tracks
    if zero_crossing_rate > 0.15:
        if energy > 0.3:
            return "Harsh Noise/Experimental"
        else:
            return "Glitch/Experimental"

    # === AMBIENT/ATMOSPHERIC (Very low energy) ===
    if energy < 0.2:
        if tempo < 70:
            if energy < 0.1:
                return "Ambient/Atmospheric"
            elif not is_major:
                return "Melancholic/Sad"
            else:
                return "Downtempo/Relaxed"
        elif 70 <= tempo < 100:
            if energy < 0.1 and brightness < 0.4:
                return "Downtempo/Dark"
            elif energy < 0.12:
                return "Ambient/Chill"
            else:
                return "Midtempo Groove"
        elif tempo < 130:
            # Moderate tempo but very low energy = probably drone/pad, not club
            if energy < 0.12:
                return "Atmospheric Pad"
            else:
                return "Minimal/Sparse"
        else:
            # High tempo but low energy = experimental/glitch
            return "Experimental/Glitch"

    # === CLUB/DANCE MUSIC (110-130 BPM, moderate-high energy) ===
    if 110 <= tempo <= 130 and energy >= 0.3:
        if brightness > 0.5:
            return "House/Dance" if is_major else "Dark House"
        elif brightness > 0.4:
            return "Disco/Funk"
        else:
            return "Club/Groovy"

    # === TECHNO/ELECTRONIC (120-145 BPM, high energy) ===
    if 120 <= tempo <= 145 and energy >= 0.35:
        if brightness < 0.4:
            return "Techno/Dark"
        else:
            return "Techno/Industrial"

    # === DRUM & BASS / FAST (160-180 BPM) ===
    if 160 <= tempo <= 180:
        if energy > 0.4:
            return "Drum & Bass"
        elif energy > 0.25:
            return "Breakbeat/Fast"
        else:
            return "Fast/Atmospheric"

    # === HIGH ENERGY RAVE/HARD (> 145 BPM or very high energy) ===
    if tempo > 145 or energy > 0.5:
        if energy > 0.6:
            return "Hard/Aggressive"
        elif energy > 0.4:
            return "Energetic/Rave"
        else:
            return "Driving Electronic"

    # === MODERATE ENERGY (Fallback) ===
    if energy >= 0.25:
        if tempo > 100:
            return "Upbeat/Moderate"
        else:
            return "Moderate Groove"
    elif energy >= 0.15:
        return "Relaxed/Moderate"
    else:
        return "Low Energy"


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
    if energy < 0.1:
        energy_desc = "very low"
    elif energy < 0.2:
        energy_desc = "low"
    elif energy < 0.35:
        energy_desc = "moderate"
    elif energy < 0.5:
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