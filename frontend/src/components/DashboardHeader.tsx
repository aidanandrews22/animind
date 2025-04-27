import { SearchIcon } from "./Icons";

interface DashboardHeaderProps {
  profileComponent: React.ReactNode;
}

export default function DashboardHeader({
  profileComponent,
}: DashboardHeaderProps) {
  return (
    <header className="sticky top-0 z-10 bg-white border-b border-adaptive py-4 px-6 shadow-sm">
      <div className="flex items-center justify-between max-w-6xl mx-auto">
        <div className="flex items-center">
          <h1 className="text-2xl font-semibold text-adaptive">animind</h1>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative">
            <SearchIcon
              className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
              size={16}
            />
            <input
              type="text"
              placeholder="Search..."
              className="bg-gray-50 border border-gray-200 rounded-md py-2 pl-10 pr-4 text-sm focus:outline-none focus:ring-1 focus:ring-gray-300 w-64"
            />
          </div>

          {profileComponent}
        </div>
      </div>
    </header>
  );
}
