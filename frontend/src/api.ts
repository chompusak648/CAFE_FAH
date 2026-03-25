const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8001').replace(/\/$/, '');

export interface ChatRequest {
    message: string;
    session_id?: string;
    mode?: string;
    top_k?: number;
}


export const chat = async (req: ChatRequest) => {
    const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req)
    });
    if (!res.ok) {
        let errMsg = `Server error (${res.status})`;
        try {
            const body = await res.json();
            errMsg = body?.error || body?.detail || errMsg;
        } catch (_) {}
        throw new Error(errMsg);
    }
    return res.json();
};

export const ingestFile = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_URL}/ingest/file`, {
        method: 'POST',
        body: formData
    });
    if (!res.ok) throw new Error('Upload failed');
    return res.json();
};

export const listDocuments = async () => {
    const res = await fetch(`${API_URL}/documents`);
    if (!res.ok) throw new Error('Failed to list documents');
    return res.json() as Promise<{ doc_id: string; filename: string; chunks: number }[]>;
};

export const deleteDocument = async (doc_id: string) => {
    const res = await fetch(`${API_URL}/documents/${doc_id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete document');
    return res.json();
};
