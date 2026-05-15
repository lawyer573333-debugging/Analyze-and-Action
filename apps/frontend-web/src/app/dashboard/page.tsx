"use client";

import { useState } from "react";
import DocumentUpload from "@/components/DocumentUpload";
import PipelineProgress from "@/components/PipelineProgress";

export default function DashboardPage() {
  const [activeDocumentId, setActiveDocumentId] = useState<string | null>(null);

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-gradient">Workspace</h1>
        <p className="text-muted-foreground mt-1">Upload documents to extract actionable business insights.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          {/* Upload Area */}
          <section className="glass-card rounded-2xl p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-primary animate-glow" />
              New Analysis
            </h2>
            <DocumentUpload onUploadComplete={(docId) => setActiveDocumentId(docId)} />
          </section>

          {/* Results Area Placeholder */}
          <section className="glass-card rounded-2xl p-6 min-h-[300px] flex items-center justify-center border-dashed">
            <p className="text-muted-foreground text-sm text-center">
              Insights and recommended actions will appear here once analysis is complete.
            </p>
          </section>
        </div>

        <div className="lg:col-span-1">
          {/* Pipeline Progress */}
          <div className="sticky top-8">
            <h2 className="text-lg font-semibold text-foreground mb-4">Pipeline Status</h2>
            {activeDocumentId ? (
              <PipelineProgress documentId={activeDocumentId} />
            ) : (
              <div className="glass-card rounded-2xl p-6 text-center border border-border/50">
                <p className="text-muted-foreground text-sm">No active pipeline.</p>
                <p className="text-xs text-muted-foreground/60 mt-2">Upload a document to start.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
