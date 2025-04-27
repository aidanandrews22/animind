import { useState, useEffect } from "react";
import { SearchIcon } from "./Icons";
import EmptyState from "./EmptyState";
import { useSupabase } from "../hooks/useSupabase";
import { getChatSessionsWithMessageCount, getChatMessagePreview } from "../services/chatService";
import type { Database } from "../types/supabase";

type ChatSession = Database['public']['Tables']['chat_sessions']['Row'] & {
  preview?: string;
  lastMessage?: string;
  messageCount?: number;
};

interface ChatHistoryProps {
  courseId: string;
  onSelectSession: (sessionId: string) => void;
  isActive?: boolean;
}

export default function ChatHistory({
  courseId,
  onSelectSession,
  isActive = false,
}: ChatHistoryProps) {
  const { userId, isLoading: isUserLoading } = useSupabase();
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredSessions, setFilteredSessions] = useState<ChatSession[]>([]);
  const [lastRefreshTime, setLastRefreshTime] = useState<number>(Date.now());

  // Load chat sessions on mount or when isActive changes
  useEffect(() => {
    if (isActive) {
      // Refresh the data when the component becomes active
      setLastRefreshTime(Date.now());
    }
  }, [isActive]);

  useEffect(() => {
    async function loadChatSessions() {
      if (!userId) return;
      
      setIsLoading(true);
      const sessionsData = await getChatSessionsWithMessageCount(userId, courseId);
      
      // Add preview and last message for each session
      const sessionsWithPreviews = await Promise.all(
        sessionsData.map(async (session) => {
          const previewMessages = await getChatMessagePreview(session.id);
          
          let preview = "";
          let lastMessage = "";
          
          if (previewMessages.length > 0) {
            // First message is usually the user's question
            preview = previewMessages[0].content.substring(0, 100) + (previewMessages[0].content.length > 100 ? "..." : "");
            
            // Second message if available would be the assistant's response
            if (previewMessages.length > 1) {
              lastMessage = previewMessages[1].content.substring(0, 100) + (previewMessages[1].content.length > 100 ? "..." : "");
            } else {
              lastMessage = "Waiting for response...";
            }
          }
          
          return {
            ...session,
            preview: preview || "No preview available",
            lastMessage: lastMessage || "No messages available",
          };
        })
      );
      
      setSessions(sessionsWithPreviews);
      setFilteredSessions(sessionsWithPreviews);
      setIsLoading(false);
    }
    
    if (!isUserLoading) {
      loadChatSessions();
    }
  }, [userId, isUserLoading, courseId, lastRefreshTime]);

  useEffect(() => {
    if (searchQuery.trim() === "") {
      setFilteredSessions(sessions);
    } else {
      const query = searchQuery.toLowerCase();
      const filtered = sessions.filter(
        (session) =>
          session.title.toLowerCase().includes(query) ||
          (session.preview && session.preview.toLowerCase().includes(query)),
      );
      setFilteredSessions(filtered);
    }
  }, [searchQuery, sessions]);

  // Format date for display
  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
    });
  };

  // Show loading state
  if (isLoading || isUserLoading) {
    return (
      <div className="max-h-screen overflow-y-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-xl font-semibold text-adaptive mb-6">
            Chat History
          </h2>
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-h-screen overflow-y-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-xl font-semibold text-adaptive mb-6">
          Chat History
        </h2>

        <div className="bg-surface border border-adaptive rounded-lg overflow-hidden">
          <div className="p-4 border-b border-adaptive">
            <div className="relative">
              <SearchIcon
                className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                size={16}
              />
              <input
                type="text"
                placeholder="Search conversations..."
                className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-md text-sm focus:outline-none"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          {filteredSessions.length === 0 ? (
            <EmptyState
              icon={<SearchIcon size={48} />}
              title="No conversations found"
              description={searchQuery.trim() ? "Try searching with different keywords" : "Send a message in the chat to start a conversation"}
              actionLabel={searchQuery.trim() ? "Clear Search" : undefined}
              onAction={searchQuery.trim() ? () => setSearchQuery("") : undefined}
            />
          ) : (
            <div className="divide-y divide-adaptive">
              {filteredSessions.map((session) => (
                <div
                  key={session.id}
                  onClick={() => onSelectSession(session.id)}
                  className="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <div className="flex justify-between items-start mb-1">
                    <h3 className="font-medium text-gray-800">
                      {session.title}
                    </h3>
                    <span className="text-xs text-gray-500">
                      {formatDate(session.updated_at)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 line-clamp-1 mb-1">
                    {session.preview}
                  </p>
                  <div className="flex justify-between items-center">
                    <p className="text-xs text-gray-400 italic line-clamp-1">
                      {session.lastMessage}
                    </p>
                    <span className="text-xs bg-gray-100 px-2 py-0.5 rounded-full">
                      {session.messageCount} message{session.messageCount !== 1 ? "s" : ""}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
