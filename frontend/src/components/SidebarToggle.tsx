interface SidebarToggleProps {
  isOpen: boolean;
  onToggle: () => void;
}

const SidebarToggle = ({ isOpen, onToggle }: SidebarToggleProps) => {
  return (
    <button
      onClick={onToggle}
      className="relative p-2 group rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-300"
      aria-label={isOpen ? "Close sidebar" : "Open sidebar"}
    >
      <div className="relative *:duration-300">
        {/* Default SVG - shown when not toggled and not hovered */}
        <svg
          width="18"
          height="18"
          viewBox="0 0 20 20"
          fill="currentColor"
          xmlns="http://www.w3.org/2000/svg"
          className={`shrink-0 transition-all text-gray-600
            ${isOpen ? "opacity-0 scale-80" : "group-hover:opacity-0 group-hover:scale-80 opacity-100 scale-100"}`}
        >
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M2.5 3C1.67157 3 1 3.67157 1 4.5V15.5C1 16.3284 1.67157 17 2.5 17H17.5C18.3284 17 19 16.3284 19 15.5V4.5C19 3.67157 18.3284 3 17.5 3H2.5ZM2 4.5C2 4.22386 2.22386 4 2.5 4H6V16H2.5C2.22386 16 2 15.7761 2 15.5V4.5ZM7 16H17.5C17.7761 16 18 15.7761 18 15.5V4.5C18 4.22386 17.7761 4 17.5 4H7V16Z"
          />
        </svg>

        {/* Toggled SVG - shown when the sidebar is toggled */}
        <svg
          width="18"
          height="18"
          viewBox="0 0 20 20"
          fill="currentColor"
          xmlns="http://www.w3.org/2000/svg"
          className={`shrink-0 absolute inset-0 transition-all text-gray-600
            ${isOpen ? "opacity-100 scale-100" : "opacity-0 scale-50"}`}
        >
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M5 10C5 9.85913 5.05943 9.72479 5.16366 9.63003L10.6637 4.63003C10.868 4.44428 11.1842 4.45933 11.37 4.66366C11.5557 4.86799 11.5407 5.18422 11.3363 5.36997L6.7933 9.5L17.5 9.5C17.7761 9.5 18 9.72386 18 10C18 10.2761 17.7761 10.5 17.5 10.5L6.7933 10.5L11.3363 14.63C11.5407 14.8158 11.5557 15.132 11.37 15.3363C11.1842 15.5407 10.868 15.5557 10.6637 15.37L5.16366 10.37C5.05943 10.2752 5 10.1409 5 10Z"
          />
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M2.5 2C2.77614 2 3 2.22386 3 2.5L3 17.5C3 17.7761 2.77614 18 2.5 18C2.22385 18 2 17.7761 2 17.5L2 2.5C2 2.22386 2.22386 2 2.5 2Z"
          />
        </svg>

        {/* Hover SVG - shown on hover when not toggled */}
        <svg
          width="18"
          height="18"
          viewBox="0 0 20 20"
          fill="currentColor"
          xmlns="http://www.w3.org/2000/svg"
          className={`shrink-0 absolute inset-0 transition-all text-gray-600
            ${isOpen ? "opacity-0 scale-50" : "group-hover:opacity-100 group-hover:scale-100 opacity-0 scale-50"}`}
        >
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M17.5 2C17.7761 2 18 2.22386 18 2.5V17.5C18 17.7761 17.7761 18 17.5 18C17.2239 18 17 17.7761 17 17.5V2.5C17 2.22386 17.2239 2 17.5 2ZM8.63003 4.66366C8.81578 4.45933 9.13201 4.44428 9.33634 4.63003L14.8363 9.63003C14.9406 9.72479 15 9.85913 15 10C15 10.1409 14.9406 10.2752 14.8363 10.37L9.33634 15.37C9.13201 15.5557 8.81578 15.5407 8.63003 15.3363C8.44428 15.132 8.45934 14.8158 8.66366 14.63L13.2067 10.5L2.5 10.5C2.22386 10.5 2 10.2761 2 10C2 9.72386 2.22386 9.5 2.5 9.5L13.2067 9.5L8.66366 5.36997C8.45934 5.18422 8.44428 4.86799 8.63003 4.66366Z"
          />
        </svg>
      </div>
    </button>
  );
};

export default SidebarToggle;
