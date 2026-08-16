from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/api/<quality>', methods=['GET'])
def get_media_link(quality):
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({"status": "error", "message": "Missing 'url' query parameter"}), 400

    if quality in ['video', 'hd']:
        fmt = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    elif quality in ['music', 'mp3']:
        fmt = 'bestaudio/best'
    else:
        return jsonify({"status": "error", "message": "Invalid quality parameter. Use 'video' or 'music'"}), 400

    ydl_opts = {
        'format': fmt,
        'quiet': True,
        'getcomments': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            stream_url = info.get('url')
            if not stream_url and 'requested_formats' in info:
                stream_url = info['requested_formats'][0].get('url')
            elif not stream_url and 'formats' in info:
                stream_url = info['formats'][-1].get('url')

            comments_list = []
            if info.get('comments'):
                for c in info.get('comments')[:10]:
                    comments_list.append({
                        "author": c.get('author'),
                        "author_avatar": c.get('author_thumbnail'),
                        "text": c.get('text'),
                        "likes": c.get('like_count')
                    })

            return jsonify({
                "status": "success",
                "title": info.get('title'),
                "quality": quality,
                "duration": info.get('duration_string'),
                "thumbnail": info.get('thumbnail'),
                "uploader": info.get('uploader'),
                "uploader_avatar": info.get('uploader_avatar') or info.get('channel_thumbnail'),
                "download_url": stream_url,
                "views": info.get('view_count'),
                "likes": info.get('like_count'),
                "total_comments": info.get('comment_count'),
                "comments": comments_list
            })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Vercel entrypoint handler
app = app