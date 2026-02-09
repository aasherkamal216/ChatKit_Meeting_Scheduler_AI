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
    <div className="min-h-screen flex flex-col items-center justify-center bg-white dark:bg-black p-4 transition-colors">
      <div className="max-w-md w-full bg-white dark:bg-black p-8 text-center transition-colors">
        <h1 className="text-3xl font-bold mb-2 text-zinc-900 dark:text-zinc-100">Meeting Scheduler Agent</h1>
        <p className="text-zinc-600 dark:text-zinc-400 mb-8">Select a persona to login</p>
        
        <div className="space-y-4">
          <button
            onClick={() => handleLogin("alice")}
            className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition"
          >
            Login as Alice (Executive)
          </button>
          
          <button
            onClick={() => handleLogin("bob")}
            className="w-full py-3 px-4 bg-zinc-100 hover:bg-zinc-200 dark:bg-zinc-800 dark:hover:bg-zinc-700 text-zinc-900 dark:text-zinc-100 rounded-lg font-medium transition"
          >
            Login as Bob (Manager)
          </button>
        </div>
      </div>
    </div>
  );
}