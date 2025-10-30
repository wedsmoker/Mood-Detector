"""
Simple Music Library Analyzer
Analyzes and filters your music collection using mood-detector
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import threading
from pathlib import Path
from typing import List, Dict

# Import mood_detector directly (no API needed!)
from mood_detector import analyze_audio

# Configuration
CACHE_FILE = "music_library_cache.json"
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'}


class MusicLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Library Analyzer")
        self.root.geometry("1200x700")

        # Data storage
        self.library = []  # List of analyzed tracks
        self.filtered_library = []  # Filtered results
        self.current_folder = None
        self.is_analyzing = False

        # Load cache if exists
        self.load_cache()

        # Build UI
        self.build_ui()

        # Update display
        self.apply_filters()

    def build_ui(self):
        """Build the user interface"""

        # === TOP CONTROLS ===
        top_frame = tk.Frame(self.root, bg="#2b2b2b", pady=10, padx=10)
        top_frame.pack(fill=tk.X)

        # Folder selection
        tk.Button(
            top_frame,
            text="📁 Open Folder",
            command=self.select_folder,
            bg="#4a4a4a",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

        # Current folder label
        self.folder_label = tk.Label(
            top_frame,
            text="No folder selected",
            bg="#2b2b2b",
            fg="#cccccc",
            font=("Arial", 9)
        )
        self.folder_label.pack(side=tk.LEFT, padx=10)

        # Analyze button
        self.analyze_btn = tk.Button(
            top_frame,
            text="🔍 Analyze All",
            command=self.analyze_folder,
            bg="#3d8c40",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5,
            state=tk.DISABLED
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=5)

        # Progress label
        self.progress_label = tk.Label(
            top_frame,
            text="",
            bg="#2b2b2b",
            fg="#ffcc00",
            font=("Arial", 9, "bold")
        )
        self.progress_label.pack(side=tk.LEFT, padx=10)

        # Stats
        self.stats_label = tk.Label(
            top_frame,
            text="Tracks: 0",
            bg="#2b2b2b",
            fg="#cccccc",
            font=("Arial", 9)
        )
        self.stats_label.pack(side=tk.RIGHT, padx=5)

        # === FILTERS ===
        filter_frame = tk.Frame(self.root, bg="#3a3a3a", pady=10, padx=10)
        filter_frame.pack(fill=tk.X)

        tk.Label(filter_frame, text="Filters:", bg="#3a3a3a", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

        # Mood filter
        tk.Label(filter_frame, text="Mood:", bg="#3a3a3a", fg="#cccccc").pack(side=tk.LEFT, padx=(20, 5))
        self.mood_filter = ttk.Combobox(filter_frame, width=20, state="readonly")
        self.mood_filter.pack(side=tk.LEFT, padx=5)
        self.mood_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # Tempo filter
        tk.Label(filter_frame, text="Tempo:", bg="#3a3a3a", fg="#cccccc").pack(side=tk.LEFT, padx=(20, 5))
        self.tempo_min = tk.Entry(filter_frame, width=8)
        self.tempo_min.pack(side=tk.LEFT, padx=2)
        self.tempo_min.insert(0, "0")
        tk.Label(filter_frame, text="-", bg="#3a3a3a", fg="#cccccc").pack(side=tk.LEFT)
        self.tempo_max = tk.Entry(filter_frame, width=8)
        self.tempo_max.pack(side=tk.LEFT, padx=2)
        self.tempo_max.insert(0, "200")

        # Energy filter
        tk.Label(filter_frame, text="Energy:", bg="#3a3a3a", fg="#cccccc").pack(side=tk.LEFT, padx=(20, 5))
        self.energy_min = tk.Entry(filter_frame, width=8)
        self.energy_min.pack(side=tk.LEFT, padx=2)
        self.energy_min.insert(0, "0.0")
        tk.Label(filter_frame, text="-", bg="#3a3a3a", fg="#cccccc").pack(side=tk.LEFT)
        self.energy_max = tk.Entry(filter_frame, width=8)
        self.energy_max.pack(side=tk.LEFT, padx=2)
        self.energy_max.insert(0, "1.0")

        # Key filter
        tk.Label(filter_frame, text="Key:", bg="#3a3a3a", fg="#cccccc").pack(side=tk.LEFT, padx=(20, 5))
        self.key_filter = ttk.Combobox(filter_frame, width=12, state="readonly")
        self.key_filter.pack(side=tk.LEFT, padx=5)
        self.key_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # Apply filters button
        tk.Button(
            filter_frame,
            text="Apply",
            command=self.apply_filters,
            bg="#4a7ba7",
            fg="white",
            padx=15
        ).pack(side=tk.LEFT, padx=10)

        # Clear filters button
        tk.Button(
            filter_frame,
            text="Clear",
            command=self.clear_filters,
            bg="#6a6a6a",
            fg="white",
            padx=15
        ).pack(side=tk.LEFT, padx=2)

        # === TRACK LIST ===
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview
        columns = ("filename", "mood", "tempo", "energy", "key", "path")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)

        # Column headers
        self.tree.heading("filename", text="Track Name")
        self.tree.heading("mood", text="Mood")
        self.tree.heading("tempo", text="Tempo (BPM)")
        self.tree.heading("energy", text="Energy")
        self.tree.heading("key", text="Key")
        self.tree.heading("path", text="Path")

        # Column widths
        self.tree.column("filename", width=250)
        self.tree.column("mood", width=150)
        self.tree.column("tempo", width=100)
        self.tree.column("energy", width=80)
        self.tree.column("key", width=80)
        self.tree.column("path", width=400)

        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b")
        style.configure("Treeview.Heading", background="#4a4a4a", foreground="white", font=("Arial", 9, "bold"))

    def select_folder(self):
        """Open folder selection dialog"""
        folder = filedialog.askdirectory(title="Select Music Folder")
        if folder:
            self.current_folder = folder
            self.folder_label.config(text=f"Folder: {folder}")
            self.analyze_btn.config(state=tk.NORMAL)

    def find_audio_files(self, folder: str) -> List[str]:
        """Recursively find all audio files in folder"""
        audio_files = []
        for root, dirs, files in os.walk(folder):
            for file in files:
                if Path(file).suffix.lower() in AUDIO_EXTENSIONS:
                    audio_files.append(os.path.join(root, file))
        return audio_files

    def analyze_folder(self):
        """Analyze all audio files in selected folder"""
        if not self.current_folder:
            messagebox.showwarning("No Folder", "Please select a folder first!")
            return

        if self.is_analyzing:
            messagebox.showinfo("Already Analyzing", "Analysis already in progress!")
            return

        # Find files
        files = self.find_audio_files(self.current_folder)
        if not files:
            messagebox.showinfo("No Files", "No audio files found in this folder!")
            return

        # Start analysis in background thread
        self.is_analyzing = True
        self.analyze_btn.config(state=tk.DISABLED, text="Analyzing...")
        threading.Thread(target=self.analyze_files_thread, args=(files,), daemon=True).start()

    def analyze_files_thread(self, files: List[str]):
        """Analyze files in background thread"""
        total = len(files)
        analyzed = 0

        for file in files:
            # Update progress
            self.root.after(0, lambda: self.progress_label.config(
                text=f"Analyzing {analyzed + 1}/{total}..."
            ))

            # Check if already in library
            if any(track['path'] == file for track in self.library):
                analyzed += 1
                continue

            # Analyze directly with mood_detector (no API needed!)
            try:
                result = analyze_audio(file, detailed=True)

                # Add to library
                track = {
                    'filename': os.path.basename(file),
                    'path': file,
                    'mood': result.mood,
                    'tempo': result.tempo,
                    'energy': result.energy,
                    'key': result.key,
                    'explanation': result.explanation
                }
                self.library.append(track)

            except Exception as e:
                print(f"Error analyzing {file}: {e}")

            analyzed += 1

        # Analysis complete
        self.is_analyzing = False
        self.root.after(0, self.analysis_complete)

    def analysis_complete(self):
        """Called when analysis is complete"""
        self.analyze_btn.config(state=tk.NORMAL, text="🔍 Analyze All")
        self.progress_label.config(text="✓ Analysis complete!")

        # Save cache
        self.save_cache()

        # Update display
        self.apply_filters()

        # Show completion message
        messagebox.showinfo("Analysis Complete",
            f"Analyzed {len(self.library)} tracks!\n\n"
            "Use filters to explore your library.")

    def apply_filters(self):
        """Apply filters and update display"""
        # Get filter values
        mood_filter = self.mood_filter.get()
        key_filter = self.key_filter.get()

        try:
            tempo_min = float(self.tempo_min.get())
            tempo_max = float(self.tempo_max.get())
            energy_min = float(self.energy_min.get())
            energy_max = float(self.energy_max.get())
        except ValueError:
            tempo_min, tempo_max = 0, 200
            energy_min, energy_max = 0.0, 1.0

        # Filter tracks
        self.filtered_library = []
        for track in self.library:
            # Check mood
            if mood_filter and mood_filter != "All" and track['mood'] != mood_filter:
                continue

            # Check tempo
            if not (tempo_min <= track['tempo'] <= tempo_max):
                continue

            # Check energy
            if not (energy_min <= track['energy'] <= energy_max):
                continue

            # Check key
            if key_filter and key_filter != "All" and track['key'] != key_filter:
                continue

            self.filtered_library.append(track)

        # Update display
        self.update_display()

        # Update filter dropdowns
        self.update_filter_options()

    def clear_filters(self):
        """Clear all filters"""
        self.mood_filter.set("All")
        self.key_filter.set("All")
        self.tempo_min.delete(0, tk.END)
        self.tempo_min.insert(0, "0")
        self.tempo_max.delete(0, tk.END)
        self.tempo_max.insert(0, "200")
        self.energy_min.delete(0, tk.END)
        self.energy_min.insert(0, "0.0")
        self.energy_max.delete(0, tk.END)
        self.energy_max.insert(0, "1.0")
        self.apply_filters()

    def update_display(self):
        """Update the track list display"""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add filtered tracks
        for track in self.filtered_library:
            self.tree.insert("", tk.END, values=(
                track['filename'],
                track['mood'],
                f"{track['tempo']:.1f}",
                f"{track['energy']:.3f}",
                track['key'],
                track['path']
            ))

        # Update stats
        self.stats_label.config(
            text=f"Showing {len(self.filtered_library)} / {len(self.library)} tracks"
        )

    def update_filter_options(self):
        """Update filter dropdown options based on library"""
        # Get unique moods and keys
        moods = sorted(set(track['mood'] for track in self.library))
        keys = sorted(set(track['key'] for track in self.library))

        # Update dropdowns
        self.mood_filter['values'] = ["All"] + moods
        if not self.mood_filter.get():
            self.mood_filter.set("All")

        self.key_filter['values'] = ["All"] + keys
        if not self.key_filter.get():
            self.key_filter.set("All")

    def save_cache(self):
        """Save library to cache file"""
        try:
            with open(CACHE_FILE, 'w') as f:
                json.dump(self.library, f, indent=2)
        except Exception as e:
            print(f"Failed to save cache: {e}")

    def load_cache(self):
        """Load library from cache file"""
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r') as f:
                    self.library = json.load(f)
                print(f"Loaded {len(self.library)} tracks from cache")
            except Exception as e:
                print(f"Failed to load cache: {e}")
                self.library = []


def main():
    root = tk.Tk()
    app = MusicLibraryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
