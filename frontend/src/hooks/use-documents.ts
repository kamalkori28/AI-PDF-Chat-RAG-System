"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { deleteDocument, listDocuments, uploadDocuments } from "@/services/documents";

export function useDocuments() {
  return useQuery({
    queryKey: ["documents"],
    queryFn: listDocuments,
    refetchInterval: 5000
  });
}

export function useUploadDocuments() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: uploadDocuments,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["documents"] })
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["documents"] })
  });
}

