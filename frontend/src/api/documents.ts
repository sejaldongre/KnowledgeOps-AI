import apiClient from "./client";

export type DocumentStatus =
  | "draft"
  | "uploaded"
  | "processing"
  | "processed"
  | "failed";

export interface DocumentResponse {
  id: string;
  title: string;
  description: string | null;
  status: DocumentStatus;
  owner_id: string;
  folder_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentVersionResponse {
  id: string;
  document_id: string;
  version_number: number;
  storage_path: string;
  file_hash: string;
  created_by: string;
  created_at: string;
}

export interface DocumentCreateRequest {
  title: string;
  filename: string;
  file_type: string;
  file_size: number;
  description?: string | null;
  folder_id?: string | null;
}

export interface DocumentUpdateRequest {
  title?: string | null;
  description?: string | null;
}

export async function getDocuments(
  status?: DocumentStatus,
): Promise<DocumentResponse[]> {
  const response =
    await apiClient.get<DocumentResponse[]>(
      "/documents",
      {
        params: status ? { status } : undefined,
      },
    );

  return response.data;
}

export async function getDocument(
  documentId: string,
): Promise<DocumentResponse> {
  const response =
    await apiClient.get<DocumentResponse>(
      `/documents/${documentId}`,
    );

  return response.data;
}

export async function getDocumentVersions(
  documentId: string,
): Promise<DocumentVersionResponse[]> {
  const response =
    await apiClient.get<DocumentVersionResponse[]>(
      `/documents/${documentId}/versions`,
    );

  return response.data;
}

export async function createDocument(
  data: DocumentCreateRequest,
): Promise<DocumentResponse> {
  const response =
    await apiClient.post<DocumentResponse>(
      "/documents",
      data,
    );

  return response.data;
}

export async function uploadDocumentVersion(
  documentId: string,
  file: File,
): Promise<DocumentVersionResponse> {
  const formData = new FormData();

  formData.append("file", file);

  const response =
    await apiClient.post<DocumentVersionResponse>(
      `/documents/${documentId}/upload`,
      formData,
    );

  return response.data;
}

export async function updateDocument(
  documentId: string,
  data: DocumentUpdateRequest,
): Promise<DocumentResponse> {
  const response =
    await apiClient.patch<DocumentResponse>(
      `/documents/${documentId}`,
      data,
    );

  return response.data;
}

export async function deleteDocument(
  documentId: string,
): Promise<void> {
  await apiClient.delete(
    `/documents/${documentId}`,
  );
}