import { useState, useEffect } from "react";
import ReactPlayer from "react-player";
import { useParams, useNavigate } from "react-router-dom";
import { getVideoById, getVideoUrls } from "../services/videoService";
import { VideoIcon, HeartIcon, ShareIcon, BookmarkIcon, ArrowLeftIcon } from "./Icons";
import type { Database } from "../types/supabase";

type Video = Database['public']['Tables']['videos']['Row'] & {
  thumbnailUrl?: string;
  videoUrl?: string;
  createdAt?: string;
};

export default function VideoPlayer() {
  const { videoId } = useParams<{ videoId: string }>();
  const navigate = useNavigate();
  const [video, setVideo] = useState<Video | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLiked, setIsLiked] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);
  
  useEffect(() => {
    async function loadVideo() {
      if (!videoId) return;
      
      setIsLoading(true);
      try {
        const videoData = await getVideoById(videoId);
        if (!videoData) throw new Error("Video not found");
        
        // Get video and thumbnail URLs
        const { videoUrl, thumbnailUrl } = await getVideoUrls(videoData.id);
        
        setVideo({
          ...videoData,
          videoUrl,
          thumbnailUrl,
          createdAt: formatDate(videoData.created_at),
        });
      } catch (error) {
        console.error("Error loading video:", error);
      } finally {
        setIsLoading(false);
      }
    }
    
    loadVideo();
  }, [videoId]);
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(date);
  };
  
  const handleLike = () => {
    setIsLiked(!isLiked);
    // In a real app, would call API to update like status
  };
  
  const handleBookmark = () => {
    setIsBookmarked(!isBookmarked);
    // In a real app, would call API to update bookmark status
  };
  
  const handleShare = () => {
    // Mock implementation - would open share dialog
    alert("Share functionality would be implemented here");
  };
  
  const handleBack = () => {
    navigate(-1);
  };
  
  // Loading state
  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8 h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }
  
  // Error state
  if (!video || !video.videoUrl) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center">
          <VideoIcon size={48} className="mx-auto text-gray-400" />
          <h2 className="mt-4 text-xl font-semibold text-gray-800">Video not found</h2>
          <p className="mt-2 text-gray-600">The video you're looking for doesn't exist or isn't available.</p>
          <button 
            onClick={handleBack}
            className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
          >
            Go back
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Back button */}
        <button 
          onClick={handleBack}
          className="mb-4 inline-flex items-center text-gray-600 hover:text-gray-900"
        >
          <ArrowLeftIcon size={16} className="mr-1" />
          <span>Back</span>
        </button>
        
        {/* Video Player */}
        <div 
          className="relative bg-black rounded-lg overflow-hidden shadow-xl aspect-video max-h-[70vh]"
        >
          <ReactPlayer
            url={video.videoUrl}
            width="100%"
            height="100%"
            controls={true}
            light={video.thumbnailUrl || undefined}
            playing={true}
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
        
        {/* Video Info */}
        <div className="mt-6 bg-white p-6 rounded-lg shadow-sm">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
            <div className="flex-grow">
              <h1 className="text-2xl font-semibold text-gray-900">{video.title}</h1>
              <div className="flex items-center text-sm text-gray-500 mt-1 space-x-2">
                <span>Published on {video.createdAt}</span>
                <span>•</span>
                <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-green-100 text-green-800 text-xs">
                  {video.status}
                </span>
              </div>
              
              <div className="flex items-center gap-4 my-4 md:hidden">
                <button 
                  onClick={handleLike}
                  className={`flex flex-col items-center ${isLiked ? 'text-red-500' : 'text-gray-500'} hover:text-red-500`}
                >
                  <HeartIcon size={20} className={isLiked ? 'fill-current' : ''} />
                  <span className="text-xs mt-1">Like</span>
                </button>
                
                <button 
                  onClick={handleBookmark}
                  className={`flex flex-col items-center ${isBookmarked ? 'text-blue-500' : 'text-gray-500'} hover:text-blue-500`}
                >
                  <BookmarkIcon size={20} className={isBookmarked ? 'fill-current' : ''} />
                  <span className="text-xs mt-1">Save</span>
                </button>
                
                <button 
                  onClick={handleShare}
                  className="flex flex-col items-center text-gray-500 hover:text-gray-700"
                >
                  <ShareIcon size={20} />
                  <span className="text-xs mt-1">Share</span>
                </button>
              </div>
              
              <p className="mt-4 text-gray-700">
                {video.description || 'No description available'}
              </p>
            </div>
            
            <div className="hidden md:flex md:items-center gap-6 pt-2">
              <button 
                onClick={handleLike}
                className={`flex flex-col items-center ${isLiked ? 'text-red-500' : 'text-gray-500'} hover:text-red-500`}
              >
                <HeartIcon size={24} className={isLiked ? 'fill-current' : ''} />
                <span className="text-xs mt-1">Like</span>
              </button>
              
              <button 
                onClick={handleBookmark}
                className={`flex flex-col items-center ${isBookmarked ? 'text-blue-500' : 'text-gray-500'} hover:text-blue-500`}
              >
                <BookmarkIcon size={24} className={isBookmarked ? 'fill-current' : ''} />
                <span className="text-xs mt-1">Save</span>
              </button>
              
              <button 
                onClick={handleShare}
                className="flex flex-col items-center text-gray-500 hover:text-gray-700"
              >
                <ShareIcon size={24} />
                <span className="text-xs mt-1">Share</span>
              </button>
            </div>
          </div>
        </div>
        
        {/* Video metrics */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center text-purple-500">
                <VideoIcon size={14} />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Video Quality</p>
                <p className="text-xs text-gray-500">HD (1080p)</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-500">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Duration</p>
                <p className="text-xs text-gray-500">1:24 minutes</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center text-green-500">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">AI Generated</p>
                <p className="text-xs text-gray-500">From your course content</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Course Information */}
        <div className="mt-6 bg-white p-6 rounded-lg shadow-sm">
          <h2 className="text-xl font-medium text-gray-900 mb-4">Course Information</h2>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
              <VideoIcon size={16} />
            </div>
            <div>
              <p className="text-sm font-medium">From course: {video.course_id || 'Unknown'}</p>
              <p className="text-xs text-gray-500">This video was generated as part of your course materials</p>
            </div>
          </div>
          <button
            onClick={() => navigate(`/course/${video.course_id}`)}
            className="mt-4 text-sm text-indigo-600 font-medium hover:text-indigo-500"
          >
            Go to course
          </button>
        </div>
      </div>
    </div>
  );
} 