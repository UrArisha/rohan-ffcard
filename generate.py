import os
import aiohttp
import json
import base64
import logging

# লগিং সেটআপ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# কনফিগারেশন
JSON_FILE_PATH = "uploaded_data.json"
OUTPUT_FILE_PATH = "token_bd.json"
GITHUB_OWNER = "UrArisha"
GITHUB_REPO = "Arisha-s-Like-bot"
GITHUB_FILE_PATH = "token_bd.json"
GITHUB_BRANCH = "main"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")  # Vercel এনভায়রনমেন্ট ভেরিয়েবল থেকে নেওয়া

# টোকেন ফেচ করা
async def fetch_token(session, uid, password):
    url = f"http://jwt.thug4ff.com/token?uid={uid}&password={password}"
    try:
        async with session.get(url, timeout=5) as resp:
            if "application/json" not in resp.headers.get("Content-Type", ""):
                text = await resp.text()
                logger.error(f"UID {uid} ফেচ ত্রুটি: JSON প্রত্যাশিত, পাওয়া গেছে {text[:200]}")
                return {"uid": uid, "token": None}
            data = await resp.json()
            return {"uid": uid, "token": data.get("token")}
    except Exception as e:
        logger.error(f"UID {uid} ফেচ ব্যতিক্রম: {e}")
        return {"uid": uid, "token": None}

# GitHub-এ ফাইল আপলোড
async def update_github(file_path):
    async with aiohttp.ClientSession() as session:
        url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
        with open(file_path, "rb") as f:
            content = f.read()
        encoded = base64.b64encode(content).decode("utf-8")
        async with session.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"}) as r:
            data = await r.json()
            sha = data.get("sha")
        payload = {"message": "অটো-আপডেট টোকেন", "content": encoded, "branch": GITHUB_BRANCH}
        if sha:
            payload["sha"] = sha
        async with session.put(url, headers={"Authorization": f"token {GITHUB_TOKEN}"}, json=payload) as r:
            if r.status in [200, 201]:
                logger.info("✅ GitHub আপলোড সফল")
                return True
            else:
                logger.error(f"GitHub আপলোড ব্যর্থ: {await r.text()}")
                return False

# টোকেন জেনারেট এবং আপলোড
async def generate_and_upload():
    if not os.path.exists(JSON_FILE_PATH):
        return {"status": "error", "message": "uploaded_data.json ফাইল পাওয়া যায়নি"}
    
    async with aiohttp.ClientSession() as session:
        with open(JSON_FILE_PATH, "r") as f:
            users = json.load(f)
        results = []
        for user in users:
            if "uid" in user and "password" in user:
                results.append(await fetch_token(session, user["uid"], user["password"]))
        with open(OUTPUT_FILE_PATH, "w") as f:
            json.dump(results, f, indent=4)
        success = await update_github(OUTPUT_FILE_PATH)
        return {
            "status": "success" if success else "error",
            "message": f"টোকেন জেনারেশন এবং GitHub আপলোড সম্পন্ন ({len(results)} টোকেন)" if success else "GitHub আপলোড ব্যর্থ",
            "tokens": results
        }

# Vercel serverless ফাংশন
def handler(request):
    import asyncio
    try:
        value = request.args.get("value")
        if value != "1":
            return {
                "statusCode": 400,
                "body": json.dumps({"status": "error", "message": "ভুল ভ্যালু। value=1 ব্যবহার করুন"})
            }
        
        result = asyncio.run(generate_and_upload())
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    except Exception as e:
        logger.error(f"হ্যান্ডলার ত্রুটি: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"status": "error", "message": str(e)})
        }
