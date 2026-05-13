"use client";

import { FileText } from "lucide-react";

import type { Citation } from "@/types";

export function SourceList({
  citations,
  compact = false
}: {
  citations: Citation[];
  compact?: boolean;
}) {
  return (
    <div className={compact ? "mt-3 space-y-2" : "space-y-2"}>
      {citations.map((citation) => (
        <div className="soft-panel p-3" key={`${citation.chunk_id}-${citation.label}`}>
          <div className="mb-1 flex items-center gap-2">
            <FileText size={15} />
            <span className="text-xs font-bold">{citation.label}</span>
            <span className="muted text-xs">Page {citation.page}</span>
          </div>
          <p className="truncate text-xs font-semibold">{citation.filename}</p>
          {!compact ? <p className="muted mt-1 text-xs">{citation.preview}</p> : null}
        </div>
      ))}
    </div>
  );
}

