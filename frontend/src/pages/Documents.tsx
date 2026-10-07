import { useEffect, useState } from "react";
import {
  AlertCircle,
  FileText,
  Loader2,
  RefreshCw,
  Upload,
  X,
} from "lucide-react";

import {
  createDocument,
  getDocuments,
  uploadDocumentVersion,
  type DocumentResponse,
} from "../api/documents";

function Documents() {
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const [showUploadModal, setShowUploadModal] =
    useState(false);

  const [showVersionModal, setShowVersionModal] =
    useState(false);

  const [selectedDocument, setSelectedDocument] =
    useState<DocumentResponse | null>(null);

  const [uploading, setUploading] = useState(false);
  const [versionUploading, setVersionUploading] =
    useState(false);

  const [error, setError] = useState("");
  const [uploadError, setUploadError] = useState("");
  const [versionError, setVersionError] = useState("");

  const [title, setTitle] = useState("");
  const [description, setDescription] =
    useState("");

  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);

  const [versionFile, setVersionFile] =
    useState<File | null>(null);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getDocuments();

      setDocuments(data);
    } catch (err) {
      console.error(
        "Failed to load documents:",
        err,
      );

      setError(
        "Unable to load documents. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const resetUploadForm = () => {
    setTitle("");
    setDescription("");
    setSelectedFile(null);
    setUploadError("");
  };

  const resetVersionForm = () => {
    setVersionFile(null);
    setVersionError("");
    setSelectedDocument(null);
  };

  const closeUploadModal = () => {
    if (uploading) {
      return;
    }

    setShowUploadModal(false);
    resetUploadForm();
  };

  const closeVersionModal = () => {
    if (versionUploading) {
      return;
    }

    setShowVersionModal(false);
    resetVersionForm();
  };

  const handleFileChange = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setSelectedFile(file);

    if (!title.trim()) {
      const filenameWithoutExtension =
        file.name.replace(/\.[^/.]+$/, "");

      setTitle(filenameWithoutExtension);
    }
  };

  const handleVersionFileChange = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setVersionFile(file);
    setVersionError("");
  };

  const handleUpload = async () => {
    setUploadError("");

    if (!selectedFile) {
      setUploadError(
        "Please select a PDF or DOCX file.",
      );
      return;
    }

    if (!title.trim()) {
      setUploadError(
        "Please enter a document title.",
      );
      return;
    }

    const fileExtension =
      selectedFile.name
        .split(".")
        .pop()
        ?.toLowerCase();

    if (
      fileExtension !== "pdf" &&
      fileExtension !== "docx"
    ) {
      setUploadError(
        "Only PDF and DOCX files are supported.",
      );
      return;
    }

    try {
      setUploading(true);

      // Step 1: Create document metadata.
      const document = await createDocument({
        title: title.trim(),
        filename: selectedFile.name,
        file_type:
          selectedFile.type ||
          `application/${fileExtension}`,
        file_size: selectedFile.size,
        description:
          description.trim() || null,
      });

      // Step 2: Upload the actual file.
      await uploadDocumentVersion(
        document.id,
        selectedFile,
      );

      // Step 3: Refresh the document list.
      await loadDocuments();

      closeUploadModal();
    } catch (err: any) {
      console.error(
        "Failed to upload document:",
        err,
      );

      const message =
        err?.response?.data?.detail ||
        "Failed to upload document. Please try again.";

      setUploadError(
        typeof message === "string"
          ? message
          : "Failed to upload document. Please try again.",
      );
    } finally {
      setUploading(false);
    }
  };

  const openVersionUpload = (
    document: DocumentResponse,
  ) => {
    setSelectedDocument(document);
    setVersionFile(null);
    setVersionError("");
    setShowVersionModal(true);
  };

  const handleVersionUpload = async () => {
    setVersionError("");

    if (!selectedDocument) {
      setVersionError(
        "No document selected.",
      );
      return;
    }

    if (!versionFile) {
      setVersionError(
        "Please select a PDF or DOCX file.",
      );
      return;
    }

    const fileExtension =
      versionFile.name
        .split(".")
        .pop()
        ?.toLowerCase();

    if (
      fileExtension !== "pdf" &&
      fileExtension !== "docx"
    ) {
      setVersionError(
        "Only PDF and DOCX files are supported.",
      );
      return;
    }

    try {
      setVersionUploading(true);

      await uploadDocumentVersion(
        selectedDocument.id,
        versionFile,
      );

      await loadDocuments();

      closeVersionModal();
    } catch (err: any) {
      console.error(
        "Failed to upload document version:",
        err,
      );

      const message =
        err?.response?.data?.detail ||
        "Failed to upload document version. Please try again.";

      setVersionError(
        typeof message === "string"
          ? message
          : "Failed to upload document version. Please try again.",
      );
    } finally {
      setVersionUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="border-b border-slate-200 bg-white">
        <div className="px-8 py-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">
                Documents
              </h1>

              <p className="mt-1 text-sm text-slate-500">
                Manage your organization's knowledge base.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={loadDocuments}
                disabled={loading}
                className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <RefreshCw
                  size={16}
                  className={
                    loading
                      ? "animate-spin"
                      : ""
                  }
                />

                Refresh
              </button>

              <button
                onClick={() =>
                  setShowUploadModal(true)
                }
                className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700"
              >
                <Upload size={17} />

                Upload Document
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <main className="px-8 py-8">
        {/* Loading */}
        {loading && (
          <div className="flex min-h-[300px] items-center justify-center rounded-2xl border border-slate-200 bg-white">
            <div className="flex flex-col items-center gap-3 text-slate-500">
              <Loader2
                size={32}
                className="animate-spin text-blue-600"
              />

              <p className="text-sm">
                Loading documents...
              </p>
            </div>
          </div>
        )}

        {/* Error */}
        {!loading && error && (
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6">
            <div className="flex items-start gap-3">
              <AlertCircle
                size={20}
                className="mt-0.5 text-red-600"
              />

              <div>
                <h2 className="font-semibold text-red-800">
                  Something went wrong
                </h2>

                <p className="mt-1 text-sm text-red-700">
                  {error}
                </p>

                <button
                  onClick={loadDocuments}
                  className="mt-4 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
                >
                  Try again
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Empty state */}
        {!loading &&
          !error &&
          documents.length === 0 && (
            <div className="flex min-h-[300px] flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white px-6 text-center">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100">
                <FileText
                  size={28}
                  className="text-slate-500"
                />
              </div>

              <h2 className="mt-4 text-lg font-semibold text-slate-900">
                No documents yet
              </h2>

              <p className="mt-1 max-w-md text-sm text-slate-500">
                Upload documents to build your
                organization's searchable knowledge
                base.
              </p>

              <button
                onClick={() =>
                  setShowUploadModal(true)
                }
                className="mt-5 flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
              >
                <Upload size={17} />

                Upload your first document
              </button>
            </div>
          )}

        {/* Documents */}
        {!loading &&
          !error &&
          documents.length > 0 && (
            <div>
              <div className="mb-6">
                <p className="text-sm font-medium text-slate-900">
                  {documents.length}{" "}
                  {documents.length === 1
                    ? "document"
                    : "documents"}
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  Documents available in your
                  workspace
                </p>
              </div>

              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                {documents.map((document) => (
                  <div
                    key={document.id}
                    className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50">
                        <FileText
                          size={22}
                          className="text-blue-600"
                        />
                      </div>

                      <span
                        className={`rounded-full px-3 py-1 text-xs font-medium ${
                          document.status ===
                          "processed"
                            ? "bg-emerald-50 text-emerald-700"
                            : document.status ===
                                "processing"
                              ? "bg-amber-50 text-amber-700"
                              : document.status ===
                                  "failed"
                                ? "bg-red-50 text-red-700"
                                : "bg-slate-100 text-slate-600"
                        }`}
                      >
                        {document.status}
                      </span>
                    </div>

                    <h2 className="mt-5 truncate text-base font-semibold text-slate-900">
                      {document.title}
                    </h2>

                    <p className="mt-2 min-h-[40px] text-sm text-slate-500">
                      {document.description ||
                        "No description provided."}
                    </p>

                    <div className="mt-5 border-t border-slate-100 pt-4">
                      <p className="text-xs text-slate-400">
                        Created
                      </p>

                      <p className="mt-1 text-sm text-slate-600">
                        {new Date(
                          document.created_at,
                        ).toLocaleDateString()}
                      </p>

                      <button
                        onClick={() =>
                          openVersionUpload(document)
                        }
                        className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg border border-blue-200 bg-blue-50 px-3 py-2.5 text-sm font-semibold text-blue-700 transition hover:bg-blue-100"
                      >
                        <Upload size={16} />

                        Upload New Version
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
      </main>

      {/* Create Document Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 px-4 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-2xl bg-white shadow-2xl">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-200 px-6 py-5">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  Upload Document
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Add a document to your knowledge base.
                </p>
              </div>

              <button
                onClick={closeUploadModal}
                disabled={uploading}
                className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="space-y-5 px-6 py-6">
              {uploadError && (
                <div className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4">
                  <AlertCircle
                    size={18}
                    className="mt-0.5 shrink-0 text-red-600"
                  />

                  <p className="text-sm text-red-700">
                    {uploadError}
                  </p>
                </div>
              )}

              {/* Title */}
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Document title
                </label>

                <input
                  type="text"
                  value={title}
                  onChange={(event) =>
                    setTitle(event.target.value)
                  }
                  placeholder="e.g. Employee Leave Policy"
                  disabled={uploading}
                  className="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-50"
                />
              </div>

              {/* Description */}
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Description
                  <span className="ml-1 font-normal text-slate-400">
                    (optional)
                  </span>
                </label>

                <textarea
                  value={description}
                  onChange={(event) =>
                    setDescription(
                      event.target.value,
                    )
                  }
                  placeholder="Briefly describe this document..."
                  rows={3}
                  disabled={uploading}
                  className="w-full resize-none rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-50"
                />
              </div>

              {/* File */}
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Document file
                </label>

                <label className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-8 text-center transition hover:border-blue-400 hover:bg-blue-50/40">
                  <Upload
                    size={28}
                    className="text-blue-600"
                  />

                  {selectedFile ? (
                    <>
                      <p className="mt-3 text-sm font-medium text-slate-900">
                        {selectedFile.name}
                      </p>

                      <p className="mt-1 text-xs text-slate-500">
                        {(
                          selectedFile.size /
                          1024 /
                          1024
                        ).toFixed(2)}{" "}
                        MB
                      </p>
                    </>
                  ) : (
                    <>
                      <p className="mt-3 text-sm font-medium text-slate-700">
                        Click to select a file
                      </p>

                      <p className="mt-1 text-xs text-slate-500">
                        PDF or DOCX files
                      </p>
                    </>
                  )}

                  <input
                    type="file"
                    accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    onChange={handleFileChange}
                    disabled={uploading}
                    className="hidden"
                  />
                </label>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex justify-end gap-3 border-t border-slate-200 px-6 py-5">
              <button
                onClick={closeUploadModal}
                disabled={uploading}
                className="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Cancel
              </button>

              <button
                onClick={handleUpload}
                disabled={uploading}
                className="flex min-w-[120px] items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {uploading ? (
                  <>
                    <Loader2
                      size={17}
                      className="animate-spin"
                    />

                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload size={17} />

                    Upload
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Upload New Version Modal */}
      {showVersionModal && selectedDocument && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 px-4 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-2xl bg-white shadow-2xl">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-200 px-6 py-5">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  Upload New Version
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  {selectedDocument.title}
                </p>
              </div>

              <button
                onClick={closeVersionModal}
                disabled={versionUploading}
                className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="space-y-5 px-6 py-6">
              {versionError && (
                <div className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4">
                  <AlertCircle
                    size={18}
                    className="mt-0.5 shrink-0 text-red-600"
                  />

                  <p className="text-sm text-red-700">
                    {versionError}
                  </p>
                </div>
              )}

              <div className="rounded-xl border border-blue-100 bg-blue-50 p-4">
                <p className="text-sm font-medium text-blue-900">
                  Updating existing document
                </p>

                <p className="mt-1 text-xs leading-5 text-blue-700">
                  The selected file will become a new
                  version of this document and will be
                  processed for RAG search.
                </p>
              </div>

              {/* Version File */}
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  New document file
                </label>

                <label className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-8 text-center transition hover:border-blue-400 hover:bg-blue-50/40">
                  <Upload
                    size={28}
                    className="text-blue-600"
                  />

                  {versionFile ? (
                    <>
                      <p className="mt-3 text-sm font-medium text-slate-900">
                        {versionFile.name}
                      </p>

                      <p className="mt-1 text-xs text-slate-500">
                        {(
                          versionFile.size /
                          1024 /
                          1024
                        ).toFixed(2)}{" "}
                        MB
                      </p>
                    </>
                  ) : (
                    <>
                      <p className="mt-3 text-sm font-medium text-slate-700">
                        Click to select a file
                      </p>

                      <p className="mt-1 text-xs text-slate-500">
                        PDF or DOCX files
                      </p>
                    </>
                  )}

                  <input
                    type="file"
                    accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    onChange={handleVersionFileChange}
                    disabled={versionUploading}
                    className="hidden"
                  />
                </label>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex justify-end gap-3 border-t border-slate-200 px-6 py-5">
              <button
                onClick={closeVersionModal}
                disabled={versionUploading}
                className="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Cancel
              </button>

              <button
                onClick={handleVersionUpload}
                disabled={versionUploading}
                className="flex min-w-[160px] items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {versionUploading ? (
                  <>
                    <Loader2
                      size={17}
                      className="animate-spin"
                    />

                    Processing...
                  </>
                ) : (
                  <>
                    <Upload size={17} />

                    Upload Version
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Documents;