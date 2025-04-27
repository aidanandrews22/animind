import { Outlet } from "react-router-dom";
import { SignedIn, SignedOut, SignIn } from "@clerk/clerk-react";

export default function App() {
  return (
    <>
      <SignedIn>
        <div className="min-h-screen flex flex-col bg-background text-adaptive">
          <Outlet />
        </div>
      </SignedIn>
      <SignedOut>
        <div className="min-h-screen flex flex-col bg-background justify-center items-center text-adaptive">
          <SignIn />
        </div>
      </SignedOut>
    </>
  );
} 