import { supabase } from './supabase';
import type { Database } from '../types/supabase';

type ChatSessionInsert = Database['public']['Tables']['chat_sessions']['Insert'];
type ChatMessageInsert = Database['public']['Tables']['chat_messages']['Insert'];

// Get all chat sessions for a user
export async function getChatSessionsByUserId(userId: string, courseId?: string) {
  try {
    let query = supabase
      .from('chat_sessions')
      .select('*')
      .eq('user_id', userId);
    
    // If courseId is provided, filter by it
    if (courseId) {
      query = query.eq('course_id', courseId);
    }
    
    const { data, error } = await query.order('updated_at', { ascending: false });
    
    if (error) throw error;
    return data || [];
  } catch (error) {
    console.error('Error fetching chat sessions:', error);
    return [];
  }
}

// Get a single chat session by ID
export async function getChatSessionById(sessionId: string) {
  try {
    const { data, error } = await supabase
      .from('chat_sessions')
      .select('*')
      .eq('id', sessionId)
      .single();
    
    if (error) throw error;
    return data;
  } catch (error) {
    console.error(`Error fetching chat session ${sessionId}:`, error);
    return null;
  }
}

// Create a new chat session
export async function createChatSession(session: ChatSessionInsert) {
  try {
    const { data, error } = await supabase
      .from('chat_sessions')
      .insert([session])
      .select('*')
      .single();
    
    if (error) throw error;
    return data;
  } catch (error) {
    console.error('Error creating chat session:', error);
    return null;
  }
}

// Update a chat session (e.g. change title)
export async function updateChatSession(sessionId: string, title: string) {
  try {
    const { data, error } = await supabase
      .from('chat_sessions')
      .update({ title, updated_at: new Date().toISOString() })
      .eq('id', sessionId)
      .select('*')
      .single();
    
    if (error) throw error;
    return data;
  } catch (error) {
    console.error(`Error updating chat session ${sessionId}:`, error);
    return null;
  }
}

// Delete a chat session
export async function deleteChatSession(sessionId: string) {
  try {
    const { error } = await supabase
      .from('chat_sessions')
      .delete()
      .eq('id', sessionId);
    
    if (error) throw error;
    return true;
  } catch (error) {
    console.error(`Error deleting chat session ${sessionId}:`, error);
    return false;
  }
}

// Get all messages for a chat session
export async function getChatMessagesBySessionId(sessionId: string) {
  try {
    const { data, error } = await supabase
      .from('chat_messages')
      .select('*')
      .eq('session_id', sessionId)
      .order('timestamp', { ascending: true });
    
    if (error) throw error;
    return data || [];
  } catch (error) {
    console.error(`Error fetching chat messages for session ${sessionId}:`, error);
    return [];
  }
}

// Add a new message to a chat session
export async function addChatMessage(message: ChatMessageInsert) {
  try {
    const { data, error } = await supabase
      .from('chat_messages')
      .insert([message])
      .select('*')
      .single();
    
    if (error) throw error;
    
    // Update the session's updated_at timestamp
    await supabase
      .from('chat_sessions')
      .update({ updated_at: new Date().toISOString() })
      .eq('id', message.session_id);
    
    return data;
  } catch (error) {
    console.error('Error adding chat message:', error);
    return null;
  }
}

// Get chat sessions with message counts for a user and course
export async function getChatSessionsWithMessageCount(userId: string, courseId?: string) {
  try {
    let query = supabase
      .from('chat_sessions')
      .select(`
        *,
        chat_messages:chat_messages(count)
      `)
      .eq('user_id', userId);
    
    // If courseId is provided, filter by it
    if (courseId) {
      query = query.eq('course_id', courseId);
    }
    
    const { data, error } = await query.order('updated_at', { ascending: false });
    
    if (error) throw error;
    
    // Filter out sessions with no messages
    const sessionsWithMessages = data
      .filter(session => session.chat_messages[0].count > 0)
      .map(session => ({
        ...session,
        messageCount: session.chat_messages[0].count
      }));
    
    return sessionsWithMessages || [];
  } catch (error) {
    console.error('Error fetching chat sessions with message count:', error);
    return [];
  }
}

// Get the first message of each role for preview
export async function getChatMessagePreview(sessionId: string) {
  try {
    const { data, error } = await supabase
      .from('chat_messages')
      .select('*')
      .eq('session_id', sessionId)
      .order('timestamp', { ascending: true })
      .limit(2);
    
    if (error) throw error;
    return data || [];
  } catch (error) {
    console.error(`Error fetching chat message preview for session ${sessionId}:`, error);
    return [];
  }
} 