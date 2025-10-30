import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from pathlib import Path
from mood_detector.analyzer import analyze_audio
from mood_detector.features import extract_features
from mood_detector.mood_classifier import classify_mood, MoodResult


class TestAnalyzer(unittest.TestCase):
    
    def setUp(self):
        # Create a dummy audio file for testing purposes
        self.dummy_audio_path = "dummy_test_audio.wav"
    
    @patch('mood_detector.features.librosa.load')
    @patch('mood_detector.features.librosa.get_duration')
    def test_extract_features(self, mock_get_duration, mock_load):
        # Mock the librosa functions
        mock_load.return_value = (np.array([0.1, 0.2, 0.3]), 22050)  # dummy signal and sample rate
        mock_get_duration.return_value = 30.0
        
        features = extract_features(self.dummy_audio_path)
        
        # Check that features are extracted
        self.assertIn('tempo', features)
        self.assertIn('energy', features)
        self.assertIn('spectral_centroid', features)
        self.assertIn('duration', features)
    
    @patch('mood_detector.features.librosa.load')
    @patch('mood_detector.features.librosa.get_duration')
    def test_classify_mood(self, mock_get_duration, mock_load):
        # Mock the librosa functions to return some dummy values
        mock_load.return_value = (np.array([0.1, 0.2, 0.3]), 22050)
        mock_get_duration.return_value = 30.0
        
        # Extract dummy features
        features = extract_features(self.dummy_audio_path)
        # Override with some meaningful test values
        features['tempo'] = 120.0
        features['energy'] = 0.7
        features['spectral_centroid'] = 2000.0
        features['chroma'] = [0.1] * 12  # 12 chroma values
        
        mood_result = classify_mood(features)
        
        # Check that the result is of the correct type
        self.assertIsInstance(mood_result, MoodResult)
        self.assertIsInstance(mood_result.mood, str)
        self.assertIsInstance(mood_result.energy, float)
        self.assertIsInstance(mood_result.tempo, float)
        self.assertIsInstance(mood_result.key, str)
        self.assertIsInstance(mood_result.explanation, str)
    
    @patch('mood_detector.analyzer.extract_features')
    @patch('mood_detector.analyzer.classify_mood')
    def test_analyze_audio(self, mock_classify_mood, mock_extract_features):
        # Mock the return values
        mock_extract_features.return_value = {
            'tempo': 120.0,
            'energy': 0.7,
            'spectral_centroid': 2000.0,
            'chroma': [0.1] * 12,
            'duration': 30.0
        }
        
        mock_classify_mood.return_value = MoodResult(
            mood="Test Mood",
            energy=0.7,
            tempo=120.0,
            key="C major",
            similarity_scores={"Test Mood": 0.9},
            explanation="Test explanation"
        )
        
        # Create a temporary dummy file for testing
        dummy_path = Path(self.dummy_audio_path)
        dummy_path.touch()  # Create the file
        
        try:
            result = analyze_audio(self.dummy_audio_path)
            
            # Check that the result is of the correct type
            self.assertIsInstance(result, MoodResult)
            self.assertEqual(result.mood, "Test Mood")
            self.assertEqual(result.energy, 0.7)
            self.assertEqual(result.tempo, 120.0)
        finally:
            # Clean up the dummy file
            if dummy_path.exists():
                dummy_path.unlink()
    
    def test_analyze_audio_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            analyze_audio("nonexistent_file.mp3")
    
    def test_analyze_audio_unsupported_format(self):
        # Create a dummy file with unsupported extension
        dummy_path = Path("test.txt")
        dummy_path.touch()
        
        try:
            with self.assertRaises(ValueError):
                analyze_audio("test.txt")
        finally:
            # Clean up the dummy file
            if dummy_path.exists():
                dummy_path.unlink()


if __name__ == '__main__':
    unittest.main()