"use client";

import { AppShell } from "@/components/app-shell";
import { AuthGuard } from "@/components/auth-guard";
import { DocumentTable } from "@/components/document-table";
import { PdfUploader } from "@/components/pdf-uploader";

export default function UploadPage() {
  return (
    <AuthGuard>
      <AppShell>
        <div className="grid gap-5">
          <header>
            <h1 className="text-2xl font-bold">Upload</h1>
            <p className="muted text-sm">PDF ingestion</p>
          </header>
          <PdfUploader />
          <DocumentTable />
        </div>
      </AppShell>
    </AuthGuard>
  );
}

