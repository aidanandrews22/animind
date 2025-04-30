import os
import asyncio
import logging
from typing import Optional
import queue
import threading
from contextlib import asynccontextmanager
import subprocess
import uuid
from datetime import datetime
import dotenv
from supabase import create_client, Client

dotenv.load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, UUID4
from fastapi.middleware.cors import CORSMiddleware

from flow import create_manim_agent_flow

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all messages
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Output to console
        logging.FileHandler("agent_api.log")  # Also log to file
    ]
)
logger = logging.getLogger("manim_agent_api")

# Ensure all loggers have DEBUG level
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger("manim_agent").setLevel(logging.DEBUG)

# Supabase configuration
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON")
supabase: Client = create_client(supabase_url, supabase_key)

# Queue for streaming progress updates
progress_queue = queue.Queue()

# Custom handler to capture log messages
class QueueHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        # Always send error logs as errors in the queue
        if record.levelno >= logging.ERROR:
            progress_queue.put(f"error: {log_entry}")
        elif record.levelno >= logging.WARNING:
            progress_queue.put(f"warning: {log_entry}")
        else:
            progress_queue.put(f"log: {log_entry}")

# Add our queue handler to the logger with debug level
queue_handler = QueueHandler()
queue_handler.setLevel(logging.DEBUG)
queue_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
logging.getLogger("manim_agent").addHandler(queue_handler)
# Also capture errors from other modules
logging.getLogger().addHandler(queue_handler)

# Pydantic model for the request
class AnimationRequest(BaseModel):
    prompt: str
    output_dir: Optional[str] = "output"
    file_name: Optional[str] = "animation"
    user_id: UUID4
    bucket_path: str
    thumbnail_path: Optional[str] = None
    course_id: Optional[UUID4] = None
    title: str
    description: Optional[str] = None

# Insert video record into Supabase
def insert_video_record(video_data):
    try:
        logger.info(f"Inserting video record for user: {video_data['user_id']}")
        
        # Create record in videos table
        result = supabase.table("videos").insert({
            "user_id": str(video_data["user_id"]),
            "course_id": str(video_data["course_id"]) if video_data.get("course_id") else None,
            "title": video_data["title"],
            "description": video_data.get("description"),
            "bucket_path": video_data["bucket_path"],
            "thumbnail_path": video_data.get("thumbnail_path"),
            "status": "completed"
        }).execute()
        
        if result.data:
            logger.info(f"Video record created with ID: {result.data[0]['id']}")
            return {
                "success": True,
                "video_id": result.data[0]["id"]
            }
        else:
            logger.error(f"Error inserting video record: {result.error}")
            return {
                "success": False,
                "error": result.error
            }
    except Exception as e:
        logger.exception(f"Error inserting video record: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Check for required environment variables
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_key:
        logger.warning("GEMINI_API_KEY environment variable is not set")
        logger.info("Using OpenAI-compatible endpoint with Google Gemini will require an API key")
    else:
        logger.info("GEMINI_API_KEY is set")
    
    # Check for Supabase configuration
    if not supabase_url or not supabase_key:
        logger.warning("SUPABASE_URL or SUPABASE_ANON environment variables are not set")
    else:
        logger.info("Supabase configuration is set")
    
    # Setup is done
    logger.info("Manim Agent API is ready")
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down Manim Agent API")

# Create FastAPI app
app = FastAPI(
    title="Manim Animation Agent API",
    description="API for generating Manim animations from text prompts",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware to allow requests from the frontend
origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
logger.info(f"Allowing CORS from origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Frontend origins from environment variable
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Execute the stitching script to generate the final video
def execute_stitching_script(stitch_file, video_data):
    try:
        logger.info(f"Executing stitching script: {stitch_file}")
        progress_queue.put(f"status: Executing stitching script to generate final video")
        
        # Run the stitching script
        result = subprocess.run(["python", stitch_file], check=True, capture_output=True, text=True)
        logger.info(f"Stitching script stdout: {result.stdout}")
        
        # Get the output directory from the stitch file path
        output_dir = os.path.dirname(stitch_file)
        final_dir = os.path.join(output_dir, "final")
        
        # Look for the final video in the expected location
        final_video_path = None
        
        # Check if the final directory exists
        if os.path.exists(final_dir):
            # Find all mp4 files in the final directory
            for file in os.listdir(final_dir):
                if file.endswith(".mp4"):
                    final_video_path = os.path.join(final_dir, file)
                    logger.info(f"Found final video: {final_video_path}")
                    break
        
        # If we didn't find a video in the final directory, search the output directory
        if not final_video_path:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4") and not file.startswith("partial_"):
                        final_video_path = os.path.join(root, file)
                        logger.info(f"Found video: {final_video_path}")
                        # We'll keep searching to try to find the most recently created video
        
        if final_video_path:
            # Insert record into Supabase
            video_data["bucket_path"] = os.path.join(video_data["bucket_path"], os.path.basename(final_video_path))
            db_result = insert_video_record(video_data)
            
            if db_result["success"]:
                return {
                    "success": True,
                    "final_video_path": final_video_path,
                    "video_id": db_result["video_id"]
                }
            else:
                logger.error(f"Failed to create video record: {db_result.get('error')}")
                return {
                    "success": True,
                    "final_video_path": final_video_path,
                    "db_error": db_result.get("error")
                }
        else:
            logger.warning("No final video found after execution")
            return {
                "success": False,
                "error": "No final video found after execution"
            }
    except Exception as e:
        logger.exception(f"Error executing stitching script: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Run the agent in a background thread
def run_agent(prompt: str, output_dir: str, file_name: str, video_data: dict):
    try:
        # Clear the queue before starting
        while not progress_queue.empty():
            progress_queue.get()
        
        # Send initial status
        progress_queue.put(f"status: Starting animation generation for prompt: {prompt}")
        
        # Create directories
        os.makedirs(output_dir, exist_ok=True)
        
        # Create the agent flow
        agent_flow = create_manim_agent_flow()
        
        # Initialize shared state
        shared = {
            "prompt": prompt,
            "output_directory": output_dir,
            "file_name": file_name
        }
        
        # Execute the flow
        progress_queue.put("status: Running animation generation flow")
        agent_flow.run(shared)
        
        # Log the final result
        if "final_result" in shared:
            final_result = shared["final_result"]
            status = final_result.get("status", "error")
            
            if status == "success":
                scene_count = final_result.get("scene_count", 0)
                final_video_path = final_result.get("final_video_path")
                
                if final_video_path and os.path.exists(final_video_path):
                    progress_queue.put(f"status: Animation generation complete! Final video available.")
                    
                    # Insert record into Supabase
                    video_data["bucket_path"] = os.path.join(video_data["bucket_path"], os.path.basename(final_video_path))
                    db_result = insert_video_record(video_data)
                    
                    if db_result["success"]:
                        progress_queue.put(f"result: {{'scene_count': {scene_count}, 'final_video': '{final_video_path}', 'video_id': '{db_result['video_id']}'}}")
                    else:
                        progress_queue.put(f"warning: Database entry failed: {db_result.get('error', 'Unknown error')}")
                        progress_queue.put(f"result: {{'scene_count': {scene_count}, 'final_video': '{final_video_path}'}}")
                else:
                    progress_queue.put(f"error: Final video path is invalid or missing: {final_video_path}")
            else:
                error_message = final_result.get("message", "Unknown error")
                progress_queue.put(f"error: Animation generation failed: {error_message}")
                progress_queue.put(f"result: {{'status': '{status}', 'error': '{error_message}'}}")
        else:
            progress_queue.put("status: Flow completed but no final result was found")
        
    except Exception as e:
        logger.exception(f"Error during animation generation: {str(e)}")
        progress_queue.put(f"error: {str(e)}")
    
    # Signal that we're done
    progress_queue.put("END")

# Generate event stream
async def event_generator():
    """Generate server-sent events with progress updates."""
    try:
        while True:
            try:
                # Non-blocking get with timeout
                message = progress_queue.get(timeout=0.1)
                
                # Check for end signal
                if message == "END":
                    yield f"data: {{'status': 'complete'}}\n\n"
                    break
                    
                yield f"data: {message}\n\n"
            except queue.Empty:
                # Allow for other async operations
                await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        # This occurs when the client disconnects
        logger.info("Client disconnected, stopping event stream")
    except Exception as e:
        logger.error(f"Unexpected error in event stream: {str(e)}")

@app.post("/generate")
async def generate_animation(request: AnimationRequest, background_tasks: BackgroundTasks):
    """
    Generate a Manim animation from a text prompt.
    Returns a stream of server-sent events with progress updates.
    """
    # Validate inputs
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    if not request.bucket_path:
        raise HTTPException(status_code=400, detail="Bucket path cannot be empty")
    
    if not request.title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    
    # Prepare video data for database
    video_data = {
        "user_id": request.user_id,
        "course_id": request.course_id,
        "title": request.title,
        "description": request.description,
        "bucket_path": request.bucket_path,
        "thumbnail_path": request.thumbnail_path
    }
    
    # Start the agent in a background task
    background_tasks.add_task(
        run_agent, 
        request.prompt, 
        request.output_dir, 
        request.file_name,
        video_data
    )
    
    # For POST requests, we'll just return a success response
    # since the client will connect separately for updates
    return {"status": "started"}

@app.get("/stream-updates")
async def stream_updates():
    """
    Stream updates for the animation generation process.
    This endpoint is specifically for EventSource clients to connect to.
    """
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "auth": {
            "gemini_key": bool(os.getenv("GEMINI_API_KEY")),
            "openai_compatible": True,
            "supabase": bool(supabase_url and supabase_key)
        }
    }

if __name__ == "__main__":
    import uvicorn
    # Start the server
    uvicorn.run("agent:app", host="0.0.0.0", port=2222, reload=True)
