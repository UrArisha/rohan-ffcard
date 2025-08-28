from PIL import Image, ImageDraw, ImageFont
import os
import uuid
import json
import requests
from io import BytesIO

def handler():
    # ইনপুট পড়া
    input_data = json.loads(os.environ.get('BODY', '{}'))
    text = input_data.get('text', 'Hello, World!')
    pos_x = int(input_data.get('position_x', 207))
    pos_y = int(input_data.get('position_y', 47))

    # বেস ইমেজ লোড (রুট ডিরেক্টরি থেকে)
    base_image_path = os.path.join(os.path.dirname(__file__), 'Photo.png')
    img = Image.open(base_image_path)
    
    # ড্রয়িং অবজেক্ট
    draw = ImageDraw.Draw(img)
    
    # ফন্ট সেট করা
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    # টেক্সট যোগ করা
    draw.text((pos_x, pos_y), text, fill="black", font=font)

    # ছবি মেমরিতে সেভ করা
    img_buffer = BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    # ImgBB API কী (Vercel Environment Variable থেকে)
    IMGBB_API_KEY = os.environ.get('IMGBB_API_KEY', 'your-imgbb-api-key')  # Vercel-এ সেট করুন

    # ImgBB-তে আপলোড
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_API_KEY,
        "name": f"output-{uuid.uuid4()}.png"
    }
    files = {
        "image": ("image.png", img_buffer, "image/png")
    }
    
    response = requests.post(url, data=payload, files=files)
    
    if response.status_code == 200:
        imgbb_data = response.json()
        image_url = imgbb_data["data"]["url"]
        return {
            "statusCode": 200,
            "body": json.dumps({"image_url": image_url})
        }
    else:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to upload image to ImgBB"})
        }

if __name__ == "__main__":
    print(handler())
