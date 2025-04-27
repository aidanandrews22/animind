import { createClient } from '@supabase/supabase-js';
import type { Database } from '../types/supabase';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase credentials');
}

export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey);

// Function to ensure user exists in the database
export async function ensureUserExists(clerkId: string, email?: string | null) {
  try {
    // First check if user exists
    const { data: existingUser } = await supabase
      .from('users')
      .select('id')
      .eq('clerk_id', clerkId)
      .single();
    
    if (existingUser) {
      // User exists, update last_login
      await supabase
        .from('users')
        .update({ last_login: new Date().toISOString() })
        .eq('clerk_id', clerkId);
      
      return existingUser.id;
    } else {
      // User doesn't exist, create new user
      const { data: newUser, error } = await supabase
        .from('users')
        .insert([
          { 
            clerk_id: clerkId,
            email: email || null,
          }
        ])
        .select('id')
        .single();
      
      if (error) throw error;
      return newUser?.id;
    }
  } catch (error) {
    console.error('Error ensuring user exists:', error);
    return null;
  }
} 