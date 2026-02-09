"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import ChatKitPanel from "@/components/ChatKitPanel";
import { useTheme } from "@/components/ThemeProvider";
import ResizableLayout from "@/components/ResizableLayout";

export default function ChatPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [userId, setUserId] = useState<string | null>(null);
  const { theme } = useTheme();

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

  // --- Left Content: Branding ---
  const LeftPanel = (
    <div className="h-full flex flex-col p-8 md:p-12 max-w-2xl mx-auto w-full justify-between">
      {/* Centered Title & Description */}
      <div className="flex-1 flex flex-col items-center justify-center text-center space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight leading-tight text-black dark:text-white">
          Meeting Scheduler AI
        </h1>
        <p className="text-lg text-zinc-500 dark:text-zinc-400">
          A meeting scheduling simulation agent utilizing ChatKit’s interactive widgets to manage complex booking flows.
        </p>
      </div>

      {/* Empty bottom to keep centering */}
      <div />
    </div>
  );

  // --- Right Content: ChatKit ---
  const RightPanel = (
    <div className="h-full w-full bg-white dark:bg-black">
      <ChatKitPanel userId={userId} theme={theme} />
    </div>
  );

  return <ResizableLayout leftContent={LeftPanel} rightContent={RightPanel} />;
}