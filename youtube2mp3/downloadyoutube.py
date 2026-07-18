def youtubedlp(youtube_url, download_path):
    import yt_dlp
    import os

    URLS = [youtube_url]
    
    # Ensure download_path is absolute and clean
    download_path = os.path.abspath(download_path)

    ydl_opts = {
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        },
        'format': 'm4a/bestaudio/best',
        'postprocessors': [{  
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }],
        # os.path.join prevents the folder name and filename from mashing together!
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'noplaylist': True,
        'retries': 10,  
        'fragment_retries': 10,  
        'sleep_interval': 1,  
        'max_sleep_interval': 5  
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # 1. Download and extract info in one clean go
        info = ydl.extract_info(URLS[0], download=True)
        
        # 2. Safely get the absolute path of the downloaded file
        requested_downloads = info.get('requested_downloads', [])
        if requested_downloads:
            file_path = requested_downloads[0].get('filepath')
        else:
            # Safe fallback if 'requested_downloads' is empty
            filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(filename)
            file_path = f"{base}.m4a"
            
        # Double-check that we are returning an absolute path
        file_path = os.path.abspath(file_path)

    print("Successfully downloaded to:", file_path)
    return info, file_path