"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import ChatKitPanel from "@/components/ChatKitPanel";

export default function ChatPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    const paramId = searchParams.get("userId");
    const storedId = localStorage.getItem("meeting_scheduler_user_id");
    
    const finalId = paramId || storedId;

    if (!finalId) {
      router.push("/");
    } else {
      setUserId(finalId);
    }
  }, [searchParams, router]);

  if (!userId) return null;

  return (
    <div className="h-screen w-screen flex flex-col bg-gray-100 p-4 md:p-8">
      <header className="mb-4 flex justify-between items-center">
        <h1 className="text-xl font-semibold text-gray-800">
          Executive Scheduler <span className="text-gray-400 font-normal text-sm ml-2">Logged in as {userId}</span>
        </h1>
        <button 
          onClick={() => router.push("/")}
          className="text-sm text-gray-500 hover:text-gray-800"
        >
          Switch User
        </button>
      </header>
      
      <main className="flex-1 min-h-0">
        <ChatKitPanel userId={userId} />
      </main>
    </div>
  );
}