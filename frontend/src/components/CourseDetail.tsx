import { useState, useEffect } from "react";
import { BookIcon, VideoIcon } from "./Icons";
import ChatInterface from "./ChatInterface";
import ChatHistory from "./ChatHistory";
import VideoTab from "./VideoTab";
import ContentTab from "./ContentTab";
import type { Database } from "../types/supabase";

interface CourseDetailProps {
  courseId: string;
  onBack: () => void;
}

// Use the Video type from VideoTab
type Video = Database['public']['Tables']['videos']['Row'] & {
  thumbnailUrl?: string;
  videoUrl?: string;
  createdAt?: string;
};

interface Course {
  id: string;
  title: string;
  description: string;
  category: string;
  lastUpdated: string;
  content?: string[];
  videos?: Video[];
}

type TabType = "chat" | "videos" | "content" | "history";

export default function CourseDetail({ courseId, onBack }: CourseDetailProps) {
  const [course, setCourse] = useState<Course | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>("chat");
  const [isLoading, setIsLoading] = useState(true);
  const [chatSessionId, setChatSessionId] = useState<string | null>(null);

  useEffect(() => {
    // Fetch course data from localStorage
    const savedCourses = localStorage.getItem("courses");
    if (savedCourses) {
      const allCourses = JSON.parse(savedCourses);
      const foundCourse = allCourses.find((c: Course) => c.id === courseId);
      if (foundCourse) {
        // Initialize videos and content arrays if they don't exist
        foundCourse.videos = foundCourse.videos || [];
        foundCourse.content = foundCourse.content || [];
        setCourse(foundCourse);
      }
    }
    setIsLoading(false);
  }, [courseId]);

  const handleSelectChatSession = (sessionId: string) => {
    setChatSessionId(sessionId);
    setActiveTab("chat");
    // Log the selected session ID
    console.log(`Loading chat session: ${chatSessionId}`);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">Loading...</div>
    );
  }

  if (!course) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-6">
          <button
            onClick={onBack}
            className="text-gray-500 hover:text-gray-700 flex items-center gap-2"
          >
            ← Back to courses
          </button>
        </div>
        <div className="text-center py-16">
          <h2 className="text-xl font-medium mb-2">Course not found</h2>
          <p className="text-gray-500 mb-4">
            The course you're looking for doesn't exist or has been removed.
          </p>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-gray-100 rounded hover:bg-gray-200"
          >
            Return to dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-6">
        <button
          onClick={onBack}
          className="text-gray-500 hover:text-gray-700 flex items-center gap-2"
        >
          ← Back to courses
        </button>
      </div>

      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-adaptive mb-2">
          {course.title}
        </h1>
        <p className="text-gray-500">{course.description}</p>
        <div className="mt-2 flex items-center text-xs text-gray-400">
          <span className="mr-3">Category: {course.category}</span>
          <span>Updated: {course.lastUpdated}</span>
        </div>
      </div>

      <div className="border-b border-adaptive mb-6">
        <div className="flex overflow-x-auto">
          <TabButton
            active={activeTab === "chat"}
            onClick={() => setActiveTab("chat")}
            label="Chat"
          />
          <TabButton
            active={activeTab === "history"}
            onClick={() => setActiveTab("history")}
            label="Chat History"
          />
          <TabButton
            active={activeTab === "videos"}
            onClick={() => setActiveTab("videos")}
            label="Videos"
            icon={<VideoIcon size={16} />}
          />
          <TabButton
            active={activeTab === "content"}
            onClick={() => setActiveTab("content")}
            label="Content"
            icon={<BookIcon size={16} />}
          />
        </div>
      </div>

      <div className="min-h-[60vh]">
        {activeTab === "chat" && <ChatInterface courseId={courseId} />}
        {activeTab === "history" && (
          <ChatHistory
            courseId={courseId}
            onSelectSession={handleSelectChatSession}
          />
        )}
        {activeTab === "videos" && (
          <VideoTab courseId={courseId} videos={course.videos || []} />
        )}
        {activeTab === "content" && (
          <ContentTab courseId={courseId} content={course.content || []} />
        )}
      </div>
    </div>
  );
}

interface TabButtonProps {
  active: boolean;
  onClick: () => void;
  label: string;
  icon?: React.ReactNode;
}

function TabButton({ active, onClick, label, icon }: TabButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`px-6 py-3 flex items-center gap-2 text-sm font-medium transition-colors border-b-2 whitespace-nowrap ${
        active
          ? "border-gray-800 text-gray-800"
          : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
      }`}
    >
      {icon}
      {label}
    </button>
  );
}
