import { SearchIcon, BookIcon, VideoIcon } from "./Icons";

interface HeaderProps {
  currentCourse?: {
    id: string;
    title: string;
  } | null;
  activeTab?: string;
  onTabChange?: (tab: string) => void;
  onBackToDashboard?: () => void;
}

export default function Header({
  currentCourse,
  activeTab,
  onTabChange,
  onBackToDashboard,
}: HeaderProps) {
  return (
    <header className="w-full border-b border-adaptive py-4 px-6">
      <div className="flex items-center justify-between">
        {!currentCourse ? (
          // Dashboard header
          <div className="flex items-center">
            <h1 className="text-xl font-semibold text-adaptive">animind</h1>
          </div>
        ) : (
          // Course header with tabs
          <div className="w-full">
            <div className="flex items-center mb-4">
              <button
                onClick={onBackToDashboard}
                className="text-gray-500 hover:text-gray-700 flex items-center gap-2 mr-4"
              >
                ← Back
              </button>
              <h1 className="text-lg font-semibold text-adaptive truncate">
                {currentCourse.title}
              </h1>
            </div>

            <div className="flex overflow-x-auto">
              <TabButton
                active={activeTab === "chat"}
                onClick={() => onTabChange?.("chat")}
                label="Chat"
              />
              <TabButton
                active={activeTab === "history"}
                onClick={() => onTabChange?.("history")}
                label="Chat History"
              />
              <TabButton
                active={activeTab === "videos"}
                onClick={() => onTabChange?.("videos")}
                label="Videos"
                icon={<VideoIcon size={16} />}
              />
              <TabButton
                active={activeTab === "content"}
                onClick={() => onTabChange?.("content")}
                label="Content"
                icon={<BookIcon size={16} />}
              />
            </div>
          </div>
        )}

        <div className="flex items-center gap-4">
          {!currentCourse && (
            <div className="relative hidden md:block">
              <SearchIcon
                className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                size={16}
              />
              <input
                type="text"
                placeholder="Search..."
                className="bg-gray-100 rounded-md py-2 pl-10 pr-4 text-sm focus:outline-none focus:ring-1 focus:ring-gray-300 w-64"
              />
            </div>
          )}

          <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center text-sm font-medium cursor-pointer">
            A
          </div>
        </div>
      </div>
    </header>
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
