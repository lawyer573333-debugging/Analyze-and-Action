"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

interface PipelineEvent {
  stage: "started" | "ingestion" | "insights" | "analysis" | "completed";
  message: string;
  results_count?: number;
}

const STAGES = ["started", "ingestion", "insights", "analysis", "completed"];

export default function PipelineProgress({ documentId }: { documentId: string }) {
  const [currentStage, setCurrentStage] = useState<string>("started");
  const [messages, setMessages] = useState<PipelineEvent[]>([]);

  useEffect(() => {
    // Determine WebSocket URL based on current origin
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    // Assume backend is on port 8000 for local dev
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || `ws://localhost:8000/ws/${documentId}`;
    
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      try {
        const data: PipelineEvent = JSON.parse(event.data);
        setCurrentStage(data.stage);
        setMessages((prev) => [...prev, data]);
      } catch (err) {
        console.error("Failed to parse websocket message", err);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    return () => {
      ws.close();
    };
  }, [documentId]);

  const currentIndex = STAGES.indexOf(currentStage);

  return (
    <div className="glass-card rounded-2xl p-6 relative overflow-hidden">
      {/* Background active glow */}
      {currentStage !== "completed" && (
        <div className="absolute top-0 right-0 w-32 h-32 bg-primary/20 rounded-full blur-[50px] animate-pulse" />
      )}

      <div className="space-y-6 relative z-10">
        {STAGES.map((stage, index) => {
          const isCompleted = index < currentIndex || currentStage === "completed";
          const isCurrent = index === currentIndex && currentStage !== "completed";
          const isPending = index > currentIndex;

          return (
            <div key={stage} className="flex gap-4">
              <div className="relative flex flex-col items-center">
                {isCompleted ? (
                  <CheckCircle2 className="w-6 h-6 text-green-500" />
                ) : isCurrent ? (
                  <Loader2 className="w-6 h-6 text-primary animate-spin" />
                ) : (
                  <Circle className="w-6 h-6 text-muted-foreground/30" />
                )}
                {index < STAGES.length - 1 && (
                  <div className={`w-0.5 h-full my-1 rounded-full ${isCompleted ? "bg-green-500" : "bg-border"}`} />
                )}
              </div>
              
              <div className={`pb-6 ${isPending ? "opacity-50" : "opacity-100"}`}>
                <p className="text-sm font-semibold text-foreground capitalize">
                  {stage === "started" ? "Initialization" : stage}
                </p>
                {isCurrent && (
                  <p className="text-xs text-muted-foreground mt-1 animate-pulse">
                    {messages[messages.length - 1]?.message || "Processing..."}
                  </p>
                )}
                {isCompleted && stage === "completed" && messages[messages.length - 1]?.results_count && (
                  <p className="text-xs text-green-400 mt-1">
                    Found {messages[messages.length - 1]?.results_count} actionable insights!
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
