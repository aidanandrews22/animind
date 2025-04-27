import { useState, useEffect, useRef } from "react";
import { VideoIcon, PlusIcon, UploadIcon } from "./Icons";
import IconButton from "./IconButton";
import EmptyState from "./EmptyState";
import { useSupabase } from "../hooks/useSupabase";
import { 
  getVideosByUserId, 
  getVideoUrls, 
  createVideo, 
  uploadVideoFile, 
  generateThumbnail,
  renameVideo
} from "../services/videoService";
import type { Database } from "../types/supabase";
import { useNavigate } from "react-router-dom";

type Video = Database['public']['Tables']['videos']['Row'] & {
  thumbnailUrl?: string;
  videoUrl?: string;
  createdAt?: string;
};

interface VideoTabProps {
  courseId: string;
  videos?: Video[];
}

interface RenameDialogProps {
  video: Video | null;
  isOpen: boolean;
  onClose: () => void;
  onRename: (videoId: string, updates: { title: string; description: string }) => Promise<void>;
}

function RenameDialog({ video, isOpen, onClose, onRename }: RenameDialogProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (video) {
      setTitle(video.title || '');
      setDescription(video.description || '');
    }
  }, [video]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!video) return;
    
    setIsSubmitting(true);
    await onRename(video.id, { title, description });
    setIsSubmitting(false);
    onClose();
  };

  if (!isOpen || !video) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-medium mb-4">Rename Video</h3>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              required
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              rows={3}
            />
          </div>
          
          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:opacity-50"
            >
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function VideoTab({
  courseId,
}: VideoTabProps) {
  const { userId, isLoading: isUserLoading } = useSupabase();
  const [videos, setVideos] = useState<Video[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null);
  const [isRenameDialogOpen, setIsRenameDialogOpen] = useState(false);

  useEffect(() => {
    async function loadVideos() {
      if (!userId || !courseId) return;
      
      setIsLoading(true);
      const videosData = await getVideosByUserId(userId, courseId);
      
      // Add UI-specific properties and get URLs for videos
      const formattedVideos = await Promise.all(videosData.map(async video => {
        // Get video and thumbnail URLs
        const { videoUrl, thumbnailUrl } = await getVideoUrls(video.id);
        
        return {
          ...video,
          videoUrl,
          thumbnailUrl,
          createdAt: formatDate(video.created_at),
        };
      }));
      
      setVideos(formattedVideos);
      setIsLoading(false);
    }
    
    if (!isUserLoading) {
      loadVideos();
    }
  }, [userId, courseId, isUserLoading]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffInDays === 0) return 'Today';
    if (diffInDays === 1) return 'Yesterday';
    if (diffInDays < 7) return `${diffInDays} days ago`;
    if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`;
    return `${Math.floor(diffInDays / 30)} months ago`;
  };

  const filteredVideos = videos.filter(
    (video) =>
      video.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (video.description && video.description.toLowerCase().includes(searchQuery.toLowerCase())),
  );

  const handleCreateVideo = () => {
    // In a real app, this would navigate to video creation or show a modal
    alert(
      "In a real implementation, this would open the video generation interface",
    );
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !userId || !courseId) return;
    
    try {
      // First create the video record
      const newVideo = await createVideo({
        user_id: userId,
        course_id: courseId,
        title: file.name.split('.')[0], // Use filename as title
        description: 'Uploaded for development',
        status: 'processing',
        bucket_path: 'pending-upload', // Temporary value, will be updated after upload
      });
      
      if (!newVideo) throw new Error('Failed to create video record');
      
      // Generate thumbnail from video
      const thumbnailBlob = await generateThumbnail(file);
      
      // Then upload the actual file and thumbnail
      const updatedVideo = await uploadVideoFile(
        newVideo.id, 
        file, 
        thumbnailBlob || undefined
      );
      
      if (updatedVideo) {
        // Get the URLs and add to the videos list
        const { videoUrl, thumbnailUrl } = await getVideoUrls(updatedVideo.id);
        
        const formattedVideo = {
          ...updatedVideo,
          videoUrl,
          thumbnailUrl,
          createdAt: formatDate(updatedVideo.created_at),
        };
        
        setVideos(prevVideos => [formattedVideo, ...prevVideos]);
        alert('Video uploaded successfully!');
      }
    } catch (error) {
      console.error('Error uploading video:', error);
      alert('Failed to upload video');
    }
    
    // Reset the input
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleVideoClick = (videoId: string) => {
    navigate(`/video/${videoId}`);
  };

  const handleVideoRename = async (videoId: string, updates: { title: string; description: string }) => {
    try {
      const updatedVideo = await renameVideo(videoId, updates);
      
      if (updatedVideo) {
        // Update the video in the list
        setVideos(prevVideos =>
          prevVideos.map(video =>
            video.id === videoId
              ? { ...video, title: updatedVideo.title, description: updatedVideo.description }
              : video
          )
        );
      }
    } catch (error) {
      console.error('Error renaming video:', error);
      alert('Failed to rename video');
    }
  };

  const handleVideoContextMenu = (e: React.MouseEvent, video: Video) => {
    e.preventDefault();
    e.stopPropagation();
    setSelectedVideo(video);
    setIsRenameDialogOpen(true);
  };

  // Show loading state
  if (isLoading && videos.length === 0) {
    return (
      <div className="max-h-screen overflow-y-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
          </div>
        </div>
      </div>
    );
  }

  // Default thumbnail for videos without one
  const defaultThumbnail = "https://via.placeholder.com/320x180/f3f4f6/808080?text=Video";

  return (
    <div className="max-h-screen overflow-y-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div className="relative flex-grow max-w-md">
            <input
              type="text"
              placeholder="Search videos..."
              className="w-full pl-3 pr-10 py-2 border border-gray-200 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-gray-300"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
              <VideoIcon size={16} />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input 
              type="file" 
              ref={fileInputRef} 
              className="hidden" 
              accept="video/*"
              onChange={handleFileChange}
            />
            <IconButton
              icon={<UploadIcon />}
              label="Upload"
              variant="secondary"
              onClick={handleUploadClick}
              className="!py-1.5 !px-3 text-xs"
            />
            <IconButton
              icon={<PlusIcon />}
              label="Generate Video"
              variant="primary"
              onClick={handleCreateVideo}
            />
          </div>
        </div>

        {filteredVideos.length === 0 ? (
          <EmptyState
            icon={<VideoIcon size={48} />}
            title="No videos found"
            description={
              searchQuery
                ? "Try a different search term"
                : "Generate your first video from course content"
            }
            actionLabel="Generate Video"
            actionIcon={<PlusIcon />}
            onAction={handleCreateVideo}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredVideos.map((video) => (
              <div
                key={video.id}
                className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => handleVideoClick(video.id)}
                onContextMenu={(e) => handleVideoContextMenu(e, video)}
              >
                <div className="aspect-video bg-gray-100 relative">
                  <img
                    src={video.thumbnailUrl || defaultThumbnail}
                    alt={video.title}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div 
                      className="w-12 h-12 bg-gray-800 bg-opacity-75 rounded-full flex items-center justify-center cursor-pointer hover:bg-opacity-90 transition-colors"
                    >
                      <svg
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="white"
                        strokeWidth="2"
                      >
                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                      </svg>
                    </div>
                  </div>
                </div>

                <div className="p-4">
                  <h3 className="font-medium text-gray-800 mb-1">
                    {video.title}
                  </h3>
                  <p className="text-sm text-gray-500 line-clamp-2 mb-2">
                    {video.description || 'No description available'}
                  </p>
                  <div className="flex justify-between items-center text-xs text-gray-400">
                    <span>Created {video.createdAt}</span>
                    <div className="inline-flex items-center px-2 py-1 rounded-full bg-gray-100 text-gray-600 text-xs">
                      {video.status}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        
        <RenameDialog
          video={selectedVideo}
          isOpen={isRenameDialogOpen}
          onClose={() => {
            setIsRenameDialogOpen(false);
            setSelectedVideo(null);
          }}
          onRename={handleVideoRename}
        />
      </div>
    </div>
  );
}
