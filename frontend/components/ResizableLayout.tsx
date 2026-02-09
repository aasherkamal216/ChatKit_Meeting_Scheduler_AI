"use client";

import { useState, useCallback, useEffect, useRef } from "react";

interface ResizableLayoutProps {
  leftContent: React.ReactNode;
  rightContent: React.ReactNode;
}

export default function ResizableLayout({
  leftContent,
  rightContent,
}: ResizableLayoutProps) {
  const [rightWidth, setRightWidth] = useState(500); // Default nicer width
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const startResizing = useCallback(() => {
    setIsDragging(true);
  }, []);

  const stopResizing = useCallback(() => {
    setIsDragging(false);
  }, []);

  const resize = useCallback(
    (mouseMoveEvent: MouseEvent) => {
      if (isDragging && containerRef.current) {
        const containerRect = containerRef.current.getBoundingClientRect();
        const newWidth = containerRect.right - mouseMoveEvent.clientX;
        
        // Min 350px, Max 70% of screen
        if (newWidth > 350 && newWidth < containerRect.width * 0.7) {
          setRightWidth(newWidth);
        }
      }
    },
    [isDragging]
  );

  useEffect(() => {
    if (isDragging) {
      window.addEventListener("mousemove", resize);
      window.addEventListener("mouseup", stopResizing);
    }
    return () => {
      window.removeEventListener("mousemove", resize);
      window.removeEventListener("mouseup", stopResizing);
    };
  }, [isDragging, resize, stopResizing]);

  return (
    <div
      ref={containerRef}
      className="flex h-screen w-screen overflow-hidden bg-white dark:bg-black transition-colors"
    >
      {/* Left Panel (Content) */}
      <div className="flex-1 min-w-0 flex flex-col justify-center px-12 lg:px-24">
        {leftContent}
      </div>

      {/* Resizer Handle */}
      <div
        onMouseDown={startResizing}
        className={`w-[1px] cursor-col-resize hover:w-1 hover:bg-blue-500 transition-all z-20 flex flex-col justify-center items-center group relative
          ${isDragging ? "w-1 bg-blue-600" : "bg-zinc-200 dark:bg-zinc-700"}`}
      >
         {/* Invisible grab area for easier clicking */}
         <div className="absolute inset-y-0 -left-2 -right-2 bg-transparent z-10 cursor-col-resize"></div>
      </div>

      {/* Right Panel (Widget) */}
      <div
        style={{ width: rightWidth }}
        className="h-full relative shadow-xl z-10 bg-white dark:bg-zinc-900 transition-colors"
      >
        {isDragging && (
          <div className="absolute inset-0 z-50 bg-transparent cursor-col-resize" />
        )}
        {rightContent}
      </div>
    </div>
  );
}