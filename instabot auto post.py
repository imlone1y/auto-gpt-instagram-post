import openai
import requests
from instabot import Bot
import os
from PIL import Image
import shutil

# remove the json file which in the config dir.
os.remove(r"path\to\the\cookie json file")

# openai api key / username / password
openai.api_key = 'your openai api key'
instagram_username = os.getenv('username')
instagram_password = os.getenv('password')

# iinitialize Instagram bot
bot = Bot()
bot.login(username=instagram_username, password=instagram_password)

# define funtion for gpt to generate caption
def generate_caption():
    prompt = "Generate an Instagram caption."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a helpful assistant that generates interesting Instagram caption."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# using dall-e-2 model to generate picture
def generate_image_from_text(text):
    response = openai.Image.create(
        model="dall-e-2",
        prompt=text,
        n=1,
        size="1024x1024"
    )
    image_data = response.data[0].url
    return image_data

# define function to download picture
def download_image(image_url, image_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(image_path, 'wb') as f:
            f.write(response.content)
        # 转换图片格式为jpeg
        convert_jpg_to_jpeg(image_path)
    else:
        print(f"Failed to download image, status code: {response.status_code}")

# due to instabot only upload jpeg pictures, not jpg
def convert_jpg_to_jpeg(image_path):
    # using pillow to open image
    img = Image.open(image_path)
    # if the file is not jpeg, then convert to jpeg
    if img.format != 'JPEG':
        jpeg_path = image_path.rsplit('.', 1)[0] + '.jpeg'
        img.save(jpeg_path, "JPEG")
        os.remove(image_path)  # delete original file
        return jpeg_path
    return image_path

# post function
def post_once():
    # generate caption
    caption = generate_caption()
    
    # using dall-e-2 to generate picture, and download to desktop
    image_url = generate_image_from_text(caption)
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')  # get path to desktop
    image_path = os.path.join(desktop_path, 'instagram_post.jpg')  # set the path that the picture saved
    downloaded_image_path = download_image(image_url, image_path)
    
    # upload everything on Instagram
    if bot.upload_photo(r"path\to\Desktop\instagram_post.jpeg", caption=caption):
        print("Post successful:", caption)
    else:
        print("Failed to post on Instagram.")

# run the program
post_once()
