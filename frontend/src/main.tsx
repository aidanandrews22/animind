import "./index.css";
import React from "react";
import ReactDOM from "react-dom/client";
import { ClerkProvider } from "@clerk/clerk-react";
import { SupabaseProvider } from "./contexts/SupabaseContext";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "./App";
import DashboardPage from "./pages/Dashboard";
import CoursePage from "./pages/Course";
import VideoPlayerPage from "./components/VideoPlayer";

// Import your Publishable Key
const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!PUBLISHABLE_KEY) {
  throw new Error("Missing Publishable Key");
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      {
        index: true,
        element: <DashboardPage />
      },
      {
        path: "course/:courseId",
        element: <CoursePage />
      },
      {
        path: "video/:videoId",
        element: <VideoPlayerPage />
      }
    ]
  }
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ClerkProvider publishableKey={PUBLISHABLE_KEY} afterSignOutUrl="/">
      <SupabaseProvider>
        <RouterProvider router={router} />
      </SupabaseProvider>
    </ClerkProvider>
  </React.StrictMode>,
);
