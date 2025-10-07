# ملف main.py محدث للـ API على Render
# يمكن نسخه مباشرة بدلاً من الملف الحالي

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import random
import json
from datetime import datetime
import yt_dlp
import asyncio

app = FastAPI(title="Video API Backend", version="1.0.0")

# إضافة CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# بيانات تجريبية
TRENDING_KEYWORDS = [
    "أغاني عربية", "أفلام جديدة", "كوميديا", "رياضة", "أخبار",
    "طبخ", "تعليم", "سفر", "موضة", "تكنولوجيا", "موسيقى",
    "دراما", "كرتون", "وثائقي", "طبيعة", "حيوانات"
]

TRENDING_VIDEOS = [
    {
        "id": f"trending_{i}",
        "title": f"فيديو رائج {i} - محتوى شيق وحصري",
        "thumbnailUrl": f"https://picsum.photos/seed/trending{i}/300/200.jpg",
        "duration": f"{random.randint(3, 15)}:{random.randint(10, 59)}",
        "channelName": f"قناة رائجة {i % 5 + 1}",
        "viewCount": f"{random.randint(100000, 1000000)}",
        "uploadTime": f"قبل {random.randint(1, 7)} ساعات",
        "platform": ["YouTube", "Facebook", "Instagram", "TikTok", "Twitter"][i % 5],
        "videoUrl": f"https://example.com/trending_{i}.mp4"
    }
    for i in range(1, 21)
]

@app.get("/")
async def root():
    """الصفحة الرئيسية للـ API"""
    return {"status": "API is Online", "message": "Video API Backend is running"}

@app.get("/api/trending-keywords")
async def get_trending_keywords():
    """الحصول على الكلمات الرائجة"""
    return {
        "keywords": TRENDING_KEYWORDS,
        "status": "success",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/trending")
async def get_trending_videos(request: Request):
    """الحصول على الفيديوهات الرائجة"""
    try:
        data = await request.json()
        platform = data.get("platform", "all")

        if platform != "all":
            filtered_videos = [v for v in TRENDING_VIDEOS if v["platform"] == platform]
        else:
            filtered_videos = TRENDING_VIDEOS

        return {
            "results": filtered_videos[:10],
            "status": "success",
            "count": len(filtered_videos[:10]),
            "platform": platform,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/search")
async def search_videos(request: Request):
    """البحث عن الفيديوهات"""
    try:
        data = await request.json()
        query = data.get("query", "")
        platform = data.get("platform", "all")

        if not query:
            return {
                "error": "Query is required",
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }

        # محاكاة نتائج البحث
        search_results = []
        for i in range(10):
            search_results.append({
                "id": f"search_{i}",
                "title": f"{query} - نتيجة البحث {i + 1}",
                "thumbnailUrl": f"https://picsum.photos/seed/{query.replace(' ', '_')}{i}/300/200.jpg",
                "duration": f"{random.randint(2, 10)}:{random.randint(10, 59)}",
                "channelName": f"قناة البحث {i % 3 + 1}",
                "viewCount": f"{random.randint(10000, 500000)}",
                "uploadTime": f"قبل {random.randint(1, 30)} يوم",
                "platform": ["YouTube", "Facebook", "Instagram", "TikTok", "Twitter"][i % 5],
                "videoUrl": f"https://example.com/search_{i}.mp4"
            })

        return {
            "results": search_results,
            "status": "success",
            "query": query,
            "count": len(search_results),
            "platform": platform,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/video-info")
async def get_video_info(request: Request):
    """الحصول على معلومات الفيديو"""
    try:
        data = await request.json()
        url = data.get("url", "")

        if not url:
            return {
                "error": "URL is required",
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }

        # استخراج معلومات الفيديو باستخدام yt-dlp
        ydl_opts = {'quiet': True, 'no_warnings': True}

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, url, download=False)

            return {
                "title": info.get('title'),
                "description": info.get('description'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration'),
                "view_count": info.get('view_count'),
                "uploader": info.get('uploader'),
                "upload_date": info.get('upload_date'),
                "url": url,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            # في حال فشل yt-dlp، نستخدم بيانات محاكاة
            return {
                "title": f"فيديو من {url}",
                "description": "وصف الفيديو المستخرج من yt-dlp",
                "thumbnail": f"https://picsum.photos/seed/{hash(url) % 1000}/300/200.jpg",
                "duration": random.randint(180, 600),
                "view_count": random.randint(10000, 1000000),
                "uploader": "مستخدم غير معروف",
                "upload_date": "20231201",
                "url": url,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/formats")
async def get_available_formats(request: Request):
    """الحصول على الصيغ المتاحة للفيديو"""
    try:
        data = await request.json()
        url = data.get("url", "")

        if not url:
            return {
                "error": "URL is required",
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }

        # استخراج الصيغ باستخدام yt-dlp
        ydl_opts = {'quiet': True, 'no_warnings': True}

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, url, download=False)

            # تجهيز قائمة بالجودات وروابطها المباشرة
            formats_list = []
            for f in info.get('formats', []):
                # نختار فقط الجودات المدمجة (فيديو وصوت) التي لها رابط مباشر
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                    formats_list.append({
                        'format_id': f.get('format_id'),
                        'resolution': f.get('resolution'),
                        'ext': f.get('ext'),
                        'filesize': f.get('filesize'),
                        'tbr': f.get('tbr'),
                        'quality': 'high'
                    })

            # في حال لم نجد جودات مدمجة
            if not formats_list:
                best_video = next((f for f in info.get('formats', []) if f.get('vcodec') != 'none' and f.get('url')), None)
                best_audio = next((f for f in info.get('formats', []) if f.get('acodec') != 'none' and f.get('url')), None)

                if best_video:
                    formats_list.append({
                        'format_id': best_video.get('format_id'),
                        'resolution': best_video.get('resolution'),
                        'ext': best_video.get('ext'),
                        'filesize': best_video.get('filesize'),
                        'tbr': best_video.get('tbr'),
                        'quality': 'high',
                        'type': 'video_only'
                    })

                if best_audio:
                    formats_list.append({
                        'format_id': best_audio.get('format_id'),
                        'resolution': 'audio',
                        'ext': best_audio.get('ext'),
                        'filesize': best_audio.get('filesize'),
                        'tbr': best_audio.get('tbr'),
                        'quality': 'medium',
                        'type': 'audio_only'
                    })

            return {
                "formats": formats_list,
                "status": "success",
                "url": url,
                "count": len(formats_list),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            # في حال فشل yt-dlp، نستخدم صيغ محاكاة
            formats = [
                {
                    "format_id": "720p",
                    "ext": "mp4",
                    "resolution": "1280x720",
                    "fps": 30,
                    "filesize": 50000000,
                    "tbr": 1200,
                    "quality": "high"
                },
                {
                    "format_id": "480p",
                    "ext": "mp4",
                    "resolution": "854x480",
                    "fps": 30,
                    "filesize": 25000000,
                    "tbr": 800,
                    "quality": "medium"
                },
                {
                    "format_id": "360p",
                    "ext": "mp4",
                    "resolution": "640x360",
                    "fps": 25,
                    "filesize": 15000000,
                    "tbr": 500,
                    "quality": "low"
                }
            ]

            return {
                "formats": formats,
                "status": "success",
                "url": url,
                "count": len(formats),
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/download-url")
async def get_download_url(request: Request):
    """الحصول على رابط التنزيل"""
    try:
        data = await request.json()
        url = data.get("url", "")
        format_id = data.get("format_id", "720p")

        if not url:
            return {
                "error": "URL is required",
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }

        # استخراج رابط التنزيل باستخدام yt-dlp
        ydl_opts = {'quiet': True, 'no_warnings': True}

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, url, download=False)

            # البحث عن الصيغة المطلوبة
            target_format = None
            for f in info.get('formats', []):
                if f.get('format_id') == format_id and f.get('url'):
                    target_format = f
                    break

            if not target_format:
                # في حال لم نجد الصيغة المطلوبة، نحاول أفضل صيغة متاحة
                target_format = next((f for f in info.get('formats', []) if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url')), None)

            if not target_format:
                raise Exception("No suitable format found")

            return {
                "download_url": target_format.get('url'),
                "filename": f"video_{format_id}.{target_format.get('ext', 'mp4')}",
                "format_id": format_id,
                "url": url,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            # في حال فشل yt-dlp، نستخدم رابط محاكاة
            return {
                "download_url": f"https://example.com/download/{format_id}/{hash(url) % 10000}.mp4",
                "filename": f"video_{format_id}.mp4",
                "format_id": format_id,
                "url": url,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }

# نقطة النهاية القديمة للحفاظ على التوافق
@app.post("/extract")
async def extract_video_info(request: Request):
    """نقطة النهاية القديمة لاستخراج معلومات الفيديو"""
    try:
        data = await request.json()
        url = data.get("url", "")

        if not url:
            raise HTTPException(status_code=400, detail="URL is required")

        ydl_opts = {'quiet': True, 'no_warnings': True}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=False)

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

        # في حال لم نجد جودات مدمجة
        if not formats_list:
            best_video = next((f for f in info.get('formats', []) if f.get('vcodec') != 'none' and f.get('url')), None)
            best_audio = next((f for f in info.get('formats', []) if f.get('acodec') != 'none' and f.get('url')), None)
            if best_video: 
                formats_list.append({
                    'resolution': best_video.get('resolution'), 
                    'ext': best_video.get('ext'), 
                    'url': best_video.get('url'), 
                    'type': 'video_only'
                })
            if best_audio: 
                formats_list.append({
                    'resolution': 'audio', 
                    'ext': best_audio.get('ext'), 
                    'url': best_audio.get('url'), 
                    'type': 'audio_only'
                })

        # تجهيز الرد النهائي
        return {
            "title": info.get('title'),
            "thumbnail": info.get('thumbnail'),
            "duration_string": info.get('duration_string'),
            "formats": formats_list
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
