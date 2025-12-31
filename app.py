from flask import Flask, render_template, jsonify, request
from service.twelvelabs_service import TwelveLabsService
import os

app = Flask(__name__)
twelvelabs_service = TwelveLabsService()

# YouTube description generation prompt
YOUTUBE_DESCRIPTION_PROMPT = """Generate a YouTube-optimized description for this video. Include:
- Strong opening hook (2-3 lines)
- Clear video summary
- Timestamp chapters (YouTube format) if applicable
- Key takeaways (bullet points)
- SEO keywords and 10-15 relevant hashtags

Format the output in Markdown. Use clear headings, lists, and professional YouTube-friendly language. Do not hallucinate content not present in the video. No emojis."""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/indexes')
def get_indexes():
    """Get list of all video indexes"""
    try:
        indexes = twelvelabs_service.get_indexes()
        return jsonify({'success': True, 'indexes': indexes})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/videos/<index_id>')
def get_videos(index_id):
    """Get list of videos for a specific index"""
    try:
        videos = twelvelabs_service.get_videos(index_id)
        return jsonify({'success': True, 'videos': videos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_video():
    """Analyze video and generate YouTube description"""
    try:
        data = request.json
        video_id = data.get('video_id')
        index_id = data.get('index_id')
        
        if not video_id or not index_id:
            return jsonify({'success': False, 'error': 'Missing video_id or index_id'}), 400
        
        # Use the analyze method with YouTube description prompt
        analysis_result = twelvelabs_service.analyze_video(video_id, YOUTUBE_DESCRIPTION_PROMPT)
        
        # Extract the description from the analysis result
        description = analysis_result if isinstance(analysis_result, str) else str(analysis_result)
        
        return jsonify({'success': True, 'description': description})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

