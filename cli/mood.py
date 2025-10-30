import argparse
import sys
from pathlib import Path
import os

# Add the parent directory to sys.path to import mood_detector
sys.path.append(str(Path(__file__).parent.parent))

from mood_detector import analyze_audio


def print_bar_chart(value, label="Energy"):
    """Print a simple bar chart representation of a value."""
    # Normalize value to 0-10 range for the bar
    bar_length = int(value * 10)
    bar = "█" * bar_length + "░" * (10 - bar_length)
    print(f"{label}: {bar} {value:.1f}")


def main():
    parser = argparse.ArgumentParser(description="Mood Detector CLI - Analyze music moods")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze the mood of an audio file")
    analyze_parser.add_argument("file", type=str, help="Path to the audio file to analyze")
    analyze_parser.add_argument("--detailed", action="store_true", help="Show detailed analysis")
    analyze_parser.add_argument("--similarity", action="store_true", help="Show similarity scores")
    
    # Batch analyze command
    batch_parser = subparsers.add_parser("batch", help="Analyze multiple audio files")
    batch_parser.add_argument("files", type=str, nargs="+", help="Paths to audio files to analyze")
    batch_parser.add_argument("--detailed", action="store_true", help="Show detailed analysis")
    batch_parser.add_argument("--similarity", action="store_true", help="Show similarity scores")
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        if not Path(args.file).exists():
            print(f"Error: File '{args.file}' does not exist.")
            sys.exit(1)
        
        try:
            result = analyze_audio(
                audio_path=args.file,
                detailed=args.detailed,
                similarity_search=args.similarity
            )
            
            print("🎵 Analysis Complete")
            print(f"Mood: {result.mood}")
            print_bar_chart(result.energy, "Energy")
            print(f"Tempo: {result.tempo:.0f} BPM")
            print(f"Key: {result.key}")
            print(f"Explanation: {result.explanation}")
            
            if args.similarity:
                print("\nSimilar moods:")
                # Sort similarity scores in descending order
                sorted_similarities = sorted(result.similarity_scores.items(), key=lambda x: x[1], reverse=True)
                for mood, score in sorted_similarities[:5]:  # Show top 5
                    print(f"  {mood}: {score:.2f}")
        
        except Exception as e:
            print(f"Error analyzing file: {str(e)}")
            sys.exit(1)
    
    elif args.command == "batch":
        print(f"🎵 Analyzing {len(args.files)} files...")
        
        for file_path in args.files:
            if not Path(file_path).exists():
                print(f"⚠️  Skipping '{file_path}' - file does not exist.")
                continue
            
            try:
                result = analyze_audio(
                    audio_path=file_path,
                    detailed=args.detailed,
                    similarity_search=args.similarity
                )
                
                print(f"\n{Path(file_path).name}:")
                print(f"  Mood: {result.mood}")
                print(f"  Energy: {result.energy:.2f}")
                print(f"  Tempo: {result.tempo:.0f} BPM")
                
            except Exception as e:
                print(f"  ⚠️  Error analyzing '{file_path}': {str(e)}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()