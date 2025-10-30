# Mood Detector API Reference

## Endpoints

### `GET /`
**Description:** Root endpoint that returns a welcome message and API documentation link.

**Response:**
```
{
  "message": "Welcome to the Mood Detector API",
  "docs": "/docs"
}
```

### `POST /analyze`
**Description:** Analyze the mood of an uploaded audio file.

**Form Parameters:**
- `file` (file, required): Audio file to analyze (MP3, WAV, FLAC, M4A, AAC, OGG)
- `detailed` (boolean, optional): Whether to return detailed analysis (default: false)
- `similarity_search` (boolean, optional): Whether to include similarity scores (default: false)

**Response:**
```json
{
  "mood": "string",
  "energy": "number",
  "tempo": "number",
  "key": "string",
  "explanation": "string",
  "duration": "number|null",
  "similar_moods": "object|null"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@song.mp3"
```

### `POST /analyze-url`
**Description:** Analyze the mood of an audio file from a URL. (Not yet implemented)

### `POST /batch-analyze`
**Description:** Analyze the mood of multiple uploaded audio files.

**Form Parameters:**
- `files` (list[file], required): List of audio files to analyze
- `detailed` (boolean, optional): Whether to return detailed analysis (default: false)
- `similarity_search` (boolean, optional): Whether to include similarity scores (default: false)

**Response:**
```json
{
  "results": [
    {
      "mood": "string",
      "energy": "number",
      "tempo": "number",
      "key": "string",
      "explanation": "string",
      "similar_moods": "object|null"
    }
  ]
}
```

## Response Field Descriptions

- `mood`: The detected mood category (e.g., "Chill/Relaxed", "High-Energy/Dance")
- `energy`: Energy level normalized to 0-1 scale
- `tempo`: Tempo in BPM (beats per minute)
- `key`: Musical key (e.g., "C major")
- `explanation`: Human-readable explanation of the mood classification
- `duration`: Audio duration in seconds (only included with detailed=true)
- `similar_moods`: Object with mood categories and their similarity scores

## Error Responses

- `400 Bad Request`: Unsupported file format or invalid parameters
- `500 Internal Server Error`: Error during audio analysis

## Example Usage

### Python
```python
import requests

url = "http://localhost:8000/analyze"
files = {"file": open("song.mp3", "rb")}
response = requests.post(url, files=files)
result = response.json()
print(result["mood"])
```

### JavaScript
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/analyze', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log(data.mood);
});
```