"use client";

import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { CHATKIT_URL, CHATKIT_DOMAIN_KEY } from "../lib/config";

interface ChatKitPanelProps {
  userId: string;
  theme: "light" | "dark";
}

export default function ChatKitPanel({ userId, theme }: ChatKitPanelProps) {
  const { control } = useChatKit({
    // Pass the theme here so ChatKit adapts its internal colors (bg, text, etc)
    theme: {
      colorScheme: theme,
    },
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
    threadItemActions: {
      feedback: true,
      retry: true,
    },
    widgets: {
      // Optional: Client-side interceptor.
      // Since our widgets use handler: "server" (default), this is mostly for debugging.
      onAction: async (action, item) => {
        console.log("Client intercepted action:", action.type, action.payload);
      },
    
    },
  });

  return (
    // The container border/bg is handled by the parent or Tailwind classes
    <div className="h-full w-full">
      <ChatKit control={control} className="h-full w-full" />
    </div>
  );
}