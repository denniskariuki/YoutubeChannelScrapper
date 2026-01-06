import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import subprocess
import whisper
import tempfile
import csv
import threading
from datetime import datetime
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
import json

# Try to import optional packages with fallbacks
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter
    TRANSCRIPT_AVAILABLE = True
except ImportError:
    TRANSCRIPT_AVAILABLE = False
    print("youtube-transcript-api not installed. Transcripts will not be available.")

try:
    from googleapiclient.discovery import build
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    print("google-api-python-client not installed. Some features may be limited.")

try:
    import isodate
    ISODATE_AVAILABLE = True
except ImportError:
    ISODATE_AVAILABLE = False
    print("isodate not installed. Duration parsing may be limited.")

class YouTubeChannelScraper:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Channel Scraper v2.0")
        self.root.geometry("1000x750")
        
        # API Key (Optional)
        self.api_key = ""
        
        # Variables
        self.channel_url = tk.StringVar()
        self.max_videos = tk.IntVar(value=25)
        self.output_file = tk.StringVar()
        self.is_scraping = False
        self.scrape_method = tk.StringVar(value="web")  # "web" or "api"
        self.include_transcript = tk.BooleanVar(value=True)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Title
        title_label = ttk.Label(main_frame, text="YouTube Channel Scraper", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1
        
        # Scraping Method Selection
        ttk.Label(main_frame, text="Scraping Method:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 10))
        
        method_frame = ttk.Frame(main_frame)
        method_frame.grid(row=row, column=1, sticky=tk.W, pady=(0, 10))
        
        ttk.Radiobutton(method_frame, text="Web Scraping (No API Key)", 
                       variable=self.scrape_method, value="web").grid(row=0, column=0, padx=(0, 20))
        ttk.Radiobutton(method_frame, text="YouTube API (More Data)", 
                       variable=self.scrape_method, value="api").grid(row=0, column=1)
        row += 1
        
        # API Key Section (only shown when API method is selected)
        self.api_frame = ttk.LabelFrame(main_frame, text="YouTube Data API Key (Optional)")
        self.api_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10), padx=5)
        self.api_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.api_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.api_key_entry = ttk.Entry(self.api_frame, width=70, show="*")
        self.api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Button(self.api_frame, text="Get API Key", 
                  command=self.open_api_help).grid(row=0, column=2, padx=5, pady=5)
        row += 1
        
        # Channel URL Section
        ttk.Label(main_frame, text="YouTube Channel URL:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))
        
        url_frame = ttk.Frame(main_frame)
        url_frame.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        url_frame.columnconfigure(0, weight=1)
        
        self.url_entry = ttk.Entry(url_frame, textvariable=self.channel_url, width=70)
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(url_frame, text="Paste", command=self.paste_url).grid(row=0, column=1)
        row += 1
        
        # Example URLs
        example_label = ttk.Label(main_frame, text="Examples: https://www.youtube.com/@ChannelName OR https://www.youtube.com/channel/UC...", 
                                 font=("Arial", 9), foreground="gray")
        example_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        row += 1
        
        # Options Frame
        options_frame = ttk.LabelFrame(main_frame, text="Options")
        options_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10), padx=5)
        options_frame.columnconfigure(1, weight=1)
        
        # Max Videos
        ttk.Label(options_frame, text="Max Videos:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        max_videos_frame = ttk.Frame(options_frame)
        max_videos_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.max_spinbox = ttk.Spinbox(max_videos_frame, from_=1, to=500, 
                                      textvariable=self.max_videos, width=10)
        self.max_spinbox.grid(row=0, column=0, padx=(0, 10))
        
        # Include Transcript
        ttk.Checkbutton(options_frame, text="Include Transcripts", 
                       variable=self.include_transcript).grid(row=0, column=2, padx=20)
        
        # Output Format
        ttk.Label(options_frame, text="Output Format:").grid(row=0, column=3, sticky=tk.W, padx=5)
        ttk.Radiobutton(options_frame, text="CSV", value="csv", 
                       variable=tk.StringVar(value="csv")).grid(row=0, column=4, padx=(0, 10))
        ttk.Radiobutton(options_frame, text="Excel", value="excel", 
                       variable=tk.StringVar(value="csv")).grid(row=0, column=5)
        row += 1
        
        # Output File Section
        ttk.Label(main_frame, text="Output File:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_file, width=70)
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(output_frame, text="Browse", command=self.browse_output_file).grid(row=0, column=1)
        row += 1
        
        # Buttons Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=15)
        
        self.scrape_button = ttk.Button(button_frame, text="🚀 Start Scraping", 
                                       command=self.start_scraping, width=20)
        self.scrape_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹ Stop", 
                                     command=self.stop_scraping, state=tk.DISABLED, width=15)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="🧹 Clear Logs", 
                  command=self.clear_logs).grid(row=0, column=2, padx=5)
        
        ttk.Button(button_frame, text="📊 Preview Data", 
                  command=self.preview_data).grid(row=0, column=3, padx=5)
        row += 1
        
        # Progress Section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 5))
        progress_frame.columnconfigure(1, weight=1)
        
        self.progress_label = ttk.Label(progress_frame, text="Ready")
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, mode='determinate')
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        row += 1
        
        # Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="Status & Logs")
        status_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), 
                         pady=(5, 0), padx=5)
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        # Log Output
        self.log_text = scrolledtext.ScrolledText(status_frame, height=20, width=100,
                                                 wrap=tk.WORD, font=("Consolas", 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Configure row/column weights
        main_frame.rowconfigure(row, weight=1)
        
        # Bind method change
        self.scrape_method.trace('w', self.on_method_change)
        self.on_method_change()
    
    def on_method_change(self, *args):
        """Show/hide API key section based on method"""
        if self.scrape_method.get() == "api":
            self.api_frame.grid()
            self.log_message("Using YouTube API method (requires API key)")
        else:
            self.api_frame.grid_remove()
            self.log_message("Using Web Scraping method (no API key needed)")
    
    def open_api_help(self):
        """Open browser to get API key instructions"""
        import webbrowser
        webbrowser.open("https://developers.google.com/youtube/v3/getting-started")
        self.log_message("Opened API key instructions in browser")
    
    def paste_url(self):
        """Paste URL from clipboard"""
        try:
            clipboard = self.root.clipboard_get()
            self.channel_url.set(clipboard)
            self.log_message(f"Pasted URL from clipboard")
        except:
            self.log_message("Could not paste from clipboard")
    
    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile="youtube_data.csv"
        )
        if filename:
            self.output_file.set(filename)
    
    def log_message(self, message, color="black"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Configure tag for color if needed
        if color != "black":
            self.log_text.tag_config(color, foreground=color)
        
        # Insert message
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", color)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_progress(self, value, total=None):
        if total:
            percentage = int((value / total) * 100)
            self.progress_var.set(percentage)
            self.progress_label.config(text=f"Processing: {value}/{total} ({percentage}%)")
        else:
            self.progress_var.set(value)
        self.root.update_idletasks()
    
    def clear_logs(self):
        self.log_text.delete(1.0, tk.END)
        self.log_message("Logs cleared", "blue")
    
    def preview_data(self):
        """Preview scraped data if available"""
        output_file = self.output_file.get()
        if not output_file or not os.path.exists(output_file):
            messagebox.showinfo("Info", "No data file found. Please scrape data first.")
            return
        
        try:
            if output_file.endswith('.csv'):
                df = pd.read_csv(output_file)
            else:
                df = pd.read_excel(output_file)
            
            # Create preview window
            preview = tk.Toplevel(self.root)
            preview.title(f"Data Preview - {len(df)} rows")
            preview.geometry("900x500")
            
            # Treeview for data
            tree_frame = ttk.Frame(preview)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Scrollbars
            vsb = ttk.Scrollbar(tree_frame, orient="vertical")
            hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
            
            # Treeview
            tree = ttk.Treeview(tree_frame, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            vsb.config(command=tree.yview)
            hsb.config(command=tree.xview)
            
            # Define columns
            tree["columns"] = list(df.columns)
            tree["show"] = "headings"
            
            # Set column headings
            for col in df.columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            
            # Add data
            for i, row in df.head(50).iterrows():  # Show first 50 rows
                tree.insert("", "end", values=list(row))
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            vsb.pack(side=tk.RIGHT, fill=tk.Y)
            hsb.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Info label
            info_label = ttk.Label(preview, 
                                 text=f"Showing {min(50, len(df))} of {len(df)} rows. Columns: {len(df.columns)}")
            info_label.pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not preview data: {str(e)}")
    
    def start_scraping(self):
        if not self.is_scraping:
            # Validate inputs
            channel_url = self.channel_url.get().strip()
            if not channel_url:
                messagebox.showerror("Error", "Please enter a YouTube channel URL")
                return
                
            output_file = self.output_file.get().strip()
            if not output_file:
                messagebox.showerror("Error", "Please select an output file")
                return
            
            # Get API key if using API method
            if self.scrape_method.get() == "api":
                self.api_key = self.api_key_entry.get().strip()
                if not self.api_key and not YOUTUBE_API_AVAILABLE:
                    messagebox.showerror("Error", 
                        "YouTube API client not installed. Please install: pip install google-api-python-client")
                    return
            
            # Disable UI elements during scraping
            self.is_scraping = True
            self.scrape_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.progress_var.set(0)
            self.progress_label.config(text="Starting...")
            self.clear_logs()
            
            # Start scraping in a separate thread
            thread = threading.Thread(target=self.scrape_channel, 
                                     args=(channel_url, output_file))
            thread.daemon = True
            thread.start()
    
    def stop_scraping(self):
        self.is_scraping = False
        self.log_message("Stopping scraper...", "orange")
    
    # ----------------------------------------------------------------------
    # Web Scraping Methods (No API Key Required)
    # ----------------------------------------------------------------------
    
    def extract_channel_id_web(self, url):
        """Extract channel ID from URL using web scraping"""
        try:
            # Handle different URL formats
            if '/channel/' in url:
                return url.split('/channel/')[-1].split('/')[0].split('?')[0]
            elif '/c/' in url:
                # For custom URLs, we need to get the actual channel ID
                response = requests.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for channel ID in meta tags or links
                meta = soup.find('meta', {'itemprop': 'channelId'})
                if meta:
                    return meta.get('content')
                
                # Look in canonical link
                canonical = soup.find('link', {'rel': 'canonical'})
                if canonical and '/channel/' in canonical.get('href', ''):
                    return canonical['href'].split('/channel/')[-1]
                
                # Try to find channel ID in script tags
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and 'channelId' in script.string:
                        import re
                        match = re.search(r'"channelId"\s*:\s*"([^"]+)"', script.string)
                        if match:
                            return match.group(1)
            
            elif '/@' in url:
                # Handle @username URLs
                username = url.split('/@')[-1].split('/')[0].split('?')[0]
                # Try to get channel page
                channel_url = f"https://www.youtube.com/@{username}"
                return self.extract_channel_id_web(channel_url)
            
            return None
            
        except Exception as e:
            self.log_message(f"Error extracting channel ID: {str(e)}", "red")
            return None
    
    def get_channel_videos_web(self, channel_id, max_videos=25):
        """Get videos from channel using web scraping"""
        videos = []
        try:
            base_url = f"https://www.youtube.com/channel/{channel_id}/videos"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(base_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find video links
            video_links = []
            for link in soup.find_all('a', {'id': 'video-title-link'}):
                href = link.get('href', '')
                if '/watch?v=' in href:
                    video_id = href.split('v=')[-1].split('&')[0]
                    title = link.get('title', '') or link.text.strip()
                    video_links.append({'video_id': video_id, 'title': title})
            
            # Get video details
            for i, video in enumerate(video_links[:max_videos]):
                if not self.is_scraping:
                    break
                    
                self.update_progress(i + 1, max_videos)
                self.log_message(f"Processing video {i+1}: {video['title'][:50]}...")
                
                video_data = self.get_video_details_web(video['video_id'])
                if video_data:
                    videos.append(video_data)
            
            return videos
            
        except Exception as e:
            self.log_message(f"Error getting videos: {str(e)}", "red")
            return videos
    
    def get_video_details_web(self, video_id):
        """Get video details by scraping video page"""
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to extract data from ytInitialData
            scripts = soup.find_all('script')
            yt_data = None
            
            for script in scripts:
                if script.string and 'ytInitialData' in script.string:
                    try:
                        start = script.string.find('{')
                        end = script.string.rfind('}') + 1
                        json_str = script.string[start:end]
                        yt_data = json.loads(json_str)
                        break
                    except:
                        continue
            
            if not yt_data:
                return None
            
            # Extract video details
            video_data = {
                'video_id': video_id,
                'video_url': url,
                'title': '',
                'description': '',
                'views': 0,
                'likes': 0,
                'duration': '',
                'upload_date': '',
                'channel_name': '',
                'channel_id': '',
                'transcript': ''
            }
            
            # Try to navigate through the JSON structure
            try:
                # Get video details
                video_details = self.find_in_json(yt_data, 'videoPrimaryInfoRenderer') or \
                               self.find_in_json(yt_data, 'videoDetails') or {}
                
                # Get title
                title = self.find_in_json(video_details, 'title') or \
                       soup.find('meta', {'property': 'og:title'})
                if title:
                    video_data['title'] = title.get('content', '') if hasattr(title, 'get') else str(title)
                
                # Get description
                desc = soup.find('meta', {'name': 'description'})
                if desc:
                    video_data['description'] = desc.get('content', '')[:500]
                
                # Get views
                view_count = self.find_in_json(video_details, 'viewCount')
                if view_count:
                    video_data['views'] = int(view_count) if str(view_count).isdigit() else view_count
                
                # Get likes (might not be available)
                likes = self.find_in_json(yt_data, 'likeCount')
                if likes:
                    video_data['likes'] = int(likes) if str(likes).isdigit() else likes
                
                # Get upload date
                date_text = self.find_in_json(video_details, 'dateText')
                if date_text and 'simpleText' in date_text:
                    video_data['upload_date'] = date_text['simpleText']
                
                # Get channel info
                channel_info = self.find_in_json(yt_data, 'channelId') or \
                              self.find_in_json(yt_data, 'ownerChannelName')
                if channel_info:
                    if isinstance(channel_info, dict):
                        video_data['channel_name'] = channel_info.get('simpleText', '')
                        video_data['channel_id'] = channel_info.get('navigationEndpoint', {}).get('browseEndpoint', {}).get('browseId', '')
                    else:
                        video_data['channel_id'] = str(channel_info)
                
                # Get transcript if requested
                if self.include_transcript.get():
                    try:
                        transcript = self.get_video_transcript(video_id)
                        video_data['transcript'] = transcript[:5000]  # Limit length
                    except:
                        video_data['transcript'] = "Not available"
                
            except Exception as e:
                self.log_message(f"Error parsing video details: {str(e)}", "orange")
            
            return video_data
            
        except Exception as e:
            self.log_message(f"Error getting video details: {str(e)}", "red")
            return None
    
    def find_in_json(self, data, target_key, current_path=None):
        """Recursively search for a key in JSON data"""
        if current_path is None:
            current_path = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if key == target_key:
                    return value
                result = self.find_in_json(value, target_key, current_path + [key])
                if result is not None:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self.find_in_json(item, target_key, current_path)
                if result is not None:
                    return result
        return None
    
    # ----------------------------------------------------------------------
    # YouTube API Methods (Requires API Key)
    # ----------------------------------------------------------------------
    
    def scrape_with_api(self, channel_url, output_file):
        """Scrape using YouTube Data API"""
        try:
            if not YOUTUBE_API_AVAILABLE:
                raise ImportError("google-api-python-client not installed")
            
            youtube = build('youtube', 'v3', developerKey=self.api_key)
            
            # Get channel ID
            if '/channel/' in channel_url:
                channel_id = channel_url.split('/channel/')[-1].split('/')[0]
            else:
                # Try to get channel ID from custom URL
                if '/@' in channel_url:
                    username = channel_url.split('/@')[-1].split('/')[0]
                    search_response = youtube.search().list(
                        q=username,
                        type='channel',
                        part='snippet',
                        maxResults=1
                    ).execute()
                    if search_response['items']:
                        channel_id = search_response['items'][0]['id']['channelId']
                    else:
                        raise ValueError("Channel not found")
                else:
                    raise ValueError("Invalid channel URL format")
            
            self.log_message(f"Channel ID: {channel_id}", "green")
            
            # Get channel details
            channel_response = youtube.channels().list(
                id=channel_id,
                part='snippet,statistics, contentDetails'
            ).execute()
            
            channel_info = channel_response['items'][0]
            channel_name = channel_info['snippet']['title']
            
            self.log_message(f"Channel: {channel_name}", "green")
            
            # Get uploads playlist ID
            uploads_playlist_id = channel_info['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos
            videos = []
            next_page_token = None
            total_processed = 0
            
            while total_processed < self.max_videos.get() and self.is_scraping:
                # Get video IDs from playlist
                playlist_response = youtube.playlistItems().list(
                    playlistId=uploads_playlist_id,
                    part='contentDetails',
                    maxResults=min(50, self.max_videos.get() - total_processed),
                    pageToken=next_page_token
                ).execute()
                
                video_ids = [item['contentDetails']['videoId'] 
                           for item in playlist_response['items']]
                
                if not video_ids:
                    break
                
                # Get video details in batches
                for i in range(0, len(video_ids), 50):
                    if not self.is_scraping:
                        break
                    
                    batch = video_ids[i:i+50]
                    
                    videos_response = youtube.videos().list(
                        id=','.join(batch),
                        part='snippet,statistics,contentDetails'
                    ).execute()
                    
                    for video in videos_response['items']:
                        if not self.is_scraping:
                            break
                        
                        video_data = self.process_api_video(video, channel_name, channel_id)
                        videos.append(video_data)
                        total_processed += 1
                        
                        self.update_progress(total_processed, self.max_videos.get())
                        self.log_message(f"Processed: {video_data['title'][:50]}...")
                        
                        if total_processed >= self.max_videos.get():
                            break
                    
                    if total_processed >= self.max_videos.get():
                        break
                
                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token:
                    break
            
            return videos
            
        except Exception as e:
            self.log_message(f"API Error: {str(e)}", "red")
            return []
    
    def process_api_video(self, video, channel_name, channel_id):
        """Process video data from API response"""
        video_data = {
            'video_id': video['id'],
            'video_url': f"https://www.youtube.com/watch?v={video['id']}",
            'title': video['snippet']['title'],
            'description': video['snippet']['description'][:500],
            'views': int(video['statistics'].get('viewCount', 0)),
            'likes': int(video['statistics'].get('likeCount', 0)),
            'comments': int(video['statistics'].get('commentCount', 0)),
            'duration': video['contentDetails']['duration'],
            'upload_date': video['snippet']['publishedAt'],
            'channel_name': channel_name,
            'channel_id': channel_id,
            'transcript': ''
        }
        
        # Get transcript if requested
        if self.include_transcript.get():
            try:
                transcript = self.get_video_transcript(video['id'])
                video_data['transcript'] = transcript[:5000]
            except:
                video_data['transcript'] = "Not available"
        
        return video_data
    
    # ----------------------------------------------------------------------
    # TRANSCRIPT METHODS
    # ----------------------------------------------------------------------
    
    def get_video_transcript(self, video_id):
        """
        Fetch transcript for a YouTube video.
        1) Try manual captions
        2) Try auto-generated captions
        3) Fallback to Whisper audio transcription (works for Shorts)
        """
        
        # ---------- TRY YOUTUBE CAPTIONS ----------
        if TRANSCRIPT_AVAILABLE:
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

                # Prefer manually created captions
                for transcript in transcript_list:
                    if not transcript.is_generated:
                        return " ".join([item["text"] for item in transcript.fetch()])

                # Fallback to auto-generated captions
                for transcript in transcript_list:
                    if transcript.is_generated:
                        return " ".join([item["text"] for item in transcript.fetch()])

            except Exception:
                pass  # Continue to Whisper fallback

        # ---------- WHISPER FALLBACK (SHORTS SAFE) ----------
        try:
            self.log_message(f"🎧 Transcribing audio with Whisper: {video_id}", "orange")

            with tempfile.TemporaryDirectory() as tmp:
                audio_path = os.path.join(tmp, "audio.mp3")

                # Download audio using yt-dlp
                subprocess.run(
                    [
                        "yt-dlp",
                        "-f", "bestaudio",
                        "-x",
                        "--audio-format", "mp3",
                        "-o", audio_path,
                        f"https://www.youtube.com/watch?v={video_id}"
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                if not os.path.exists(audio_path):
                    return "Transcript unavailable (audio download failed)"

                # Transcribe with Whisper
                model = whisper.load_model("base")
                result = model.transcribe(audio_path)

                return result.get("text", "Transcript unavailable")

        except Exception as e:
            return f"Transcript unavailable: {str(e)}"
    
    # ----------------------------------------------------------------------
    # Main Scraping Function
    # ----------------------------------------------------------------------
    
    def scrape_channel(self, channel_url, output_file):
        """Main scraping function"""
        try:
            self.log_message("Starting YouTube Channel Scraper...", "green")
            self.log_message(f"URL: {channel_url}")
            self.log_message(f"Method: {self.scrape_method.get().upper()}")
            self.log_message(f"Max Videos: {self.max_videos.get()}")
            
            videos = []
            
            if self.scrape_method.get() == "api" and self.api_key and YOUTUBE_API_AVAILABLE:
                self.log_message("Using YouTube Data API...", "blue")
                videos = self.scrape_with_api(channel_url, output_file)
            else:
                self.log_message("Using Web Scraping method...", "blue")
                # Extract channel ID
                channel_id = self.extract_channel_id_web(channel_url)
                if not channel_id:
                    raise ValueError("Could not extract channel ID from URL")
                
                self.log_message(f"Found Channel ID: {channel_id}", "green")
                videos = self.get_channel_videos_web(channel_id, self.max_videos.get())
            
            # Save to CSV
            if videos and self.is_scraping:
                self.log_message(f"Saving {len(videos)} videos to CSV...", "green")
                
                df = pd.DataFrame(videos)
                
                # Ensure output file has .csv extension
                if not output_file.lower().endswith('.csv'):
                    output_file += '.csv'
                
                df.to_csv(output_file, index=False, encoding='utf-8-sig')
                
                self.log_message(f"✅ Data saved successfully!", "green")
                self.log_message(f"📁 File: {output_file}", "green")
                self.log_message(f"📊 Total videos: {len(videos)}", "green")
                self.log_message(f"📋 Columns: {', '.join(df.columns)}", "green")
                
                # Show summary
                messagebox.showinfo("Success", 
                    f"✅ Successfully scraped {len(videos)} videos\n"
                    f"📁 Saved to: {output_file}\n"
                    f"📊 Columns: {len(df.columns)}")
                
            elif not self.is_scraping:
                self.log_message("Scraping stopped by user", "orange")
            else:
                self.log_message("No video data was scraped", "orange")
            
        except Exception as e:
            self.log_message(f"❌ Error during scraping: {str(e)}", "red")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        finally:
            self.on_scraping_finished()
    
    def on_scraping_finished(self):
        """Clean up after scraping"""
        self.is_scraping = False
        self.scrape_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_label.config(text="Ready")
        self.progress_var.set(0)

def main():
    root = tk.Tk()
    
    # Set style
    style = ttk.Style()
    style.theme_use('clam')
    
    app = YouTubeChannelScraper(root)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()