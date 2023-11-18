import requests
from bs4 import BeautifulSoup
from pathlib import Path
import io
from urllib.parse import urlparse, parse_qs
from pytube import YouTube
import uuid


def generate_random_file_id():
    # Generate a random UUID and convert it to a string
    file_id = str(uuid.uuid4())

    return file_id

class TwitterDownloader:
    # THANKS erfanhs https://gist.github.com/erfanhs/2e08840db47dce4da7e08f78dda23c4c

    def __init__(self):

        self.session = requests.Session()
        self.csrf = self.session.get('http://twittervideodownloader.com').cookies['csrftoken']


    def download_video(self, tweet_url,output):

        tweet_url = tweet_url.split('?', 1)[0]

        result = self.session.post('http://twittervideodownloader.com/download', data={'tweet': tweet_url, 'csrfmiddlewaretoken': self.csrf})

        if result.status_code == 200:

            bs = BeautifulSoup(result.text, 'html.parser')
            video_element = bs.find('a', string='Download Video')

            if video_element is None:
                print('video not found !')
            else:
                video_url = video_element['href']
                tweet_id = tweet_url.split('/')[-1]
                fname = tweet_id + '.mp4'

                download_result = self.session.get(video_url, stream = True)

                with open(output,"wb") as f:
                    for chunk in download_result.iter_content(chunk_size=1024*1024):
                        if chunk:
                            f.write(chunk)

        else:
            return('an error in downloading video! status code: ' + result.status_code)

class TiktokDownloader:

    @staticmethod
    def download(url:str,output:str):
        video_id = url.split("video/")[1].split("?")[0]

        if video_id:
            print(video_id)
            # Construct a new URL
            tiktok_url = f"https://tikcdn.io/ssstik/{video_id}"

            # Make the request and handle errors
            try:
                r = requests.get(url=tiktok_url,stream=True)
                r.raise_for_status()  # Raise an exception for bad responses
                print(r.status_code)
                # Download the content into a BytesIO object
                with open(output,"wb") as f:
                    for chunk in r.iter_content(chunk_size=1024*1024):
                        if chunk:
                            f.write(chunk)
                return output
            except requests.exceptions.RequestException     as e:
                return False
        else:
            return False

class YoutubeDownloader:

    @staticmethod
    def download(url:str,output):
        try:
            # Create a YouTube object
            video_stream = YouTube(url).streams.get_highest_resolution()
            video_stream.download(output_path=".",filename=output)
            return True
        except Exception as e:
            return(f"Error: {e}")

#if __name__ == "__main__":
    #twitter = TwitterDownloader()
    #twitter.download_video(tweet_url="https://x.com/RassdNewsN/status/1725931876043341953?s=20",output=generate_random_file_id()+".mp4")
    #TiktokDownloader.download(url="https://www.tiktok.com/@hazim_shwman1/video/7292853003709664518?is_from_webapp=1&sender_device=pc",output=generate_random_file_id()+".mp4")
    #d = YoutubeDownloader.download(url="https://www.youtube.com/shorts/72MYQo4IUNg",output_path=generate_random_file_id()+".mp4")
    #print(d)
