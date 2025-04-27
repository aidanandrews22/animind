import { ReactNode } from "react";
import IconButton from "./IconButton";

interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description: string;
  actionLabel?: string;
  actionIcon?: ReactNode;
  onAction?: () => void;
}

export default function EmptyState({
  icon,
  title,
  description,
  actionLabel,
  actionIcon,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-16 bg-surface border border-adaptive rounded-lg">
      <div className="flex justify-center text-gray-300 mx-auto mb-4">{icon}</div>
      <h3 className="text-xl font-medium text-adaptive mb-2 text-center">{title}</h3>
      <p className="text-adaptive opacity-60 mb-6 text-center max-w-md mx-auto">{description}</p>

      {actionLabel && onAction && (
        <div className="flex justify-center">
          <IconButton
            icon={actionIcon || null}
            label={actionLabel}
            variant="secondary"
            onClick={onAction}
          />
        </div>
      )}
    </div>
  );
}