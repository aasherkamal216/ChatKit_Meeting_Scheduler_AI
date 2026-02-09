"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import ChatKitPanel from "@/components/ChatKitPanel";
import ThemeToggle from "@/components/ThemeToggle";

export default function ChatPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [userId, setUserId] = useState<string | null>(null);
  const [theme, setTheme] = useState<"light" | "dark">("light");

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

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  if (!userId) return null;

  return (
    <div
      className={`h-screen w-screen flex flex-col p-4 md:p-8 transition-colors duration-300 ${
        theme === "dark" ? "bg-zinc-950" : "bg-gray-100"
      }`}
    >
      <header className="mb-4 flex justify-between items-center">
        <div className="flex flex-col">
          <h1
            className={`text-xl font-semibold ${
              theme === "dark" ? "text-white" : "text-gray-800"
            }`}
          >
            Executive Scheduler
          </h1>
          <span className="text-gray-500 font-normal text-sm">
            Logged in as {userId}
          </span>
        </div>

        <div className="flex items-center gap-4">
          <ThemeToggle theme={theme} onToggle={toggleTheme} />
          <button
            onClick={() => router.push("/")}
            className="text-sm text-gray-500 hover:text-gray-800 dark:hover:text-gray-300"
          >
            Switch User
          </button>
        </div>
      </header>

      <main className="flex-1 min-h-0 bg-white rounded-xl overflow-hidden shadow-sm">
        <ChatKitPanel userId={userId} theme={theme} />
      </main>
    </div>
  );
}