import { useState, useEffect } from "react";
import ReactPlayer from "react-player";
import { getVideoById, getVideoUrls } from "../services/videoService";

interface EmbeddedVideoProps {
  videoId: string;
  title: string;
}

export default function EmbeddedVideo({ videoId, title }: EmbeddedVideoProps) {
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [thumbnailUrl, setThumbnailUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Supabase storage base URL - adjust as needed
  const STORAGE_BASE_URL = "https://iprttfzpkrjkslvhmhtp.supabase.co/storage/v1/object/public/";
  const VIDEO_BUCKET = "videos";
  const THUMBNAIL_BUCKET = "thumbnails";
  const ACTUAL_VIDEO_ID = "564283c8-dc10-4c32-88a2-94b55c2ab99a";
  const USER_ID = "2c55f983-47a9-4e52-9a20-d0d315e51596";

  useEffect(() => {
    async function loadVideo() {
      if (!videoId) return;
      
      // Special case for our demo video - set this first and immediately
      if (videoId === "trajectories-integrals") {
        console.log("Loading demo video for trajectories with ID:", ACTUAL_VIDEO_ID);
        
        try {
          // Try to load from the actual video service first
          const videoData = await getVideoById(ACTUAL_VIDEO_ID);
          
          if (videoData) {
            // Get video and thumbnail URLs from service
            const { videoUrl, thumbnailUrl } = await getVideoUrls(ACTUAL_VIDEO_ID);
            
            if (videoUrl) {
              setVideoUrl(videoUrl);
              setThumbnailUrl(thumbnailUrl);
              setIsLoading(false);
              return;
            }
          }
        } catch (error) {
          console.warn("Could not load from video service, using direct URLs:", error);
        }
        
        // Fallback to direct URLs if service call fails
        const fullVideoPath = `${STORAGE_BASE_URL}${VIDEO_BUCKET}/${USER_ID}/${ACTUAL_VIDEO_ID}/1745751182429.mp4`;
        // Try to use thumbnail from Supabase as well
        const fullThumbnailPath = `${STORAGE_BASE_URL}${THUMBNAIL_BUCKET}/${USER_ID}/${ACTUAL_VIDEO_ID}/thumbnail.jpg`;
        
        setVideoUrl(fullVideoPath);
        setThumbnailUrl(fullThumbnailPath);
        setIsLoading(false);
        return;
      }
      
      // For other video IDs, use the regular flow
      setIsLoading(true);
      try {
        const videoData = await getVideoById(videoId);
        if (!videoData) throw new Error("Video not found");
        
        // Get video and thumbnail URLs
        const { videoUrl, thumbnailUrl } = await getVideoUrls(videoData.id);
        
        setVideoUrl(videoUrl);
        setThumbnailUrl(thumbnailUrl);
      } catch (error) {
        console.error("Error loading video:", error);
        setError("Failed to load video");
      } finally {
        setIsLoading(false);
      }
    }
    
    // Call immediately 
    loadVideo();
  }, [videoId]);
  
  // Force immediate display for trajectory video (fallback if effect has issues)
  useEffect(() => {
    if (videoId === "trajectories-integrals" && isLoading) {
      console.log("Forcing immediate load of trajectories video");
      const fullVideoPath = `${STORAGE_BASE_URL}${VIDEO_BUCKET}/${USER_ID}/${ACTUAL_VIDEO_ID}/1745751182429.mp4`;
      const fullThumbnailPath = `${STORAGE_BASE_URL}${THUMBNAIL_BUCKET}/${USER_ID}/${ACTUAL_VIDEO_ID}/thumbnail.jpg`;
      
      setVideoUrl(fullVideoPath);
      setThumbnailUrl(fullThumbnailPath);
      setIsLoading(false);
    }
  }, [videoId, isLoading]);
  
  // Loading state
  if (isLoading) {
    return (
      <div className="rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
        <div className="aspect-video flex items-center justify-center bg-gray-100 dark:bg-gray-900">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        </div>
        <div className="p-3">
          <p className="font-medium">{title}</p>
          <p className="text-sm text-gray-500">Loading video...</p>
        </div>
      </div>
    );
  }
  
  // Error state
  if (error || !videoUrl) {
    return (
      <div className="rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
        <div className="aspect-video flex items-center justify-center bg-gray-100 dark:bg-gray-900">
          <svg
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            className="text-gray-400"
          >
            <path d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14v-4z"></path>
            <rect x="3" y="6" width="12" height="12" rx="2" ry="2"></rect>
          </svg>
        </div>
        <div className="p-3">
          <p className="font-medium">{title}</p>
          <p className="text-sm text-gray-500">{error || "Video unavailable"}</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
      <div className="relative bg-black rounded-t-lg overflow-hidden aspect-video">
        <ReactPlayer
          url={videoUrl}
          width="100%"
          height="100%"
          controls={true}
          light={thumbnailUrl || undefined}
          playing={false}
          playsinline
          config={{
            file: {
              attributes: {
                controlsList: 'nodownload',
              }
            }
          }}
          className="aspect-video object-contain"
        />
      </div>
      <div className="p-3 bg-white dark:bg-gray-800">
        <p className="font-medium">{title}</p>
        <p className="text-sm text-gray-500">Click to play</p>
      </div>
    </div>
  );
} 