from mood_detector import analyze_audio

# Simplest usage
result = analyze_audio("song.mp3")
print(f"Mood: {result.mood}")

# Advanced usage
result = analyze_audio(
    "song.mp3",
    detailed=True,
    similarity_search=True
)
print(f"Similar vibes: {result.similarity_scores}")