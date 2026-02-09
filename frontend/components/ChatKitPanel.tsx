"use client";

import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { CHATKIT_URL, CHATKIT_DOMAIN_KEY } from "../lib/config";

interface ChatKitPanelProps {
  userId: string;
  theme: "light" | "dark";
}

export default function ChatKitPanel({ userId, theme }: ChatKitPanelProps) {
  const { control } = useChatKit({
    theme: {
      colorScheme: theme,
      color: {
        accent: {
          primary: "#2563eb", // Blue-600
          level: 1, // Determines contrast level
        },
      },
      typography: {
        baseSize: 16,
        fontFamily: '"OpenAI Sans", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif',
        fontFamilyMono: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "DejaVu Sans Mono", "Courier New", monospace',
        fontSources: [
          {
            family: 'OpenAI Sans',
            src: 'https://cdn.openai.com/common/fonts/openai-sans/v2/OpenAISans-Regular.woff2',
            weight: 400,
            style: 'normal',
            display: 'swap'
          }
        ]
      },
      radius: "pill",
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
      greeting: "Good day. I am your Executive Scheduler. How can I assist you?",
      // 3-4 Good Starter Prompts
      prompts: [
        { 
          label: "Book a meeting", 
          prompt: "I need to book a meeting with the design team.", 
          icon: "calendar" 
        },
        { 
          label: "My Schedule", 
          prompt: "What does my calendar look like today?", 
          icon: "clock" 
        },
        { 
          label: "Quick Sync", 
          prompt: "Book a quick 15 min sync with Bob tomorrow morning.", 
          icon: "bolt" 
        }
      ],
    },
    threadItemActions: {
      feedback: true,
      retry: true,
    },
  });

  return (
    // Ensure container takes full height/width of the resizable parent
    <div className="h-full w-full flex flex-col">
      <ChatKit control={control} className="flex-1 h-full w-full border-none" />
    </div>
  );
}