import { supabase } from './supabase';
import type { Database } from '../types/supabase';

type CourseInsert = Database['public']['Tables']['courses']['Insert'];
type CourseUpdate = Database['public']['Tables']['courses']['Update'];

// Get all courses for a user
export async function getCoursesByUserId(userId: string) {
  try {
    const { data, error } = await supabase
      .from('courses')
      .select('*')
      .eq('user_id', userId)
      .order('updated_at', { ascending: false });
    
    if (error) throw error;
    return data || [];
  } catch (error) {
    console.error('Error fetching courses:', error);
    return [];
  }
}

// Get a single course by ID
export async function getCourseById(courseId: string) {
  try {
    const { data, error } = await supabase
      .from('courses')
      .select('*')
      .eq('id', courseId)
      .single();
    
    if (error) throw error;
    return data;
  } catch (error) {
    console.error(`Error fetching course ${courseId}:`, error);
    return null;
  }
}

// Create a new course
export async function createCourse(course: CourseInsert) {
  try {
    const { data, error } = await supabase
      .from('courses')
      .insert([course])
      .select('*')
      .single();
    
    if (error) throw error;
    return data;
  } catch (error) {
    console.error('Error creating course:', error);
    return null;
  }
}

// Update a course
export async function updateCourse(courseId: string, updates: CourseUpdate) {
  try {
    const { data, error } = await supabase
      .from('courses')
      .update(updates)
      .eq('id', courseId)
      .select('*')
      .single();
    
    if (error) throw error;
    return data;
  } catch (error) {
    console.error(`Error updating course ${courseId}:`, error);
    return null;
  }
}

// Delete a course
export async function deleteCourse(courseId: string) {
  try {
    const { error } = await supabase
      .from('courses')
      .delete()
      .eq('id', courseId);
    
    if (error) throw error;
    return true;
  } catch (error) {
    console.error(`Error deleting course ${courseId}:`, error);
    return false;
  }
} 