import { supabase } from './supabase';
import type { Database } from '../types/supabase';

type File = Database['public']['Tables']['files']['Row'];
type FileInsert = Database['public']['Tables']['files']['Insert'];

const BUCKET_NAME = 'animind';

// Get all files for a user
export async function getFilesByUserId(userId: string, courseId?: string) {
  try {
    let query = supabase
      .from('files')
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
    console.error('Error fetching files:', error);
    return [];
  }
}

// Get a single file by ID
export async function getFileById(fileId: string) {
  try {
    const { data, error } = await supabase
      .from('files')
      .select('*')
      .eq('id', fileId)
      .single();
    
    if (error) throw error;
    return data;
  } catch (error) {
    console.error(`Error fetching file ${fileId}:`, error);
    return null;
  }
}

// Upload a file to Supabase storage and create a database record
export async function uploadFile(file: File, fileData: Blob) {
  try {
    // Create a unique file path
    const filePath = `${file.user_id}/${file.course_id ? file.course_id + '/' : ''}${Date.now()}_${file.name}`;
    
    // Upload to storage bucket
    const { error: uploadError } = await supabase.storage
      .from(BUCKET_NAME)
      .upload(filePath, fileData, {
        cacheControl: '3600',
        upsert: false
      });
    
    if (uploadError) throw uploadError;
    
    // Create database record
    const fileRecord: FileInsert = {
      user_id: file.user_id,
      course_id: file.course_id,
      name: file.name,
      type: file.type,
      size: file.size,
      bucket_path: filePath
    };
    
    const { data: insertedFile, error: insertError } = await supabase
      .from('files')
      .insert([fileRecord])
      .select('*')
      .single();
    
    if (insertError) throw insertError;
    return insertedFile;
  } catch (error) {
    console.error('Error uploading file:', error);
    return null;
  }
}

// Get a public URL for a file
export async function getFileUrl(bucketPath: string) {
  try {
    const { data } = supabase.storage
      .from(BUCKET_NAME)
      .getPublicUrl(bucketPath);
    
    return data.publicUrl;
  } catch (error) {
    console.error(`Error getting public URL for file ${bucketPath}:`, error);
    return null;
  }
}

// Delete a file
export async function deleteFile(fileId: string) {
  try {
    // First get the file to find the bucketPath
    const { data: file, error: fetchError } = await supabase
      .from('files')
      .select('bucket_path')
      .eq('id', fileId)
      .single();
    
    if (fetchError) throw fetchError;
    if (!file) throw new Error('File not found');
    
    // Delete from storage
    const { error: storageError } = await supabase.storage
      .from(BUCKET_NAME)
      .remove([file.bucket_path]);
    
    if (storageError) throw storageError;
    
    // Delete database record
    const { error: deleteError } = await supabase
      .from('files')
      .delete()
      .eq('id', fileId);
    
    if (deleteError) throw deleteError;
    return true;
  } catch (error) {
    console.error(`Error deleting file ${fileId}:`, error);
    return false;
  }
}

// Get avatar files for a user
export async function getAvatarFilesByUserId(userId: string, courseId?: string) {
  try {
    let query = supabase
      .from('files')
      .select('*')
      .eq('user_id', userId)
      .eq('is_avatar', true);
    
    // If courseId is provided, filter by it
    if (courseId) {
      query = query.eq('course_id', courseId);
    }
    
    const { data, error } = await query.order('created_at', { ascending: false });
    
    if (error) throw error;
    return data || [];
  } catch (error) {
    console.error('Error fetching avatar files:', error);
    return [];
  }
}

// Upload an avatar file
export async function uploadAvatarFile(file: Blob, userId: string, courseId?: string) {
  try {
    // Create a unique file path for avatars
    const fileName = file instanceof File ? file.name : 'avatar.png';
    const filePath = `${userId}/${courseId ? courseId + '/' : ''}avatars/${Date.now()}_${fileName}`;
    
    // Upload to storage bucket
    const { error: uploadError } = await supabase.storage
      .from(BUCKET_NAME)
      .upload(filePath, file, {
        cacheControl: '3600',
        upsert: false
      });
    
    if (uploadError) throw uploadError;
    
    // Create database record with is_avatar flag
    const fileRecord: FileInsert = {
      user_id: userId,
      course_id: courseId || null,
      name: fileName,
      type: file.type ? (file.type.split('/')[1] || 'png') : 'png',
      size: file.size,
      bucket_path: filePath,
      is_avatar: true
    };
    
    const { data: insertedFile, error: insertError } = await supabase
      .from('files')
      .insert([fileRecord])
      .select('*')
      .single();
    
    if (insertError) throw insertError;
    return insertedFile;
  } catch (error) {
    console.error('Error uploading avatar file:', error);
    return null;
  }
} 