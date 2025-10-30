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
    # detect_mood may adjust tempo for half-tempo detection, so we capture both
    mood, corrected_tempo = detect_mood(energy, tempo, tempo_confidence, features['chroma'], spectral_centroid, zero_crossing_rate)
    key = determine_key(features['chroma'])

    # Generate similarity scores for related moods (use corrected tempo)
    similarity_scores = calculate_similarity_scores(energy, corrected_tempo, spectral_centroid)

    # Create explanation (use corrected tempo)
    explanation = generate_explanation(energy, corrected_tempo, spectral_centroid, key)

    return MoodResult(
        mood=mood,
        energy=energy,
        tempo=corrected_tempo,  # Use corrected tempo
        key=key,
        similarity_scores=similarity_scores,
        explanation=explanation
    )


def detect_mood(energy: float, tempo: float, tempo_confidence: float, chroma: List[float], spectral_centroid: float, zero_crossing_rate: float) -> tuple:
    """
    Advanced mood detection with DJ-relevant categories.
    Uses energy, tempo, brightness (spectral centroid), and timbre (zero crossing rate).
    Tempo confidence helps identify drones/ambient (which have unreliable tempo detection).

    Returns:
        tuple: (mood_string, corrected_tempo)
    """

    # Normalize spectral centroid to 0-1 range (typical range is 0-8000 Hz)
    brightness = min(spectral_centroid / 5000.0, 1.0)

    # Determine if major or minor key (affects mood)
    is_major = determine_major_minor(chroma)

    # === HALF-TEMPO DETECTION ===
    # Fast electronic music (techno, DnB, etc.) is often detected at half-tempo
    # If tempo is 80-145 BPM with very high energy (>0.8), it's likely half-tempo
    # Double the tempo for more accurate genre classification
    if 80 <= tempo <= 145 and energy > 0.8:
        tempo = tempo * 2.0

    # === DRONES/AMBIENT (Very low tempo confidence = no clear beat) ===
    # Binaural beats, sine waves, drones have unreliable tempo detection
    # Increased threshold from 0.1 to 0.2 for better detection
    if tempo_confidence < 0.2:
        if energy < 0.15:
            return ("Ambient/Drone", tempo)
        elif energy < 0.30:
            return ("Atmospheric/Textural", tempo)
        elif energy < 0.50:
            return ("Atmospheric/Textural", tempo)  # Medium energy drones
        elif energy < 0.70:
            # High energy but no beat = droning noise
            return ("Atmospheric/Textural" if brightness < 0.3 else "Noise/Experimental", tempo)
        else:
            return ("Harsh Noise/Experimental", tempo)

    # === EXPERIMENTAL/NOISE (High zero-crossing rate = lots of high-freq noise/chaos) ===
    # Catches glitchy experimental tracks
    # Increased threshold from 0.15 to 0.25 to avoid false positives with normal music
    # Most regular music has ZCR between 0.08-0.22
    if zero_crossing_rate > 0.25:
        if energy > 0.3:
            return ("Harsh Noise/Experimental", tempo)
        else:
            return ("Glitch/Experimental", tempo)

    # === TECHNO/ELECTRONIC (120-145 BPM, high energy) ===
    # Check techno before club/dance to prioritize high-energy tracks
    # Lowered energy threshold from 0.35 to 0.30 for better techno detection
    if 120 <= tempo <= 145 and energy >= 0.50:
        if brightness < 0.4:
            return ("Techno/Dark", tempo)
        else:
            return ("Techno/Industrial", tempo)

    # === CLUB/DANCE MUSIC (100-130 BPM, moderate-high energy) ===
    # Lowered energy threshold from 0.3 to 0.15 to catch more house music
    # Extended tempo range from 110-130 to 100-130 to include disco tracks
    if 100 <= tempo <= 130 and energy >= 0.15:
        # Very high energy (>0.7) in this tempo range = energetic techno/house
        if energy > 0.7:
            if 115 <= tempo <= 130:
                return ("Techno/Industrial" if brightness > 0.5 else "Techno/Dark", tempo)
            else:
                return ("Energetic/Rave", tempo)
        # Disco typically 100-115 BPM with moderate energy
        elif 100 <= tempo <= 115 and energy < 0.5:
            return ("Disco/Funk", tempo)
        elif brightness > 0.5:
            return ("House/Dance" if is_major else "Dark House", tempo)
        elif brightness > 0.4:
            return ("Disco/Funk", tempo)
        else:
            return ("Club/Groovy", tempo)

    # === DRUM & BASS / FAST (148-180 BPM) ===
    # Lowered min BPM from 160 to 148 to catch half-tempo detection issues
    if 148 <= tempo <= 180:
        if energy > 0.4:
            return ("Drum & Bass", tempo)
        elif energy > 0.25:
            return ("Breakbeat/Fast", tempo)
        else:
            return ("Fast/Atmospheric", tempo)

    # === HIGH ENERGY RAVE/HARD (> 180 BPM or very high energy) ===
    # Changed tempo threshold from 145 to 180 to avoid conflicts with DnB
    # Increased energy threshold from 0.5 to 0.7 to avoid catching normal loud tracks
    if tempo > 180 or energy > 0.7:
        if energy > 0.8:
            return ("Hard/Aggressive", tempo)
        elif energy > 0.6:
            return ("Energetic/Rave", tempo)
        else:
            return ("Driving Electronic", tempo)

    # === AMBIENT/ATMOSPHERIC (Very low energy) ===
    # This section handles tracks that didn't match dance/electronic categories above
    if energy < 0.2:
        if tempo < 70:
            if energy < 0.1:
                return ("Ambient/Atmospheric", tempo)
            elif not is_major:
                return ("Melancholic/Sad", tempo)
            else:
                return ("Downtempo/Relaxed", tempo)
        elif 70 <= tempo < 100:
            if energy < 0.1 and brightness < 0.4:
                return ("Downtempo/Dark", tempo)
            elif energy < 0.12:
                return ("Ambient/Chill", tempo)
            else:
                return ("Midtempo Groove", tempo)
        else:
            # High tempo (>100 BPM) but low energy - minimal electronic
            return ("Minimal/Sparse", tempo)

    # === MODERATE ENERGY (Fallback) ===
    if energy >= 0.25:
        if tempo > 100:
            return ("Upbeat/Moderate", tempo)
        else:
            return ("Moderate Groove", tempo)
    elif energy >= 0.15:
        return ("Relaxed/Moderate", tempo)
    else:
        return ("Low Energy", tempo)


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