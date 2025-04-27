import { useState, useEffect, useRef } from "react";
import { PlusIcon, BookIcon } from "./Icons";
import IconButton from "./IconButton";
import EmptyState from "./EmptyState";
import { useSupabase } from "../hooks/useSupabase";
import { getFilesByUserId, uploadFile, getFileUrl, deleteFile } from "../services/fileService";
import type { Database } from "../types/supabase";

type ContentFile = Database['public']['Tables']['files']['Row'] & {
  uploadedAt?: string;
  url?: string;
};

interface ContentTabProps {
  courseId: string;
  content: string[];
}

export default function ContentTab({
  courseId,
}: ContentTabProps) {
  const { userId, isLoading: isUserLoading } = useSupabase();
  const [files, setFiles] = useState<ContentFile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    async function loadFiles() {
      if (!userId || !courseId) return;
      
      setIsLoading(true);
      const filesData = await getFilesByUserId(userId, courseId);
      
      // Add UI-specific properties and get URLs for files
      const formattedFiles = await Promise.all(filesData.map(async file => {
        const url = await getFileUrl(file.bucket_path);
        return {
          ...file,
          uploadedAt: formatDate(file.created_at),
          url: url,
        };
      }));
      
      setFiles(formattedFiles);
      setIsLoading(false);
    }
    
    if (!isUserLoading) {
      loadFiles();
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

  const formatFileSize = (sizeInBytes: number) => {
    if (sizeInBytes < 1024) return `${sizeInBytes} B`;
    if (sizeInBytes < 1024 * 1024) return `${(sizeInBytes / 1024).toFixed(1)} KB`;
    return `${(sizeInBytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const filteredFiles = files.filter((file) =>
    file.name.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const handleUpload = () => {
    // Trigger file input click
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;
    if (!selectedFiles || !userId || !courseId) return;
    
    setIsLoading(true);
    
    // Upload each file
    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];
      
      try {
        // Create a simpler type that doesn't need to match the database schema exactly
        // The uploadFile function will handle the proper conversion internally
        const fileData = {
          user_id: userId,
          course_id: courseId,
          name: file.name,
          type: file.type.split('/')[1] || file.type,
          size: file.size
        };
        
        // Upload the file to Supabase
        // @ts-ignore - The uploadFile function is designed to handle this type of object
        const uploadedFile = await uploadFile(fileData, file);
        
        if (uploadedFile) {
          // Get the URL for the file
          const fileUrl = await getFileUrl(uploadedFile.bucket_path);
          
          // Add to state with UI properties
          setFiles(prev => [{
            ...uploadedFile,
            uploadedAt: 'Just now',
            url: fileUrl,
          }, ...prev]);
        }
      } catch (error) {
        console.error(`Error uploading file ${file.name}:`, error);
      }
    }
    
    setIsLoading(false);
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDeleteFile = async (fileId: string) => {
    if (!confirm('Are you sure you want to delete this file?')) return;
    
    setIsLoading(true);
    const success = await deleteFile(fileId);
    
    if (success) {
      // Remove from state
      setFiles(prev => prev.filter(file => file.id !== fileId));
    } else {
      alert('Failed to delete file. Please try again.');
    }
    
    setIsLoading(false);
  };

  const getFileIcon = (fileType: string) => {
    switch (fileType) {
      case "pdf":
        return (
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            className="text-red-400"
          >
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <path d="M9 15h6"></path>
            <path d="M9 11h6"></path>
          </svg>
        );
      case "docx":
      case "doc":
        return (
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            className="text-blue-400"
          >
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
        );
      case "pptx":
      case "ppt":
        return (
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            className="text-orange-400"
          >
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <rect x="8" y="12" width="8" height="6" rx="1"></rect>
          </svg>
        );
      default:
        return (
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            className="text-gray-400"
          >
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
        );
    }
  };

  // Show loading state
  if (isLoading && files.length === 0) {
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
              placeholder="Search content files..."
              className="w-full pl-3 pr-10 py-2 border border-gray-200 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-gray-300"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
              <BookIcon size={16} />
            </div>
          </div>

          <IconButton
            icon={<PlusIcon />}
            label="Upload Content"
            variant="primary"
            onClick={handleUpload}
          />
          
          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            onChange={handleFileChange}
            multiple
            accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.md,.csv"
          />
        </div>

        {isLoading && (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-indigo-500"></div>
              <span className="text-sm text-gray-500">Uploading files...</span>
            </div>
          </div>
        )}

        {filteredFiles.length === 0 ? (
          <EmptyState
            icon={<BookIcon size={48} />}
            title="No content files found"
            description={
              searchQuery
                ? "Try a different search term"
                : "Upload content files to get started"
            }
            actionLabel="Upload Content"
            actionIcon={<PlusIcon />}
            onAction={handleUpload}
          />
        ) : (
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div className="grid grid-cols-12 text-xs font-medium text-gray-500 bg-gray-50 p-4 border-b border-gray-200">
              <div className="col-span-5">Name</div>
              <div className="col-span-2">Type</div>
              <div className="col-span-2">Size</div>
              <div className="col-span-2">Uploaded</div>
              <div className="col-span-1">Action</div>
            </div>

            <div className="divide-y divide-gray-100">
              {filteredFiles.map((file) => (
                <div
                  key={file.id}
                  className="grid grid-cols-12 p-4 items-center text-sm hover:bg-gray-50"
                >
                  <div className="col-span-5 flex items-center gap-3">
                    <div className="flex-shrink-0">
                      {getFileIcon(file.type)}
                    </div>
                    <a 
                      href={file.url || '#'} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="truncate text-blue-600 hover:underline"
                    >
                      {file.name}
                    </a>
                  </div>
                  <div className="col-span-2 text-gray-500 uppercase">
                    {file.type}
                  </div>
                  <div className="col-span-2 text-gray-500">{formatFileSize(file.size)}</div>
                  <div className="col-span-2 text-gray-500">
                    {file.uploadedAt}
                  </div>
                  <div className="col-span-1 text-right">
                    <button 
                      onClick={() => handleDeleteFile(file.id)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <svg
                        width="16"
                        height="16"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                      >
                        <path d="M3 6h18"></path>
                        <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6"></path>
                        <path d="M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="font-medium text-gray-700 mb-2">
            Supported File Types
          </h3>
          <div className="text-sm text-gray-500">
            <p>
              Upload documents, presentations, and text files to enhance your
              course.
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              <span className="px-2 py-1 bg-white border border-gray-200 rounded text-xs">
                .PDF
              </span>
              <span className="px-2 py-1 bg-white border border-gray-200 rounded text-xs">
                .DOCX
              </span>
              <span className="px-2 py-1 bg-white border border-gray-200 rounded text-xs">
                .PPT
              </span>
              <span className="px-2 py-1 bg-white border border-gray-200 rounded text-xs">
                .TXT
              </span>
              <span className="px-2 py-1 bg-white border border-gray-200 rounded text-xs">
                .MD
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
