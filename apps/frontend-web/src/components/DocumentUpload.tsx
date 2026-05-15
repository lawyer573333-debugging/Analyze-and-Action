"use client";

import { useState, useRef } from "react";
import { UploadCloud, File, Link as LinkIcon, Loader2 } from "lucide-react";
import { api } from "@/services/api";

export default function DocumentUpload({ onUploadComplete }: { onUploadComplete: (id: string) => void }) {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
    else if (e.type === "dragleave") setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const triggerUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("source_type", "pdf");

      const res = await api.post("/documents/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const docId = res.data.id;
      
      // Trigger analysis
      await api.post(`/insights/${docId}/analyze`);
      onUploadComplete(docId);
      setFile(null); // Reset
    } catch (err: any) {
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      {error && <p className="text-red-400 text-sm">{error}</p>}
      
      <div 
        className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all ${
          dragActive ? "border-primary bg-primary/5" : "border-border hover:border-primary/50 hover:bg-white/5"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input 
          ref={inputRef} 
          type="file" 
          accept="application/pdf" 
          onChange={handleChange} 
          className="hidden" 
        />
        
        {file ? (
          <div className="flex flex-col items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center text-primary">
              <File className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">{file.name}</p>
              <p className="text-xs text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <div className="flex gap-2 mt-2">
              <button onClick={() => setFile(null)} className="px-3 py-1.5 text-xs rounded-lg border border-border hover:bg-white/5">Cancel</button>
              <button 
                onClick={triggerUpload} 
                disabled={uploading}
                className="px-3 py-1.5 text-xs rounded-lg bg-primary text-white font-medium hover:bg-primary/90 flex items-center gap-2"
              >
                {uploading ? <Loader2 className="w-3 h-3 animate-spin" /> : null}
                {uploading ? "Uploading..." : "Analyze"}
              </button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center text-muted-foreground">
              <UploadCloud className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">Drag & drop a PDF</p>
              <p className="text-xs text-muted-foreground mt-1">or click to browse files</p>
            </div>
            <button 
              onClick={() => inputRef.current?.click()}
              className="mt-2 px-4 py-2 text-xs rounded-lg bg-white/10 hover:bg-white/20 transition-colors font-medium text-foreground"
            >
              Select File
            </button>
          </div>
        )}
      </div>
      
      <div className="flex items-center gap-4">
        <div className="h-px bg-border flex-1" />
        <span className="text-xs text-muted-foreground uppercase tracking-wider">OR</span>
        <div className="h-px bg-border flex-1" />
      </div>

      <div className="flex gap-2">
        <div className="relative flex-1">
          <LinkIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input 
            type="text" 
            placeholder="Paste a URL to analyze" 
            className="w-full bg-black/40 border border-border rounded-lg py-2 pl-9 pr-3 text-sm text-foreground focus:outline-none focus:border-primary/50 transition-colors"
          />
        </div>
        <button className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors text-sm font-medium">
          Analyze
        </button>
      </div>
    </div>
  );
}
