import { ReactNode } from "react";

interface CourseCardProps {
  title: string;
  description: string;
  category?: string;
  lastUpdated?: string;
  onClick?: () => void;
  icon?: ReactNode;
}

export default function CourseCard({
  title,
  description,
  category,
  lastUpdated,
  onClick,
  icon,
}: CourseCardProps) {
  return (
    <div
      onClick={onClick}
      className="bg-surface border border-adaptive rounded-lg p-6 hover:shadow-md transition-all cursor-pointer"
    >
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-medium text-adaptive">{title}</h3>
        {icon && <div className="text-gray-400">{icon}</div>}
      </div>

      <p className="text-sm text-adaptive opacity-75 mb-4 line-clamp-2">
        {description}
      </p>

      <div className="flex justify-between items-center text-xs text-adaptive opacity-60">
        {category && <span>{category}</span>}
        {lastUpdated && <span>Updated {lastUpdated}</span>}
      </div>
    </div>
  );
}
