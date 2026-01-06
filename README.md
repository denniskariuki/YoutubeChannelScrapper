YouTube Channel Scraper
A powerful desktop application for scraping YouTube channel data with transcript extraction capabilities. 
This tool allows you to extract video details and transcripts from any YouTube channel by simply pasting the channel URL.

✨ Features
📊 Data Extraction
Video Metadata: Title, description, views, likes, comments, duration, upload date

Channel Information: Channel name, ID, handle

Transcript Support: Automatic transcript extraction using multiple methods

Multi-format Export: CSV, Excel, and JSON export options

🔄 Multiple Scraping Methods
Web Scraping: No API key required, works immediately

YouTube API: More reliable data with official API (requires key)

🎯 Advanced Features
Smart Transcript Extraction:

Manual captions (highest priority)

Auto-generated captions

Whisper AI fallback for videos without captions

Works with YouTube Shorts

Batch Processing: Scrape up to 500 videos at once

Progress Tracking: Real-time progress bar and detailed logs

Data Preview: Preview scraped data before export

User-Friendly GUI: Modern interface with color-coded logs

📸 Screenshot
<img width="1013" height="831" alt="image" src="https://github.com/user-attachments/assets/27d7b730-dc41-4f97-b0fa-4810af6a17cf" />


🚀 Installation
Prerequisites
Python 3.8 or higher

Method 1: Quick Install (Recommended)
bash
# Clone the repository
git clone https://github.com/yourusername/youtube-channel-scraper.git
cd youtube-channel-scraper

# Install dependencies
pip install -r requirements.txt

# Run the application
python youtube_scraper.py
Method 2: Manual Installation
bash
# Install core dependencies
pip install google-api-python-client youtube-transcript-api pandas requests beautifulsoup4

# Install Whisper for transcript fallback
pip install openai-whisper yt-dlp

# Install GUI dependencies (usually pre-installed with Python)
# If you get tkinter errors:
# Ubuntu/Debian: sudo apt-get install python3-tk
# Fedora: sudo dnf install python3-tkinter
# Arch: sudo pacman -S tk

Full Requirements File (requirements.txt)
txt
google-api-python-client>=2.80.0
youtube-transcript-api>=0.6.0
pandas>=2.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0
openai-whisper>=20231117
yt-dlp>=2023.10.13
isodate>=0.6.1

🎮 Usage
Getting Started
Launch the Application:

bash
python youtube_scraper.py
Choose Scraping Method:

Web Scraping: No API key needed (recommended for beginners)

YouTube API: More reliable, requires API key

Enter Channel URL:

Supported formats:

https://www.youtube.com/@ChannelName

https://www.youtube.com/channel/UC...

https://www.youtube.com/c/CustomName

https://www.youtube.com/user/Username

Configure Options:

Set maximum videos to scrape (1-500)

Choose to include transcripts

Select output file location

Start Scraping:

Click "🚀 Start Scraping"

Monitor progress in real-time

Preview data before saving

Getting YouTube API Key (Optional)
For API method, get a free API key:

Go to Google Cloud Console

Create a new project

Enable YouTube Data API v3

Create credentials (API Key)

Copy the API key to the application

📁 Output Format
CSV Columns
The tool exports data with these columns:

Column	Description
video_id	YouTube video ID
video_url	Full YouTube URL
title	Video title
description	Video description (truncated)
views	View count
likes	Like count
comments	Comment count
duration	Video duration
upload_date	Publication date
channel_name	Channel name
channel_id	Channel ID
transcript	Full transcript (if available)
Sample Output
csv
video_id,title,views,likes,duration,transcript
dQw4w9WgXcQ,Never Gonna Give You Up,1500000000,12000000,PT3M30S,"We're no strangers to love..."

🔧 Advanced Configuration
Command Line Usage
bash
# Basic usage
python youtube_scraper.py

# With specific channel URL
python youtube_scraper.py --url "https://www.youtube.com/@ChannelName"

# With API key
python youtube_scraper.py --method api --api-key "YOUR_API_KEY"

# Set maximum videos
python youtube_scraper.py --max 100 --output "data.csv"
Environment Variables
bash
# Set default API key
export YOUTUBE_API_KEY="your_api_key_here"

# Set default output directory
export YOUTUBE_OUTPUT_DIR="/path/to/output"
🤖 How Transcript Extraction Works
3-Stage Transcript Pipeline
Stage 1: YouTube Captions API ✅

First tries manual captions (most accurate)

Falls back to auto-generated captions

Fastest method when available

Stage 2: Whisper AI 🔊

Downloads audio using yt-dlp

Transcribes using OpenAI's Whisper model

Works for Shorts and videos without captions

Supports multiple languages

Stage 3: Fallback ⚠️

Returns "Transcript not available" if all methods fail

⚠️ Important Notes
Legal Considerations
Terms of Service: This tool is for educational purposes

Rate Limits: Respect YouTube's rate limits

Data Usage: Use scraped data responsibly

Commercial Use: Check YouTube's Terms of Service for commercial use

Limitations
YouTube API has daily quotas (10,000 units/day free tier)

Transcripts not available for all videos

Some channels may restrict access

Very large channels may take time to process

🛠️ Troubleshooting
Common Issues
"No videos found"

Check if channel has public videos

Try Web Scraping method instead of API

Verify URL format

"API Error: quotaExceeded"

You've exceeded YouTube API quota

Switch to Web Scraping method

Wait 24 hours or upgrade quota

"Transcript unavailable"

Video may have no captions

Try disabling transcript option

Check Whisper installation

"tkinter not found"


# Windows (usually pre-installed)
Slow Performance

Reduce maximum videos

Disable transcript extraction

Close other applications

Logs and Debugging
Check the application logs for detailed error messages. Enable debug mode for more information:

python
# Add to the beginning of your script
import logging
logging.basicConfig(level=logging.DEBUG)
📊 Performance Tips
For Large Channels (>100 videos)

Set reasonable limits (50-100 videos)

Disable transcripts for faster scraping

Use API method for reliability

For Transcript Extraction

Use base Whisper model for speed

Consider small or medium for better accuracy

Transcripts add 30-60 seconds per video

Memory Usage

Close other applications during scraping

Increase max videos gradually

Export data periodically

🤝 Contributing
We welcome contributions! Here's how:

Fork the repository

Create a feature branch

bash
git checkout -b feature/amazing-feature
Make your changes

Test thoroughly

Submit a pull request

Areas for Contribution
Add support for more export formats

Improve error handling

Add batch processing

Create CLI-only version

Add multilingual support

Running Tests
bash
# Install test dependencies
pip install pytest

# Run tests
pytest tests/
Building Executable
bash
# Install PyInstaller
pip install pyinstaller

# Build standalone executable
pyinstaller --onefile --windowed youtube_scraper.py
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
YouTube Data API v3 by Google

OpenAI Whisper for speech recognition

youtube-transcript-api

yt-dlp for video downloading

⭐ Support
If you find this project useful, please consider:

⭐ Starring the repository on GitHub

🐛 Reporting bugs and issues

💡 Suggesting new features

📢 Sharing with others

📞 Contact
GitHub Issues: Report bugs or request features

Email: denkarish@gmail.com
Disclaimer: This tool is for educational and research purposes only. Users are responsible for complying with YouTube's Terms of Service and applicable laws. The developers are not responsible for any misuse of this tool.
