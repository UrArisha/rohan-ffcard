from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image, ImageDraw, ImageFont
import io
import requests
from urllib.parse import urlparse

app = FastAPI()

# ImgBB থেকে ছবির URL
BASE_IMAGE_URL = "https://ibb.co.com/Q4FdmSh"

@app.post("/add-text-to-photo/")
async def add_text_to_photo(
    text: str = "আপনার টেক্সট",
    position_x: int = 207,
    position_y: int = 47,
    font_size: int = 40,
    text_color: str = "white"
):
    try:
        # ImgBB থেকে ছবি ডাউনলোড
        response = requests.get(BASE_IMAGE_URL, stream=True)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content)).convert("RGBA")

        # ড্র করার জন্য অবজেক্ট তৈরি
        draw = ImageDraw.Draw(image)

        # ডিফল্ট ফন্ট (কাস্টম .ttf ফন্ট যোগ করতে পারেন)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        # ছবিতে টেক্সট যোগ
        draw.text((position_x, position_y), text, fill=text_color, font=font)

        # পরিবর্তিত ছবি সেভ করা
        output = io.BytesIO()
        image.save(output, format="PNG")
        output.seek(0)

        # ছবি রেজাল্ট হিসেবে ফেরত
        return StreamingResponse(output, media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ত্রুটি: {str(e)}")

@app.get("/")
async def root():
    return {"message": "POST /add-text-to-photo/ ব্যবহার করে ছবিতে টেক্সট যোগ করুন।"}
