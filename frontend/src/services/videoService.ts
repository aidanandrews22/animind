import { supabase } from './supabase';
import type { Database } from '../types/supabase';

type VideoInsert = Database['public']['Tables']['videos']['Insert'];
type VideoUpdate = Database['public']['Tables']['videos']['Update'];

const BUCKET_NAME = 'animind';

// Get all videos for a user
export async function getVideosByUserId(userId: string, courseId?: string) {
  try {
    let query = supabase
      .from('videos')
      .select('*')
      .eq('user_id', userId);
    
    // If courseId is provided, filter by it
    if (courseId) {
      query = query.eq('course_id', courseId);
    }
    
    const { data, error } = await query.order('created_at', { ascending: false });
    
    if (error) throw error;
    return data || [];
  } catch (error) {
    console.error('Error fetching videos:', error);
    return [];
  }
}

// Get a single video by ID
export async function getVideoById(videoId: string) {
  try {
    const { data, error } = await supabase
      .from('videos')
      .select('*')
      .eq('id', videoId)
      .single();
    
    if (error) throw error;
    return data;
  } catch (error) {
    console.error(`Error fetching video ${videoId}:`, error);
    return null;
  }
}

// Create a new video record (without the actual video file yet)
export async function createVideo(video: VideoInsert) {
  try {
    const { data, error } = await supabase
      .from('videos')
      .insert([video])
      .select('*')
      .single();
    
    if (error) throw error;
    return data;
  } catch (error) {
    console.error('Error creating video record:', error);
    return null;
  }
}

// Get public URLs for a video and its thumbnail
export async function getVideoUrls(videoId: string) {
  try {
    const { data: video, error } = await supabase
      .from('videos')
      .select('bucket_path, thumbnail_path, id')
      .eq('id', videoId)
      .single();
    
    if (error) throw error;
    if (!video) throw new Error('Video not found');
    
    const videoUrl = supabase.storage
      .from(BUCKET_NAME)
      .getPublicUrl(video.bucket_path).data.publicUrl;
    
    let thumbnailUrl = null;
    
    // If video doesn't have a thumbnail, generate one
    if (!video.thumbnail_path) {
      try {
        await generateAndSaveThumbnailFromUrl(videoId, videoUrl);
        
        // Fetch the updated video record with the new thumbnail path
        const { data: updatedVideo } = await supabase
          .from('videos')
          .select('thumbnail_path')
          .eq('id', videoId)
          .single();
          
        if (updatedVideo && updatedVideo.thumbnail_path) {
          thumbnailUrl = supabase.storage
            .from(BUCKET_NAME)
            .getPublicUrl(updatedVideo.thumbnail_path).data.publicUrl;
        }
      } catch (thumbnailError) {
        console.error('Error generating thumbnail on fetch:', thumbnailError);
      }
    } else {
      thumbnailUrl = supabase.storage
        .from(BUCKET_NAME)
        .getPublicUrl(video.thumbnail_path).data.publicUrl;
    }
    
    return { videoUrl, thumbnailUrl };
  } catch (error) {
    console.error(`Error getting URLs for video ${videoId}:`, error);
    return { videoUrl: null, thumbnailUrl: null };
  }
}

// Generate a thumbnail from a video URL and save it
async function generateAndSaveThumbnailFromUrl(videoId: string, videoUrl: string) {
  try {
    // Get the video record
    const { data: video } = await supabase
      .from('videos')
      .select('*')
      .eq('id', videoId)
      .single();
      
    if (!video) throw new Error('Video not found');
    
    // Create a video element to capture a frame
    const vidElement = document.createElement('video');
    vidElement.crossOrigin = 'anonymous';
    
    // Create a promise to handle video loading
    await new Promise((resolve, reject) => {
      vidElement.onloadedmetadata = () => {
        // Set to a random position between 10% and 80% of the video
        const randomPosition = Math.random() * 0.7 + 0.1; // 10% to 80%
        vidElement.currentTime = vidElement.duration * randomPosition;
      };
      
      vidElement.onseeked = () => {
        try {
          // Create canvas and draw the video frame
          const canvas = document.createElement('canvas');
          canvas.width = vidElement.videoWidth;
          canvas.height = vidElement.videoHeight;
          const ctx = canvas.getContext('2d');
          
          if (ctx) {
            ctx.drawImage(vidElement, 0, 0, canvas.width, canvas.height);
            
            // Convert to blob
            canvas.toBlob(async (blob) => {
              if (blob) {
                // Upload the thumbnail
                const thumbnailPath = `thumbnails/${video.user_id}/${videoId}/${Date.now()}.jpg`;
                
                const { error: uploadError } = await supabase.storage
                  .from(BUCKET_NAME)
                  .upload(thumbnailPath, blob, {
                    cacheControl: '3600',
                    upsert: true
                  });
                  
                if (uploadError) throw uploadError;
                
                // Update video record
                await supabase
                  .from('videos')
                  .update({ thumbnail_path: thumbnailPath })
                  .eq('id', videoId);
                  
                resolve(thumbnailPath);
              } else {
                reject(new Error('Failed to create thumbnail blob'));
              }
            }, 'image/jpeg', 0.85);
          } else {
            reject(new Error('Failed to get canvas context'));
          }
        } catch (err) {
          reject(err);
        }
      };
      
      vidElement.onerror = () => {
        reject(new Error('Error loading video'));
      };
      
      // Start loading the video
      vidElement.src = videoUrl;
      vidElement.load();
    });
    
    return true;
  } catch (error) {
    console.error(`Error generating thumbnail for video ${videoId}:`, error);
    return false;
  }
}

// Upload a video file to Supabase storage and update the video record
export async function uploadVideoFile(videoId: string, videoFile: File | Blob, thumbnailFile?: File | Blob) {
  try {
    // First get the video record
    const { data: video, error: fetchError } = await supabase
      .from('videos')
      .select('*')
      .eq('id', videoId)
      .single();
    
    if (fetchError) throw fetchError;
    if (!video) throw new Error('Video record not found');
    
    // Create unique file paths
    const videoPath = `videos/${video.user_id}/${videoId}/${Date.now()}.mp4`;
    let thumbnailPath = null;
    
    // Upload video to storage bucket
    const { error: videoUploadError } = await supabase.storage
      .from(BUCKET_NAME)
      .upload(videoPath, videoFile, {
        cacheControl: '3600',
        upsert: true
      });
    
    if (videoUploadError) throw videoUploadError;
    
    // If a thumbnail wasn't provided, generate one from the video
    if (!thumbnailFile) {
      thumbnailFile = await generateThumbnail(videoFile);
    }
    
    // Upload thumbnail
    if (thumbnailFile) {
      thumbnailPath = `thumbnails/${video.user_id}/${videoId}/${Date.now()}.jpg`;
      
      const { error: thumbnailUploadError } = await supabase.storage
        .from(BUCKET_NAME)
        .upload(thumbnailPath, thumbnailFile, {
          cacheControl: '3600',
          upsert: true
        });
      
      if (thumbnailUploadError) throw thumbnailUploadError;
    }
    
    // Update video record with file paths and status
    const updates: VideoUpdate = {
      bucket_path: videoPath,
      status: 'completed',
    };
    
    if (thumbnailPath) {
      updates.thumbnail_path = thumbnailPath;
    }
    
    const { data: updatedVideo, error: updateError } = await supabase
      .from('videos')
      .update(updates)
      .eq('id', videoId)
      .select('*')
      .single();
    
    if (updateError) throw updateError;
    return updatedVideo;
  } catch (error) {
    console.error(`Error uploading video file for video ${videoId}:`, error);
    
    // Update status to failed
    await supabase
      .from('videos')
      .update({ status: 'failed' })
      .eq('id', videoId);
    
    return null;
  }
}

// Delete a video
export async function deleteVideo(videoId: string) {
  try {
    // First get the video to find the paths
    const { data: video, error: fetchError } = await supabase
      .from('videos')
      .select('bucket_path, thumbnail_path')
      .eq('id', videoId)
      .single();
    
    if (fetchError) throw fetchError;
    if (!video) throw new Error('Video not found');
    
    // Create an array of paths to delete
    const pathsToDelete = [video.bucket_path];
    if (video.thumbnail_path) {
      pathsToDelete.push(video.thumbnail_path);
    }
    
    // Delete from storage
    const { error: storageError } = await supabase.storage
      .from(BUCKET_NAME)
      .remove(pathsToDelete);
    
    if (storageError) throw storageError;
    
    // Delete database record
    const { error: deleteError } = await supabase
      .from('videos')
      .delete()
      .eq('id', videoId);
    
    if (deleteError) throw deleteError;
    return true;
  } catch (error) {
    console.error(`Error deleting video ${videoId}:`, error);
    return false;
  }
}

// Generate a thumbnail from a video file
export async function generateThumbnail(videoFile: File | Blob): Promise<Blob> {
  return new Promise((resolve) => {
    try {
      const video = document.createElement('video');
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      // Create a temporary URL for the video
      const videoUrl = URL.createObjectURL(videoFile);
      
      // Setup video event handlers
      video.addEventListener('loadeddata', () => {
        // Set canvas dimensions to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Choose a random position between 10% and 80% of the video
        const randomPosition = Math.random() * 0.7 + 0.1; // 10% to 80%
        video.currentTime = Math.min(video.duration * randomPosition, video.duration - 0.1);
      });
      
      video.addEventListener('seeked', () => {
        // Draw the video frame on the canvas
        if (ctx) {
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        }
        
        // Convert canvas to blob
        canvas.toBlob((blob) => {
          // Clean up
          URL.revokeObjectURL(videoUrl);
          if (blob) {
            resolve(blob);
          } else {
            // Create an empty blob if thumbnail generation fails
            resolve(new Blob([], { type: 'image/jpeg' }));
          }
        }, 'image/jpeg', 0.85);
      });
      
      // Handle errors
      video.addEventListener('error', () => {
        URL.revokeObjectURL(videoUrl);
        // Create an empty blob if video loading fails
        resolve(new Blob([], { type: 'image/jpeg' }));
      });
      
      // Set the video source and begin loading
      video.src = videoUrl;
      video.load();
    } catch (error) {
      console.error('Error generating thumbnail:', error);
      // Create an empty blob if there's an exception
      resolve(new Blob([], { type: 'image/jpeg' }));
    }
  });
}

// Rename a video (update title and/or description)
export async function renameVideo(videoId: string, updates: { title?: string; description?: string }) {
  try {
    // Validate the updates
    if (!updates.title && !updates.description) {
      throw new Error('At least one of title or description must be provided');
    }
    
    // Build the update object with only the provided fields
    const videoUpdates: VideoUpdate = {};
    if (updates.title !== undefined) videoUpdates.title = updates.title;
    if (updates.description !== undefined) videoUpdates.description = updates.description;
    
    // Update the video record
    const { data, error } = await supabase
      .from('videos')
      .update(videoUpdates)
      .eq('id', videoId)
      .select('*')
      .single();
    
    if (error) throw error;
    return data;
  } catch (error) {
    console.error(`Error renaming video ${videoId}:`, error);
    return null;
  }
} 