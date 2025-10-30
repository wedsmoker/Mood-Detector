import sys
from pathlib import Path

# Add the parent directory to sys.path to import mood_detector
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from typing import Optional

# Import from same directory
sys.path.insert(0, str(Path(__file__).parent))
from models import MoodAnalysisResponse

from mood_detector import analyze_audio, batch_analyze


app = FastAPI(
    title="Mood Detector API",
    description="Open-source music mood analysis API",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Mood Detector API", "docs": "/docs"}


@app.post("/analyze", response_model=MoodAnalysisResponse)
async def analyze_file(
    file: UploadFile = File(...),
    detailed: bool = Form(False),
    similarity_search: bool = Form(False)
):
    """
    Analyze the mood of an uploaded audio file.
    
    Args:
        file: Audio file to analyze (MP3, WAV, FLAC)
        detailed: Whether to return detailed analysis
        similarity_search: Whether to include similarity scores
        
    Returns:
        MoodAnalysisResponse: Analysis results including mood, energy, tempo, etc.
    """
    # Check if the uploaded file has a valid extension
    valid_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in valid_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_extension}. Supported formats: {valid_extensions}"
        )
    
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        try:
            contents = await file.read()
            temp_file.write(contents)
            temp_path = temp_file.name
        except Exception:
            raise HTTPException(status_code=400, detail="Could not read uploaded file. Is it corrupted?")
    
    try:
        # Analyze the audio file
        result = analyze_audio(
            audio_path=temp_path,
            detailed=detailed,
            similarity_search=similarity_search
        )
        
        # Prepare response (order matches README example)
        response = MoodAnalysisResponse(
            mood=result.mood,
            tempo=result.tempo,
            energy=result.energy,
            key=result.key,
            explanation=result.explanation
        )

        return response
        
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="File not found. Check the audio file?")
    except ValueError as e:
        if "Invalid or unsupported audio file" in str(e):
            raise HTTPException(status_code=400, detail="Invalid audio file. Is it actually an audio file?")
        else:
            raise HTTPException(status_code=400, detail=f"Invalid audio file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Can't read audio file. Is it corrupted? ({str(e)})")
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@app.post("/analyze-url")
async def analyze_url(
    url: str = Form(...),
    detailed: bool = Form(False),
    similarity_search: bool = Form(False)
):
    """
    Analyze the mood of an audio file from a URL.
    Note: This is a placeholder implementation. A full implementation would need 
    to handle downloading from URL and potentially using a library like youtube-dl
    for YouTube links.
    """
    # Placeholder implementation - would need additional dependencies to download from URL
    raise HTTPException(status_code=501, detail="URL analysis not yet implemented")


@app.post("/batch-analyze")
async def batch_analyze_files(
    files: list[UploadFile] = File(...),
    detailed: bool = Form(False),
    similarity_search: bool = Form(False)
):
    """
    Analyze the mood of multiple uploaded audio files.
    
    Args:
        files: List of audio files to analyze
        detailed: Whether to return detailed analysis
        similarity_search: Whether to include similarity scores
    """
    results = []
    
    # Validate all files first
    valid_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg'}
    
    for file in files:
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in valid_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_extension} in file {file.filename}"
            )
    
    # Process each file
    temp_paths = []
    try:
        for file in files:
            file_extension = os.path.splitext(file.filename)[1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                try:
                    contents = await file.read()
                    temp_file.write(contents)
                    temp_paths.append(temp_file.name)
                except Exception:
                    raise HTTPException(status_code=400, detail=f"Could not read file {file.filename}. Is it corrupted?")
        
        # Analyze all files
        analysis_results = batch_analyze(
            temp_paths,
            detailed=detailed,
            similarity_search=similarity_search
        )
        
        # Format results
        for result in analysis_results:
            response = MoodAnalysisResponse(
                mood=result.mood,
                tempo=result.tempo,
                energy=result.energy,
                key=result.key,
                explanation=result.explanation
            )
            results.append(response)
        
        return {"results": results}
        
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="File not found. Check the audio files?")
    except ValueError as e:
        if "Invalid or unsupported audio file" in str(e):
            raise HTTPException(status_code=400, detail="Invalid audio file found. Check the files?")
        else:
            raise HTTPException(status_code=400, detail=f"Invalid audio file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing audio: {str(e)}")
    
    finally:
        # Clean up temporary files
        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)