import { ButtonHTMLAttributes } from "react";

type ButtonProps = {
  variant?: "primary" | "secondary";
} & ButtonHTMLAttributes<HTMLButtonElement>;

export default function Button({
  children,
  variant = "primary",
  className = "",
  ...props
}: ButtonProps) {
  const baseClasses = "px-4 py-2 rounded font-medium transition-colors";

  const variantStyle = {
    backgroundColor:
      variant === "primary" ? "var(--color-primary)" : "transparent",
    color: variant === "primary" ? "white" : "var(--color-text)",
    border: variant === "secondary" ? "1px solid var(--color-border)" : "none",
  };

  return (
    <button
      className={`${baseClasses} ${className}`}
      style={variantStyle}
      {...props}
    >
      {children}
    </button>
  );
}
