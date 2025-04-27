import { createContext, useEffect, useState, ReactNode } from 'react';
import { useUser } from '@clerk/clerk-react';
import { ensureUserExists } from '../services/supabase';

type SupabaseContextType = {
  userId: string | null;
  isLoading: boolean;
  error: Error | null;
};

const SupabaseContext = createContext<SupabaseContextType>({
  userId: null,
  isLoading: true,
  error: null,
});

interface SupabaseProviderProps {
  children: ReactNode;
}

export const SupabaseProvider = ({ children }: SupabaseProviderProps) => {
  const { user, isLoaded: isClerkLoaded } = useUser();
  const [userId, setUserId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  useEffect(() => {
    const initializeSupabase = async () => {
      // Only proceed if Clerk has loaded the user
      if (!isClerkLoaded) return;
      
      setIsLoading(true);
      setError(null);
      
      try {
        if (user) {
          // Ensure the user exists in our Supabase database
          const supabaseUserId = await ensureUserExists(user.id, user.primaryEmailAddress?.emailAddress);
          
          if (supabaseUserId) {
            setUserId(supabaseUserId);
          } else {
            throw new Error('Failed to initialize user in Supabase');
          }
        } else {
          // User is not logged in
          setUserId(null);
        }
      } catch (err) {
        console.error('Error initializing Supabase user:', err);
        setError(err instanceof Error ? err : new Error('Unknown error'));
      } finally {
        setIsLoading(false);
      }
    };
    
    initializeSupabase();
  }, [user, isClerkLoaded]);
  
  const value = {
    userId,
    isLoading,
    error,
  };
  
  return (
    <SupabaseContext.Provider value={value}>
      {children}
    </SupabaseContext.Provider>
  );
};

// Export the context for use in the hooks file
export { SupabaseContext }; 