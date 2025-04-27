import { BookIcon, VideoIcon, AvatarIcon } from "./Icons";
import SidebarToggle from "./SidebarToggle";

interface SidebarProps {
  currentCourse?: {
    id: string;
    title: string;
  } | null;
  activeTab?: string;
  onTabChange?: (tab: string) => void;
  onBackToDashboard?: () => void;
  isOpen: boolean;
  onToggle: () => void;
}

export default function Sidebar({
  currentCourse,
  activeTab,
  onTabChange,
  onBackToDashboard,
  isOpen,
  onToggle,
}: SidebarProps) {
  return (
    <>
      {/* Toggle button container - always visible and positioned consistently */}
      <div className="fixed top-3 left-3 z-30">
        <SidebarToggle isOpen={isOpen} onToggle={onToggle} />
      </div>

      {/* Sidebar content */}
      <div
        className={`fixed inset-y-0 left-0 z-20 max-h-screen transition-all duration-300 ${isOpen ? "w-64" : "w-0"}`}
      >
        <div className="flex flex-col bg-white border-r border-adaptive h-full w-full">
          <div
            className={`flex-1 overflow-y-auto pt-16 px-4 ${isOpen ? "opacity-100" : "opacity-0"} transition-opacity duration-300`}
          >
            <div className="mb-6">
              <h1 className="text-xl font-semibold text-adaptive">
                {!currentCourse ? "animind" : currentCourse.title}
                <div className="border-t border-gray-200 dark:border-gray-700 my-4"></div>
              </h1>
            </div>

            {currentCourse && (
              <nav className="">
                <ul className="space-y-2">
                  <NavItem
                    label="Chat"
                    isActive={activeTab === "chat"}
                    onClick={() => onTabChange?.("chat")}
                  />
                  <NavItem
                    label="Chat History"
                    isActive={activeTab === "history"}
                    onClick={() => onTabChange?.("history")}
                  />
                  <NavItem
                    label="Videos"
                    isActive={activeTab === "videos"}
                    onClick={() => onTabChange?.("videos")}
                    icon={<VideoIcon size={16} />}
                  />
                  <NavItem
                    label="Content"
                    isActive={activeTab === "content"}
                    onClick={() => onTabChange?.("content")}
                    icon={<BookIcon size={16} />}
                  />
                  <NavItem
                    label="Avatars"
                    isActive={activeTab === "avatars"}
                    onClick={() => onTabChange?.("avatars")}
                    icon={<AvatarIcon size={16} />}
                  />
                </ul>
              </nav>
            )}
          </div>

          {/* Back to dashboard button at bottom */}
          {currentCourse && isOpen && (
            <div className="p-4">
              <div className="border-t border-gray-200 dark:border-gray-700 my-2"></div>
              <button
                onClick={onBackToDashboard}
                className="flex items-center text-gray-500 hover:text-gray-700 w-full py-2"
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M19 12H5M5 12L12 19M5 12L12 5" />
                </svg>
                <span className="ml-2">Back to dashboard</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Overlay when sidebar is open on mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 bg-opacity-50 md:hidden max-h-screen z-10"
          onClick={onToggle}
        ></div>
      )}
    </>
  );
}

interface NavItemProps {
  label: string;
  isActive: boolean;
  onClick: () => void;
  icon?: React.ReactNode;
}

function NavItem({ label, isActive, onClick, icon }: NavItemProps) {
  return (
    <li>
      <button
        onClick={onClick}
        className={`flex items-center w-full px-3 py-2 text-left rounded-md transition-colors ${
          isActive
            ? "bg-gray-100 text-gray-800"
            : "text-gray-600 hover:bg-gray-50 hover:text-gray-800"
        }`}
      >
        {icon && <span className="mr-2">{icon}</span>}
        <span>{label}</span>
      </button>
    </li>
  );
}
