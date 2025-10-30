# Analyze a song
curl -X POST http://localhost:8000/analyze \
  -F "file=@song.mp3"

# Analyze from YouTube URL (placeholder)
curl -X POST http://localhost:8000/analyze-url \
  -d '{"url": "https://youtube.com/watch?v=..."}'

# Batch analysis
curl -X POST http://localhost:8000/batch \
  -F "files=@song1.mp3" \
  -F "files=@song2.mp3"