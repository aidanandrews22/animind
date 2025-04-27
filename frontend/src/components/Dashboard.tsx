import { useState, useEffect } from "react";
import { PlusIcon, EditIcon } from "./Icons";
import IconButton from "./IconButton";
import { useSupabase } from "../hooks/useSupabase";
import { getCoursesByUserId, createCourse, updateCourse } from "../services/courseService";
import type { Database } from "../types/supabase";
import CourseModal from "./CourseModal";

type Course = Database['public']['Tables']['courses']['Row'] & {
  lastAccessed?: string;
  progress?: number;
};

interface DashboardProps {
  onSelectCourse: (courseId: string) => void;
}

export default function Dashboard({
  onSelectCourse,
}: DashboardProps) {
  const { userId, isLoading: isUserLoading } = useSupabase();
  const [courses, setCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<'create' | 'edit'>('create');
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);

  // Fetch courses when userId is available
  useEffect(() => {
    async function loadCourses() {
      if (!userId) return;
      
      setIsLoading(true);
      const coursesData = await getCoursesByUserId(userId);
      
      // Add UI-specific properties to course objects
      const formattedCourses = coursesData.map(course => ({
        ...course,
        lastAccessed: formatDate(course.updated_at),
        progress: Math.floor(Math.random() * 100), // Placeholder for actual progress
      }));
      
      setCourses(formattedCourses);
      setIsLoading(false);
    }
    
    if (!isUserLoading) {
      loadCourses();
    }
  }, [userId, isUserLoading]);

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

  const filteredCourses = courses.filter(
    (course) =>
      course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (course.description && course.description.toLowerCase().includes(searchQuery.toLowerCase())),
  );

  const handleCreateCourse = () => {
    setModalMode('create');
    setSelectedCourse(null);
    setIsModalOpen(true);
  };

  const handleEditCourse = (course: Course, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering the course selection
    setModalMode('edit');
    setSelectedCourse(course);
    setIsModalOpen(true);
  };

  const handleSaveCourse = async (courseData: {
    title: string;
    description: string;
    category: string;
  }) => {
    if (!userId) return;
    
    if (modalMode === 'create') {
      // Create new course
      const newCourseData = {
        user_id: userId,
        title: courseData.title,
        description: courseData.description,
        category: courseData.category,
      };

      const newCourse = await createCourse(newCourseData);
      
      if (newCourse) {
        // Add UI properties
        const formattedCourse = {
          ...newCourse,
          lastAccessed: 'Just now',
          progress: 0,
        };
        
        setCourses([formattedCourse, ...courses]);
      }
    } else if (modalMode === 'edit' && selectedCourse) {
      // Update existing course
      const updatedCourse = await updateCourse(selectedCourse.id, {
        title: courseData.title,
        description: courseData.description,
        category: courseData.category,
      });
      
      if (updatedCourse) {
        // Update the course in the state
        setCourses(courses.map(course => 
          course.id === updatedCourse.id ? {
            ...updatedCourse,
            lastAccessed: 'Just now',
            progress: course.progress,
          } : course
        ));
      }
    }
  };

  // Show loading state
  if (isLoading || isUserLoading) {
    return (
      <div className="h-full w-full overflow-y-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Your Courses
            </h1>
            <p className="text-gray-600">Loading courses...</p>
          </div>
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full overflow-y-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Your Courses
          </h1>
          <p className="text-gray-600">
            Select a course to continue learning or create a new one
          </p>
        </div>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div className="relative flex-grow max-w-md">
            <input
              type="text"
              placeholder="Search courses..."
              className="w-full pl-3 pr-10 py-2 border border-gray-200 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-gray-300"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
            </div>
          </div>

          <IconButton
            icon={<PlusIcon />}
            label="Create Course"
            variant="primary"
            onClick={handleCreateCourse}
          />
        </div>

        {filteredCourses.length === 0 ? (
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              No courses found
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchQuery
                ? "Try a different search term"
                : "Get started by creating a new course"}
            </p>
            <div className="mt-6">
              <button
                type="button"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                onClick={handleCreateCourse}
              >
                <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
                Create Course
              </button>
            </div>
          </div>
        ) :
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCourses.map((course) => (
              <div
                key={course.id}
                className="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow cursor-pointer relative"
              >
                <div 
                  className="absolute top-2 right-2 z-10"
                  onClick={(e) => handleEditCourse(course, e)}
                >
                  <IconButton
                    icon={<EditIcon size={16} />}
                    variant="secondary"
                    className="!p-2"
                    aria-label="Edit course"
                  />
                </div>
                <div 
                  className="h-36 bg-gradient-to-r from-indigo-500 to-purple-600 flex items-center justify-center"
                  onClick={() => onSelectCourse(course.id)}
                >
                  <span className="text-white text-lg font-medium">
                    {course.title
                      .split(" ")
                      .map((word) => word[0])
                      .join("")}
                  </span>
                </div>
                <div 
                  className="p-4"
                  onClick={() => onSelectCourse(course.id)}
                >
                  <h3 className="font-medium text-gray-900 mb-1">
                    {course.title}
                  </h3>
                  <p className="text-sm text-gray-500 mb-4 line-clamp-2">
                    {course.description || "No description available"}
                  </p>

                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>Last updated: {course.lastAccessed}</span>
                    <span>{course.progress}% complete</span>
                  </div>

                  <div className="mt-2 w-full bg-gray-200 rounded-full h-1.5">
                    <div
                      className="bg-indigo-600 h-1.5 rounded-full"
                      style={{ width: `${course.progress}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        }
      </div>
      
      <CourseModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveCourse}
        course={selectedCourse ? {
          id: selectedCourse.id,
          title: selectedCourse.title,
          description: selectedCourse.description || undefined,
          category: selectedCourse.category || undefined
        } : undefined}
        mode={modalMode}
      />
    </div>
  );
}
