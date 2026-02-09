"use client";

import { usePathname, useRouter } from "next/navigation";

export default function ChatPageSwitchUser() {
  const pathname = usePathname();
  const router = useRouter();

  if (pathname !== "/chat") return null;

  return (
    <button
      onClick={() => router.push("/")}
      className="px-4 py-2 text-sm font-medium text-zinc-600 dark:text-zinc-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-full transition-all"
    >
      Switch User
    </button>
  );
}
