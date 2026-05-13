import { api } from "@/services/api";
import type { DocumentRecord, UploadResponse } from "@/types";

export async function listDocuments(): Promise<DocumentRecord[]> {
  const response = await api.get<DocumentRecord[]>("/documents");
  return response.data;
}

export async function uploadDocuments(files: File[]): Promise<UploadResponse> {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }
  const response = await api.post<UploadResponse>("/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
  return response.data;
}

export async function deleteDocument(documentId: string): Promise<void> {
  await api.delete("/documents", { params: { document_id: documentId } });
}

