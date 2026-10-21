interface Document {
  id: string;
  title: string;
  tags: readonly string[];
}

// A missing document should be an ordinary result.
export async function findDocument(id: string): Promise<Document | null> {
  const response = await fetch(`/api/documents/${encodeURIComponent(id)}`);
  if (response.status === 404) return null;
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  const document: Document = await response.json();
  return { ...document, tags: document.tags ?? [] };
}
