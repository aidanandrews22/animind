from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import requests
import json
import os
from pydantic import BaseModel
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Animind API"}

@app.post("/agent")
async def agent(text: str):
    return {"response": "hi"}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        api_key = os.environ.get('OPENROUTER_API_KEY')
        if not api_key:
            logger.error("OPENROUTER_API_KEY environment variable not set")
            return JSONResponse(
                status_code=500,
                content={"error": "API key not configured. Please set OPENROUTER_API_KEY environment variable."}
            )
            
        logger.info(f"Processing chat request with message: {request.message[:30]}...")
        
        def generate():
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "google/gemini-2.0-flash-exp:free",
                "messages": [{"role": "user", "content": request.message}],
                "stream": True
            }

            logger.info(f"Sending request to OpenRouter API with model: {payload['model']}")
            
            try:
                with requests.post(url, headers=headers, json=payload, stream=True) as r:
                    if r.status_code != 200:
                        error_msg = f"OpenRouter API returned status code {r.status_code}"
                        logger.error(error_msg)
                        yield json.dumps({"error": error_msg, "details": r.text})
                        return
                        
                    logger.info("Successfully connected to OpenRouter API, streaming response")
                    buffer = ""
                    for chunk in r.iter_content(chunk_size=1024, decode_unicode=False):
                        if chunk:
                            chunk_text = chunk.decode('utf-8')
                            buffer += chunk_text
                            while True:
                                try:
                                    # Find the next complete SSE line
                                    line_end = buffer.find('\n')
                                    if line_end == -1:
                                        break

                                    line = buffer[:line_end].strip()
                                    buffer = buffer[line_end + 1:]

                                    if line.startswith('data: '):
                                        data = line[6:]
                                        if data == '[DONE]':
                                            logger.info("Completed streaming response")
                                            break

                                        try:
                                            data_obj = json.loads(data)
                                            content = data_obj["choices"][0]["delta"].get("content")
                                            if content:
                                                yield content
                                        except json.JSONDecodeError as e:
                                            logger.error(f"Failed to parse JSON: {e}")
                                            yield f"\nError parsing data: {data}\n"
                                except Exception as e:
                                    logger.error(f"Error processing chunk: {e}")
                                    yield f"\nError processing response: {str(e)}\n"
                                    break
            except requests.RequestException as e:
                error_msg = f"Error connecting to OpenRouter API: {str(e)}"
                logger.error(error_msg)
                yield json.dumps({"error": error_msg})
                
        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        logger.exception("Unexpected error in chat endpoint")
        return JSONResponse(
            status_code=500, 
            content={"error": f"Server error: {str(e)}"}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 