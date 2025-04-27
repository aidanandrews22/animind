export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[];

export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string;
          clerk_id: string;
          email: string | null;
          username: string | null;
          created_at: string;
          last_login: string;
        };
        Insert: {
          id?: string;
          clerk_id: string;
          email?: string | null;
          username?: string | null;
          created_at?: string;
          last_login?: string;
        };
        Update: {
          id?: string;
          clerk_id?: string;
          email?: string | null;
          username?: string | null;
          created_at?: string;
          last_login?: string;
        };
      };
      courses: {
        Row: {
          id: string;
          user_id: string;
          title: string;
          description: string | null;
          category: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          title: string;
          description?: string | null;
          category?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          title?: string;
          description?: string | null;
          category?: string | null;
          created_at?: string;
          updated_at?: string;
        };
      };
      files: {
        Row: {
          id: string;
          user_id: string;
          course_id: string | null;
          name: string;
          type: string;
          size: number;
          bucket_path: string;
          created_at: string;
          is_avatar?: boolean;
        };
        Insert: {
          id?: string;
          user_id: string;
          course_id?: string | null;
          name: string;
          type: string;
          size: number;
          bucket_path: string;
          created_at?: string;
          is_avatar?: boolean;
        };
        Update: {
          id?: string;
          user_id?: string;
          course_id?: string | null;
          name?: string;
          type?: string;
          size?: number;
          bucket_path?: string;
          created_at?: string;
          is_avatar?: boolean;
        };
      };
      chat_sessions: {
        Row: {
          id: string;
          user_id: string;
          course_id: string | null;
          title: string;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          course_id?: string | null;
          title: string;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          course_id?: string | null;
          title?: string;
          created_at?: string;
          updated_at?: string;
        };
      };
      chat_messages: {
        Row: {
          id: string;
          session_id: string;
          role: 'user' | 'assistant';
          content: string;
          timestamp: string;
        };
        Insert: {
          id?: string;
          session_id: string;
          role: 'user' | 'assistant';
          content: string;
          timestamp?: string;
        };
        Update: {
          id?: string;
          session_id?: string;
          role?: 'user' | 'assistant';
          content?: string;
          timestamp?: string;
        };
      };
      videos: {
        Row: {
          id: string;
          user_id: string;
          course_id: string | null;
          title: string;
          description: string | null;
          bucket_path: string;
          thumbnail_path: string | null;
          status: 'processing' | 'completed' | 'failed';
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          course_id?: string | null;
          title: string;
          description?: string | null;
          bucket_path: string;
          thumbnail_path?: string | null;
          status?: 'processing' | 'completed' | 'failed';
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          course_id?: string | null;
          title?: string;
          description?: string | null;
          bucket_path?: string;
          thumbnail_path?: string | null;
          status?: 'processing' | 'completed' | 'failed';
          created_at?: string;
          updated_at?: string;
        };
      };
    };
  };
} 