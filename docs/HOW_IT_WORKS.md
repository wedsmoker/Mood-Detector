# How Mood Detector Works

This document explains the technical details of how Mood Detector analyzes audio files to determine musical mood.

## Architecture Overview

Mood Detector uses a combination of audio signal processing and rule-based classification to determine the mood of music. The process involves:

1. Feature extraction from audio signals
2. Rule-based mood classification
3. Result formatting and explanation generation

## Feature Extraction

The `features.py` module extracts various acoustic features from audio files:

### Temporal Features
- **Tempo**: Beats per minute (BPM) calculated using librosa's beat tracking
- **Zero Crossing Rate**: Rate at which the audio signal changes sign, indicating rhythmic activity

### Spectral Features
- **Spectral Centroid**: Center of mass of the spectrum, indicating brightness
- **Spectral Rolloff**: Frequency below which a certain percentage of the spectrum's energy lies
- **MFCCs**: Mel-frequency cepstral coefficients representing spectral characteristics
- **Chroma Features**: Pitch class profiles showing the intensity of different musical notes

### Energy Features
- **RMS Energy**: Root mean square energy indicating overall loudness and activity

## Mood Classification

The `mood_classifier.py` module uses the extracted features to classify mood based on:

### Primary Classifiers
- **Tempo**: Slower tempos associate with relaxed/melancholic moods, faster with energetic ones
- **Energy**: Higher energy signals associate with active, exciting moods
- **Spectral Brightness**: Brighter sounds often correspond to happier, more open moods

### Mood Categories

Currently supported mood categories:

- **Melancholic Ambient**: Slow tempo (<80 BPM), low energy (<0.3)
- **Chill/Relaxed**: Moderate tempo (<100 BPM), low-to-moderate energy (<0.5)
- **Upbeat/Energetic**: Moderate tempo (<120 BPM), high energy (>0.7)
- **High-Energy/Dance**: Fast tempo (>120 BPM), high energy (>0.8)
- **Intense/Pumped**: Very fast tempo (>140 BPM), high energy (>0.6)
- **Deep Contemplation**: Slow tempo (<80 BPM), high energy (>0.6)
- **Bright & Energetic**: High brightness and energy
- **Dark & Mellow**: Low brightness, low energy
- **Balanced/Neutral**: Moderate values across all dimensions

## Key Detection

The system attempts to identify the musical key using chroma features, which represent the intensity of different pitch classes in the audio signal.

## Technical Implementation Details

### Audio Processing
- Uses librosa for audio loading and feature extraction
- Limited to first 30 seconds for performance
- Supports common audio formats through librosa

### Feature Normalization
- Tempo normalized to meaningful ranges
- Energy values scaled to 0-1 range
- Spectral features normalized relative to their typical ranges

### Classification Rules
The classifier uses a combination of threshold-based rules and weighted feature combinations to determine the most appropriate mood classification.

## Extending the System

### Adding New Mood Categories
1. Add new rules in `classify_mood()` function
2. Update similarity calculations in `calculate_similarity_scores()`
3. Modify explanation generation in `generate_explanation()`

### Feature Enhancement
The system can be enhanced with:
- More sophisticated machine learning models
- Additional acoustic features
- Genre-specific classifications
- Cultural adaptation of mood definitions

## Performance Characteristics

- **Speed**: ~2-5 seconds per 3-minute song (depending on hardware)
- **Memory**: ~50-100 MB for typical analysis
- **Accuracy**: Rule-based, optimized for common mood distinctions
- **Scalability**: Can process multiple files sequentially or in batch mode