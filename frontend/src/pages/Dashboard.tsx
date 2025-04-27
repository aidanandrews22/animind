import Dashboard from "../components/Dashboard";
import DashboardHeader from "../components/DashboardHeader";
import { UserButton } from "@clerk/clerk-react";
import { useNavigate } from "react-router-dom";

export default function DashboardPage() {
  const navigate = useNavigate();
  
  return (
    <>
      <DashboardHeader profileComponent={<UserButton />} />
      <main className="flex-grow min-h-screen overflow-hidden">
        <Dashboard onSelectCourse={(courseId) => {
          navigate(`/course/${courseId}`);
        }} />
      </main>
    </>
  );
} 