import { ButtonHTMLAttributes, ReactNode } from "react";

interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  icon: ReactNode;
  label?: string;
  variant?: "primary" | "secondary" | "ghost";
}

export default function IconButton({
  icon,
  label,
  variant = "ghost",
  className = "",
  ...props
}: IconButtonProps) {
  const baseClasses =
    "flex items-center gap-2 px-3 py-2 rounded-md transition-all text-sm font-medium";

  const variantClasses = {
    primary: "bg-gray-800 text-white hover:bg-gray-700",
    secondary: "border border-gray-200 hover:bg-gray-50",
    ghost: "text-gray-600 hover:bg-gray-100",
  };

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      {...props}
    >
      <span className="text-[1.1em]">{icon}</span>
      {label && <span>{label}</span>}
    </button>
  );
}
