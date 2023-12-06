import tkinter as tk
import re
import json
import requests
import os

from tkinter import ttk
from PIL import Image
from io import BytesIO
from urllib.request import Request, urlopen
from pathlib import Path
from tkinter import scrolledtext


class ShopeeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shopee downloader")
        self.root.geometry("800x600")
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'
        }

        # URL Entry
        self.url_label = ttk.Label(root, text="Enter URL:")
        self.url_label.pack(pady=5)
        self.url_entry = ttk.Entry(root, width=50)
        self.url_entry.pack()

        # Download Button
        self.download_button = ttk.Button(
            root, text="Download images and videos", command=self.process)
        self.download_button.pack(pady=10)

        # Log Text
        self.log_text = scrolledtext.ScrolledText(
            root, width=100, height=50, state="disabled")
        self.log_text.pack(padx=10, pady=10)

        # self.log_text.config(state="normal")

    # def get_soup(self, url):
    #     return BeautifulSoup(urlopen(Request(url=url, headers=self.header)), 'html.parser')

    def extract_item_id_shop_id_from_url(self, url):
        pattern = r'i\.\d+\.\d+'
        match = re.search(pattern, url)
        if match:
            # Extract and print the 'id' number
            id_number = match.group()
            return id_number
        else:
            return None

    def save_img(self, image_url, id):
        # self.log_text.config(state="normal")
        print(image_url)
        image_name = os.path.basename(image_url)

        response = requests.get(image_url, headers=self.header)

        if response.status_code == 200:
            image_data = response.content
            image_stream = BytesIO(image_data)
            img = Image.open(image_stream)
            save_directory = os.path.join('data', id)
            save_path = os.path.join(save_directory, image_name)
            os.makedirs(save_directory, exist_ok=True)
            img.save(save_path)

            self.log_text.insert(tk.END, f"Image saved as {save_path} \n")
        else:
            self.log_text.insert(
                tk.END, f"Failed to download image. Status code: {response.status_code} \n")

        # self.log_text.config(state="disabled")

    def save_video(self, video_url, id):
        self.log_text.config(state="normal")
        print(video_url)
        video_name = os.path.basename(video_url)
        response = requests.get(video_url, headers=self.header)
        if response.status_code == 200:
            save_directory = os.path.join('data', id)
            os.makedirs(save_directory, exist_ok=True)
            save_path = os.path.join(save_directory, video_name)
            with open(save_path, "wb") as video_file:
                video_file.write(response.content)

            self.log_text.insert(tk.END, f"Video saved as {save_path} \n")
        else:
            self.log_text.insert(
                tk.END, f"Failed to download video. Status code: {response.status_code} \n")
        # self.log_text.config(state="disabled")

    def get_rating_data(self, params):
        rating_api_url = 'https://shopee.vn/api/v2/item/get_ratings'
        return requests.get(url=rating_api_url, params=params).json()

    def process_recursive(self, params, offset, item_id):
        rating_json = self.get_rating_data(params=params)
        if rating_json is not None:
            rating_data = rating_json['data']
            if 'has_more' in rating_data.keys() and rating_data['has_more']:
                list_ratings = rating_data['ratings']
                for rating in list_ratings:
                    images = rating['images']
                    videos = rating['videos']
                    if len(images) > 0:
                        for image in images:
                            image_url = f'https://down-ws-vn.img.susercontent.com/{image}_tn.webp'
                            self.save_img(image_url, item_id)
                    if len(videos) > 0:
                        for video in videos:
                            video_url = video['url']
                            self.save_video(video_url, item_id)
                offset += 1
                params['offset'] = offset
                self.process_recursive(params, offset, item_id)

    def process(self):
        self.log_text.config(state="normal")
        url = self.url_entry.get()
        id_number = self.extract_item_id_shop_id_from_url(url)
        if id_number:
            id_number_split = id_number.split('.')
            item_id = id_number_split[2]
            shop_id = id_number_split[1]
            self.log_text.insert(tk.END, f"Item ID: {item_id} \n")
            self.log_text.insert(tk.END, f"Shop ID: {shop_id} \n")
            offset = 0
            params = {
                'exclude_filter': 1,
                'filter': 3,
                'filter_size': 0,
                'flag': 1,
                'fold_filter': 0,
                'itemid': item_id,
                'limit': 6,
                'offset': offset,
                'relevant_reviews': False,
                'request_source': 2,
                'shopid': shop_id,
                'tag_filter': '',
                'type': 0,
                'variation_filters': ''
            }
            self.process_recursive(params, offset, item_id)
            self.log_text.insert(tk.END, f"Done")
        else:
            self.log_text.insert(tk.END, f"No item ID found")


if __name__ == "__main__":
    root = tk.Tk()
    app = ShopeeDownloaderApp(root)
    root.mainloop()
