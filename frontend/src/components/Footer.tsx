export default function Footer() {
  return (
    <footer className="border-t border-adaptive py-6 px-6">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center">
        <div className="text-sm text-gray-400 mb-4 md:mb-0">
          © {new Date().getFullYear()} animind • All rights reserved
        </div>

        <div className="flex gap-6">
          <a href="#" className="text-sm text-gray-400 hover:text-gray-600">
            Help
          </a>
          <a href="#" className="text-sm text-gray-400 hover:text-gray-600">
            Privacy
          </a>
          <a href="#" className="text-sm text-gray-400 hover:text-gray-600">
            Terms
          </a>
        </div>
      </div>
    </footer>
  );
}
