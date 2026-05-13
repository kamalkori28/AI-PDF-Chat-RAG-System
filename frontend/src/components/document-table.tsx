"use client";

import { FileText, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { useDeleteDocument, useDocuments } from "@/hooks/use-documents";
import { getErrorMessage } from "@/services/errors";

export function DocumentTable() {
  const { data, isLoading } = useDocuments();
  const deleteDocument = useDeleteDocument();

  async function onDelete(documentId: string) {
    try {
      await deleteDocument.mutateAsync(documentId);
      toast.success("Document deleted");
    } catch (error) {
      toast.error(getErrorMessage(error, "Delete failed"));
    }
  }

  return (
    <section className="panel overflow-hidden">
      <div className="border-b border-[var(--border)] p-4">
        <h2 className="font-bold">Documents</h2>
      </div>
      <div className="divide-y divide-[var(--border)]">
        {isLoading
          ? Array.from({ length: 3 }).map((_, index) => (
              <div className="flex items-center gap-3 p-4" key={index}>
                <div className="h-10 w-10 rounded-lg skeleton" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-2/3 rounded skeleton" />
                  <div className="h-3 w-1/3 rounded skeleton" />
                </div>
              </div>
            ))
          : null}

        {(data ?? []).map((document) => (
          <div className="flex items-center justify-between gap-3 p-4" key={document.id}>
            <div className="flex min-w-0 items-center gap-3">
              <div className="icon-btn shrink-0" aria-hidden>
                <FileText size={18} />
              </div>
              <div className="min-w-0">
                <p className="truncate font-semibold">{document.filename}</p>
                <p className="muted text-xs">
                  {document.status} - {formatBytes(document.file_size)} - {document.chunk_count} chunks
                </p>
                {document.error_message ? (
                  <p className="text-xs text-[var(--danger)]">{document.error_message}</p>
                ) : null}
              </div>
            </div>
            <button
              className="icon-btn"
              onClick={() => onDelete(document.id)}
              title="Delete document"
              type="button"
            >
              <Trash2 size={17} />
            </button>
          </div>
        ))}

        {!isLoading && !data?.length ? <p className="muted p-4 text-sm">No documents</p> : null}
      </div>
    </section>
  );
}

function formatBytes(bytes: number) {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}
