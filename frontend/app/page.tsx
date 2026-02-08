"use client";

import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();

  const handleLogin = (userId: string) => {
    // In a real app, this would be authentication. 
    // Here we just pass the ID to the chat page.
    localStorage.setItem("meeting_scheduler_user_id", userId);
    router.push(`/chat?userId=${userId}`);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-white p-4">
      <div className="max-w-md w-full bg-white p-8 text-center">
        <h1 className="text-3xl font-bold mb-2 text-gray-800">Meeting Scheduler Agent</h1>
        <p className="text-gray-500 mb-8">Select a persona to login</p>
        
        <div className="space-y-4">
          <button
            onClick={() => handleLogin("alice")}
            className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition"
          >
            Login as Alice (Executive)
          </button>
          
          <button
            onClick={() => handleLogin("bob")}
            className="w-full py-3 px-4 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-lg font-medium transition"
          >
            Login as Bob (Manager)
          </button>
        </div>
      </div>
    </div>
  );
}