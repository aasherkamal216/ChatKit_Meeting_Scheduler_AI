"use client";

import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { CHATKIT_URL, CHATKIT_DOMAIN_KEY } from "../lib/config";

interface ChatKitPanelProps {
  userId: string;
}

export default function ChatKitPanel({ userId }: ChatKitPanelProps) {
  const { control } = useChatKit({
    api: {
      url: CHATKIT_URL,
      domainKey: CHATKIT_DOMAIN_KEY,
      fetch: (url, init) => 
        fetch(url, {
          ...init,
          headers: {
            ...init?.headers,
            "X-User-ID": userId,
          },
        }),
    },
    startScreen: {
      greeting: "I am your Executive Scheduler. Who are we meeting today?",
      prompts: [
        { label: "Book a meeting", prompt: "I want to book a meeting.", icon: "calendar" },
        { label: "Check my schedule", prompt: "What does my day look like?", icon: "notebook" },
      ],
    },
  });

  return (
    // Ensure the container has height
    <div className="h-full w-full bg-white rounded-xl overflow-hidden shadow-sm">
      <ChatKit control={control} className="h-full w-full" />
    </div>
  );
}