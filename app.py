import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi

# Replace with your LLM library (e.g., langchain, openai, transformers)
# Example uses OpenAI for simplicity; adjust for your LLM
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Allow CORS for Chrome extension requests
CORS(app, resources={r"/*": {"origins": ["chrome-extension://*"]}})

# Initialize LLM client (example with OpenAI; replace with your LLM setup)
if OpenAI:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
else:
    # Placeholder for custom LLM (e.g., Hugging Face, local model)
    client = None
    logger.warning("OpenAI not available. LLM client not configured.")

def query_llm(transcript, question):
    """
    Process the transcript and question with your LLM.
    Replace this with your actual RAG logic.
    """
    if not client:
        logger.error("LLM client not configured.")
        return "LLM not configured. Please set up an LLM client."

    try:
        logger.info("Querying LLM with transcript and question.")
        # Example RAG prompt: Combine transcript and question
        prompt = f"Based on the following transcript, answer the question:\n\nTranscript: {transcript}\n\nQuestion: {question}\n\nAnswer:"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Replace with your model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on video transcripts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"LLM error: {str(e)}")
        return f"LLM error: {str(e)}"

@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    """
    Fetch YouTube transcript for a given video ID.
    Expects JSON: {"video_id": "your_video_id"}
    """
    try:
        data = request.get_json()
        video_id = data.get('video_id')
        if not video_id:
            logger.warning("Missing video_id in request.")
            return jsonify({'error': 'video_id is required'}), 400
        
        logger.info(f"Fetching transcript for video_id: {video_id}")
        # Fetch transcript using YouTube Transcript API
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([entry['text'] for entry in transcript])
        logger.info("Transcript fetched successfully.")
        return jsonify({'transcript': transcript_text})
    except Exception as e:
        logger.error(f"Error fetching transcript: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/ask_question', methods=['POST'])
def ask_question():
    """
    Answer a question based on the transcript using the LLM.
    Expects JSON: {"transcript": "transcript text", "question": "your question"}
    """
    try:
        data = request.get_json()
        transcript = data.get('transcript')
        question = data.get('question')
        if not transcript or not question:
            logger.warning("Missing transcript or question in request.")
            return jsonify({'error': 'transcript and question are required'}), 400
        
        logger.info("Processing question with LLM.")
        # Query LLM with transcript and question
        answer = query_llm(transcript, question)
        return jsonify({'answer': answer})
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/')
def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed.")
    return jsonify({'status': 'Backend is running'})

if __name__ == '__main__':
    # For local testing only; Render uses gunicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)