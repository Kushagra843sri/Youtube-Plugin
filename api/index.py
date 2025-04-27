from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS for your Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask(request: Request):
    body = await request.json()
    video_id = body.get('video_id')
    question = body.get('question')

    if not video_id or not question:
        return JSONResponse({"error": "Missing video_id or question"}, status_code=400)

    # Your logic here: generate transcript from video_id, use RAG, answer the question
    # Example dummy response:
    answer = f"This is a dummy answer for video {video_id} and question '{question}'."

    return {"answer": answer}
