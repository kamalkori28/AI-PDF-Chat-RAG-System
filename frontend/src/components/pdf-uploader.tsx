"use client";

import { ChangeEvent, DragEvent, useRef, useState } from "react";
import { UploadCloud } from "lucide-react";
import { toast } from "sonner";

import { useUploadDocuments } from "@/hooks/use-documents";
import { getErrorMessage } from "@/services/errors";

export function PdfUploader() {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const uploadDocuments = useUploadDocuments();

  async function upload(files: FileList | File[]) {
    const pdfs = Array.from(files).filter(
      (file) => file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf")
    );
    if (!pdfs.length) {
      toast.error("Select at least one PDF");
      return;
    }
    try {
      await uploadDocuments.mutateAsync(pdfs);
      toast.success("Upload queued");
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    } catch (error) {
      toast.error(getErrorMessage(error, "Upload failed"));
    }
  }

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragActive(false);
    upload(event.dataTransfer.files);
  }

  function onChange(event: ChangeEvent<HTMLInputElement>) {
    if (event.target.files) {
      upload(event.target.files);
    }
  }

  return (
    <section
      className={`panel border-dashed p-6 text-center ${
        dragActive ? "border-[var(--primary)] bg-[var(--surface-strong)]" : ""
      }`}
      onDragEnter={() => setDragActive(true)}
      onDragLeave={() => setDragActive(false)}
      onDragOver={(event) => event.preventDefault()}
      onDrop={onDrop}
    >
      <input
        accept="application/pdf"
        className="hidden"
        multiple
        onChange={onChange}
        ref={inputRef}
        type="file"
      />
      <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--surface-strong)]">
        <UploadCloud size={24} />
      </div>
      <h2 className="font-bold">PDF Upload</h2>
      <p className="muted mb-4 text-sm">Queued ingestion</p>
      <button
        className="btn btn-primary"
        disabled={uploadDocuments.isPending}
        onClick={() => inputRef.current?.click()}
        type="button"
      >
        <UploadCloud size={18} />
        {uploadDocuments.isPending ? "Uploading" : "Choose PDFs"}
      </button>
    </section>
  );
}
