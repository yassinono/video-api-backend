# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp
import asyncio

# إعداد التطبيق
app = FastAPI(title="Video Extractor API")

# نموذج لبيانات الطلب
class VideoRequest(BaseModel):
    url: str

# نقطة النهاية (Endpoint) الرئيسية
@app.post("/extract")
async def extract_video_info(request: VideoRequest):
    ydl_opts = {'quiet': True, 'no_warnings': True}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, request.url, download=False)

        # تجهيز قائمة بالجودات وروابطها المباشرة
        formats_list = []
        for f in info.get('formats', []):
            # نختار فقط الجودات المدمجة (فيديو وصوت) التي لها رابط مباشر
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                formats_list.append({
                    'resolution': f.get('resolution'),
                    'ext': f.get('ext'),
                    'url': f.get('url') # رابط التحميل المباشر
                })

        # في حال لم نجد جودات مدمجة (مثل بعض فيديوهات يوتيوب عالية الدقة)
        # سنقوم بتوفير أفضل جودة فيديو وأفضل جودة صوت بشكل منفصل
        if not formats_list:
            best_video = next((f for f in info.get('formats', []) if f.get('vcodec') != 'none' and f.get('url')), None)
            best_audio = next((f for f in info.get('formats', []) if f.get('acodec') != 'none' and f.get('url')), None)
            if best_video: formats_list.append({'resolution': best_video.get('resolution'), 'ext': best_video.get('ext'), 'url': best_video.get('url'), 'type': 'video_only'})
            if best_audio: formats_list.append({'resolution': 'audio', 'ext': best_audio.get('ext'), 'url': best_audio.get('url'), 'type': 'audio_only'})


        # تجهيز الرد النهائي
        return {
            "title": info.get('title'),
            "thumbnail": info.get('thumbnail'),
            "duration_string": info.get('duration_string'),
            "formats": formats_list
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def root():
    return {"status": "API is Online"}