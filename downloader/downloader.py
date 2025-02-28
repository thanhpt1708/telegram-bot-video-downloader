import os

import yt_dlp

from logger import logger

FFMPEG_PATH = "/usr/local/bin/ffmpeg"
TMP_DIR = "/tmp"


class Downloader:
    def __init__(self, url):
        self.url = url

    def extract_info(self):
        try:
            with yt_dlp.YoutubeDL() as ydl:
                return ydl.extract_info(self.url, download=False)
        except Exception as e:
            logger.error(f"Error extract_info {self.url}: {str(e)}")
            return None

    def download(self):
        try:
            # First, extract info without downloading to get the title
            ydl_opts_info = {
                "quiet": True,
                "no_warnings": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(self.url, download=False)
                video_title = info.get("title")
                output_template = os.path.join(TMP_DIR, f"{video_title}.%(ext)s")

            # Now download with the sanitized title as filename
            ydl_opts = {
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "outtmpl": output_template,
                "merge_output_format": "mp4",
                "ffmpeg_location": FFMPEG_PATH,
                "quiet": True,
                "no_warnings": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                file_path = ydl.prepare_filename(info).replace(".mkv", ".mp4").replace(".webm", ".mp4")
                if not os.path.exists(file_path):
                    file_path = os.path.join(TMP_DIR, f"{video_title}.mp4")
                if os.path.exists(file_path):
                    logger.info(f"Successfully downloaded video to {file_path}")
                    return file_path
                else:
                    logger.error(f"Download completed but file not found at {file_path}")
                    return None
        except Exception as e:
            logger.error(f"Error downloading video {self.url}: {str(e)}")
            return None
