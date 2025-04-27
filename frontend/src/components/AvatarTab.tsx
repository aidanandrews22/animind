import { useState, useEffect, useRef } from "react";
import { PlusIcon, AvatarIcon } from "./Icons";
import IconButton from "./IconButton";
import EmptyState from "./EmptyState";
import { useSupabase } from "../hooks/useSupabase";
import { getAvatarFilesByUserId, uploadAvatarFile, getFileUrl, deleteFile } from "../services/fileService";
import type { Database } from "../types/supabase";

type AvatarFile = Database['public']['Tables']['files']['Row'] & {
  uploadedAt?: string;
  url?: string;
};

interface AvatarTabProps {
  courseId?: string; // Optional as avatars aren't tied to courses
}

export default function AvatarTab({ courseId }: AvatarTabProps) {
  const { userId, isLoading: isUserLoading } = useSupabase();
  const [avatars, setAvatars] = useState<AvatarFile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedAvatar, setSelectedAvatar] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    async function loadAvatars() {
      if (!userId) return;
      
      setIsLoading(true);
      const avatarsData = await getAvatarFilesByUserId(userId, courseId);
      
      // Add UI-specific properties and get URLs for files
      const formattedAvatars = await Promise.all(avatarsData.map(async file => {
        const url = await getFileUrl(file.bucket_path);
        return {
          ...file,
          uploadedAt: formatDate(file.created_at),
          url: url,
        };
      }));
      
      setAvatars(formattedAvatars);
      if (formattedAvatars.length > 0) {
        setSelectedAvatar(formattedAvatars[0].id);
      }
      setIsLoading(false);
    }
    
    if (!isUserLoading) {
      loadAvatars();
    }
  }, [userId, isUserLoading, courseId]);

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

  const filteredAvatars = avatars.filter((avatar) =>
    avatar.name.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const handleUpload = () => {
    // Trigger file input click
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;
    if (!selectedFiles || !userId) return;
    
    setIsLoading(true);
    
    // Upload each file
    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];
      
      // Validate file type - only allow PNGs
      if (!file.type.includes('png')) {
        alert('Only PNG images are allowed for avatars!');
        continue;
      }
      
      try {
        // Upload the avatar file
        const uploadedFile = await uploadAvatarFile(file, userId, courseId);
        
        if (uploadedFile) {
          // Get the URL for the file
          const fileUrl = await getFileUrl(uploadedFile.bucket_path);
          
          // Add to state with UI properties
          const newAvatar = {
            ...uploadedFile,
            uploadedAt: 'Just now',
            url: fileUrl,
          };
          
          setAvatars(prev => [newAvatar, ...prev]);
          
          // Select the new avatar if it's the first one
          if (avatars.length === 0) {
            setSelectedAvatar(newAvatar.id);
          }
        }
      } catch (error) {
        console.error(`Error uploading avatar ${file.name}:`, error);
      }
    }
    
    setIsLoading(false);
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDeleteAvatar = async (avatarId: string) => {
    if (!confirm('Are you sure you want to delete this avatar?')) return;
    
    setIsLoading(true);
    const success = await deleteFile(avatarId);
    
    if (success) {
      // Remove from state
      setAvatars(prev => prev.filter(avatar => avatar.id !== avatarId));
      
      // If the selected avatar was deleted, select the first one in the list
      if (selectedAvatar === avatarId && avatars.length > 1) {
        const remainingAvatars = avatars.filter(avatar => avatar.id !== avatarId);
        if (remainingAvatars.length > 0) {
          setSelectedAvatar(remainingAvatars[0].id);
        } else {
          setSelectedAvatar(null);
        }
      }
    } else {
      alert('Failed to delete avatar. Please try again.');
    }
    
    setIsLoading(false);
  };

  const handleSelectAvatar = (avatarId: string) => {
    setSelectedAvatar(avatarId);
  };

  // Show loading state
  if (isLoading && avatars.length === 0) {
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

  return (
    <div className="max-h-screen overflow-y-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div className="relative flex-grow max-w-md">
            <input
              type="text"
              placeholder="Search avatars..."
              className="w-full pl-3 pr-10 py-2 border border-gray-200 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-gray-300"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
              <AvatarIcon size={16} />
            </div>
          </div>

          <IconButton
            icon={<PlusIcon />}
            label="Upload Avatar"
            variant="primary"
            onClick={handleUpload}
            disabled={!courseId}
          />
          
          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            onChange={handleFileChange}
            accept=".png"
          />
        </div>

        {isLoading && (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-indigo-500"></div>
              <span className="text-sm text-gray-500">Uploading avatar...</span>
            </div>
          </div>
        )}

        {/* Selected Avatar Display */}
        {selectedAvatar && (
          <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
            <h2 className="text-lg font-medium mb-4">Selected Avatar</h2>
            <div className="flex flex-col items-center">
              {avatars.find(a => a.id === selectedAvatar)?.url && (
                <img 
                  src={avatars.find(a => a.id === selectedAvatar)?.url || ''} 
                  alt="Selected Avatar" 
                  className="rounded-full object-cover w-32 h-32 mb-4 border-2 border-indigo-500"
                />
              )}
              <p className="text-sm text-gray-500">
                {avatars.find(a => a.id === selectedAvatar)?.name}
              </p>
            </div>
          </div>
        )}
        
        {filteredAvatars.length === 0 ? (
          <EmptyState
            icon={<AvatarIcon size={48} />}
            title="No avatars found"
            description={
              searchQuery
                ? "Try a different search term"
                : courseId 
                  ? "Upload PNG avatars for this course to get started"
                  : "Select a course to manage avatars"
            }
            actionLabel={courseId ? "Upload Avatar" : ""}
            actionIcon={courseId ? <PlusIcon /> : undefined}
            onAction={courseId ? handleUpload : undefined}
          />
        ) : (
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <h2 className="text-lg font-medium p-4 border-b border-gray-200">
              {courseId ? "Course Avatar Gallery" : "Avatar Gallery"}
            </h2>
            
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 p-4">
              {filteredAvatars.map((avatar) => (
                <div 
                  key={avatar.id}
                  className={`relative cursor-pointer group ${
                    selectedAvatar === avatar.id ? 'ring-2 ring-indigo-500 rounded-lg' : ''
                  }`}
                  onClick={() => handleSelectAvatar(avatar.id)}
                >
                  <div className="aspect-square overflow-hidden rounded-lg">
                    <img 
                      src={avatar.url || '#'} 
                      alt={avatar.name}
                      className="w-full h-full object-cover transition-transform group-hover:scale-105"
                    />
                  </div>
                  
                  {/* Hover overlay with delete button */}
                  <div className="absolute inset-0 bg-black opacity-0 group-hover:opacity-40 transition-opacity rounded-lg"></div>
                  <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteAvatar(avatar.id);
                      }}
                      className="bg-red-500 hover:bg-red-600 text-white p-2 rounded-full shadow-lg transform transition-transform hover:scale-110"
                      title="Delete avatar"
                    >
                      <svg
                        width="16"
                        height="16"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M3 6h18"></path>
                        <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6"></path>
                        <path d="M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2"></path>
                      </svg>
                    </button>
                  </div>
                  
                  <div className="mt-2 text-xs text-center truncate px-2">
                    <span className="text-gray-500">{avatar.uploadedAt}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="font-medium text-gray-700 mb-2">
            Avatar Guidelines
          </h3>
          <div className="text-sm text-gray-500">
            <p>
              Upload PNG images to use as your avatar in the application.
              {courseId ? " These avatars will only be available in this course." : " Please select a course to manage avatars."}
            </p>
            <ul className="list-disc pl-5 mt-2 space-y-1">
              <li>Only PNG files are accepted</li>
              <li>Square images work best (1:1 ratio)</li>
              <li>Recommended size: 256x256 pixels or larger</li>
              <li>Maximum file size: 2MB</li>
              {courseId && <li>Avatars are specific to this course</li>}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
} 