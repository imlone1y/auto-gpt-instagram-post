import openai
import requests
from instabot import Bot
import os
from PIL import Image
import shutil


def delete_and_recreate_folder(folder_path):
    # 删除整个文件夹
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"'{folder_path}' has been deleted.")
    
    # 重新创建同名文件夹
    os.makedirs(folder_path)
    print(f"Empty '{folder_path}' has been recreated.")

# 调用函数，替换下面的路径为您的`config`文件夹的实际路径
config_folder_path = r'C:\Users\justi\config'
delete_and_recreate_folder(config_folder_path)


# 建议使用环境变量来管理敏感信息
openai.api_key = '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'
instagram_username = os.getenv('daily_gpt_auto_post')
instagram_password = os.getenv('chatgpt123')

# 初始化Instagram bot
bot = Bot()
bot.login(username=instagram_username, password=instagram_password)

# 从ChatGPT生成文案的函数
def generate_caption():
    prompt = "Generate an Instagram caption, about some fun fact."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# 使用DALL·E 3生成图片的函数
def generate_image_from_text(text):
    response = openai.Image.create(
        model="dall-e-2",
        prompt=text,
        n=1,
        size="1024x1024"
    )
    image_data = response.data[0].url
    return image_data

# 下载图片的函数
def download_image(image_url, image_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(image_path, 'wb') as f:
            f.write(response.content)
        # 转换图片格式为jpeg
        convert_jpg_to_jpeg(image_path)
    else:
        print(f"Failed to download image, status code: {response.status_code}")

def convert_jpg_to_jpeg(image_path):
    # 使用Pillow打开jpg图片
    img = Image.open(image_path)
    # 如果图片不是JPEG格式，则转换
    if img.format != 'JPEG':
        jpeg_path = image_path.rsplit('.', 1)[0] + '.jpeg'
        img.save(jpeg_path, "JPEG")
        os.remove(image_path)  # 删除原jpg文件
        return jpeg_path
    return image_path

# 执行发布流程的函数
def post_once():
    # 生成文案
    caption = generate_caption()
    
    # 使用DALL·E 2生成图片，并指定保存路径到桌面
    image_url = generate_image_from_text(caption)
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')  # 获取桌面路径
    image_path = os.path.join(desktop_path, 'instagram_post.jpg')  # 指定图片保存位置
    downloaded_image_path = download_image(image_url, image_path)
    
    # 上传图片到Instagram
    if bot.upload_photo(r"C:\Users\justi\Desktop\instagram_post.jpeg", caption=caption):
        print("Post successful:", caption)
    else:
        print("Failed to post on Instagram.")
    # 清理由instabot创建的临时文件
    try:
        os.remove("instagram_post.jpeg")
    except:
        pass

# 调用执行函数
post_once()