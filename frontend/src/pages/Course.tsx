import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import ChatInterface from "../components/ChatInterface";
import ChatHistory from "../components/ChatHistory";
import VideoTab from "../components/VideoTab";
import ContentTab from "../components/ContentTab";
import AvatarTab from "../components/AvatarTab";
import { useSupabase } from "../hooks/useSupabase";
import { getCourseById } from "../services/courseService";
import type { Database } from "../types/supabase";

type TabType = "chat" | "videos" | "content" | "history" | "avatars";

type Course = Database['public']['Tables']['courses']['Row'] & {
  lastAccessed?: string;
  progress?: number;
  content?: string[];
};

export default function CoursePage() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const { userId, isLoading: isUserLoading } = useSupabase();
  const [currentCourse, setCurrentCourse] = useState<Course | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>("chat");
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);

  useEffect(() => {
    async function loadCourseDetails() {
      if (!courseId || !userId) return;
      
      setIsLoading(true);
      
      // Fetch course details from Supabase
      const courseData = await getCourseById(courseId);
      
      if (courseData) {
        setCurrentCourse({
          ...courseData,
          content: [],  // Initialize empty content array (actual content will come from files table)
          lastAccessed: formatDate(courseData.updated_at)
        });
      }
      
      setIsLoading(false);
    }
    
    if (!isUserLoading && courseId) {
      loadCourseDetails();
    }
  }, [courseId, userId, isUserLoading]);

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

  const handleBackToDashboard = () => {
    navigate("/");
  };

  const handleTabChange = (tab: string) => {
    setActiveTab(tab as TabType);
    // Clear selected session when leaving the chat tab
    if (tab !== 'chat') {
      setSelectedSessionId(null);
    }
  };

  const handleSelectChatSession = async (sessionId: string) => {
    setSelectedSessionId(sessionId);
    setActiveTab("chat");
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Loading state for the entire app
  if (isUserLoading) {
    return (
      <div className="min-h-screen flex flex-col bg-background text-adaptive">
        <main className="flex-grow flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mb-4"></div>
            <p className="text-xl">Loading user data...</p>
          </div>
        </main>
      </div>
    );
  }

  // Loading state for course details
  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col bg-background text-adaptive">
        <Sidebar
          currentCourse={
            currentCourse
              ? { id: currentCourse.id, title: currentCourse.title }
              : null
          }
          activeTab={activeTab}
          onTabChange={handleTabChange}
          onBackToDashboard={handleBackToDashboard}
          isOpen={sidebarOpen}
          onToggle={toggleSidebar}
        />
        <main className="flex-grow flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mb-4"></div>
            <p className="text-xl">Loading course data...</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-background text-adaptive">
      <Sidebar
        currentCourse={
          currentCourse
            ? { id: currentCourse.id, title: currentCourse.title }
            : null
        }
        activeTab={activeTab}
        onTabChange={handleTabChange}
        onBackToDashboard={handleBackToDashboard}
        isOpen={sidebarOpen}
        onToggle={toggleSidebar}
      />

      <main
        className={`flex-grow min-h-screen overflow-hidden transition-all duration-300 ${sidebarOpen ? "ml-64" : "ml-0"}`}
      >
        {activeTab === "chat" && (
          <ChatInterface 
            courseId={courseId || ""} 
            sessionId={selectedSessionId} 
          />
        )}
        {activeTab === "history" && (
          <ChatHistory
            courseId={courseId || ""}
            onSelectSession={handleSelectChatSession}
            isActive={activeTab === "history"}
          />
        )}
        {activeTab === "videos" && (
          <VideoTab
            courseId={courseId || ""}
          />
        )}
        {activeTab === "content" && (
          <ContentTab
            courseId={courseId || ""}
            content={currentCourse?.content || []}
          />
        )}
        {activeTab === "avatars" && (
          <AvatarTab 
            courseId={courseId || ""}
          />
        )}
      </main>
    </div>
  );
} 