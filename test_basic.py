"""
Quick test to see if mood_detector imports work
"""

try:
    from mood_detector import analyze_audio
    print("✅ mood_detector imports successfully!")
    print("✅ Ready to analyze audio files")
    print("\nUsage:")
    print('  from mood_detector import analyze_audio')
    print('  result = analyze_audio("song.mp3")')
    print('  print(result.mood)')
except ImportError as e:
    print("❌ Import failed:", e)
    print("\nMake sure you ran:")
    print("  pip install -e .")
