import { useEffect, useRef, useState } from "react";

// ==========================================
// CONFIG
// ==========================================

const API_BASE = import.meta.env.VITE_API_BASE_URL;

// ==========================================
// STYLES (inline, no dependencies)
// ==========================================

const styles = {
  title: {
    fontSize: "clamp(22px, 4vw, 30px)",
    fontWeight: 800,
    letterSpacing: "-0.03em",
    margin: 0,
    lineHeight: 1.1,
    background: "linear-gradient(90deg, #e9f6ff 0%, #7fd7ff 60%, #38bdf8 100%)",
    WebkitBackgroundClip: "text",
    backgroundClip: "text",
    WebkitTextFillColor: "transparent",
  },
  subtitle: {
    color: "#8a93a6",
    fontSize: "13px",
    margin: "6px 0 0",
    letterSpacing: "0.01em",
  },
  tabBtn: (active) => ({
    border: "none",
    cursor: "pointer",
    padding: "9px 20px",
    borderRadius: "9px",
    fontSize: "13px",
    fontWeight: 700,
    letterSpacing: "0.02em",
    color: active ? "#04121b" : "#aeb7c7",
    background: active
      ? "linear-gradient(180deg, #5ad1ff 0%, #22a8e0 100%)"
      : "transparent",
    boxShadow: active ? "0 6px 20px -6px rgba(56,189,248,0.65)" : "none",
    transition: "all 0.2s ease",
    position: "relative",
    zIndex: 1,
  }),
  cardTitle: {
    fontSize: "11px",
    fontWeight: 700,
    textTransform: "uppercase",
    letterSpacing: "0.16em",
    color: "#5fd0f5",
    margin: "0 0 14px",
    display: "flex",
    alignItems: "center",
    gap: "8px",
  },
  fileInput: {
    display: "block",
    width: "100%",
    fontSize: "13px",
    color: "#aeb7c7",
    marginBottom: "12px",
  },
  button: (disabled) => ({
    width: "100%",
    padding: "11px 14px",
    borderRadius: "11px",
    border: "none",
    fontSize: "14px",
    fontWeight: 700,
    letterSpacing: "0.02em",
    cursor: disabled ? "not-allowed" : "pointer",
    background: disabled
      ? "rgba(255,255,255,0.05)"
      : "linear-gradient(180deg, #5ad1ff 0%, #1e9fd8 100%)",
    color: disabled ? "#5a6373" : "#04121b",
    boxShadow: disabled ? "none" : "0 8px 24px -8px rgba(56,189,248,0.7)",
    transition: "all 0.2s ease",
  }),
  ghostButton: {
    padding: "11px 14px",
    borderRadius: "11px",
    border: "1px solid rgba(120,180,255,0.28)",
    fontSize: "14px",
    fontWeight: 700,
    cursor: "pointer",
    background: "rgba(255,255,255,0.02)",
    color: "#dbe4f3",
    transition: "all 0.2s ease",
  },
  message: (ok) => ({
    marginTop: "12px",
    fontSize: "13px",
    lineHeight: 1.5,
    color: ok ? "#5ff0b0" : "#ff8098",
  }),
  docName: {
    fontSize: "13px",
    fontWeight: 600,
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
    color: "#eef3fb",
  },
  badge: (status) => {
    const map = {
      indexed: { bg: "rgba(16,185,129,0.12)", fg: "#5ff0b0", bd: "rgba(16,185,129,0.35)" },
      processing: { bg: "rgba(251,191,36,0.12)", fg: "#fbd76e", bd: "rgba(251,191,36,0.35)" },
      failed: { bg: "rgba(244,63,94,0.12)", fg: "#ff8098", bd: "rgba(244,63,94,0.35)" },
    };
    const c = map[status] || { bg: "rgba(148,163,184,0.12)", fg: "#8a93a6", bd: "rgba(148,163,184,0.3)" };
    return {
      fontSize: "10px",
      fontWeight: 700,
      padding: "3px 9px",
      borderRadius: "999px",
      background: c.bg,
      color: c.fg,
      border: `1px solid ${c.bd}`,
      textTransform: "uppercase",
      letterSpacing: "0.08em",
      flexShrink: 0,
    };
  },
  textarea: {
    width: "100%",
    padding: "15px",
    fontSize: "15px",
    borderRadius: "13px",
    border: "1px solid rgba(120,180,255,0.18)",
    background: "rgba(4,9,16,0.6)",
    color: "#eef3fb",
    resize: "vertical",
    boxSizing: "border-box",
    fontFamily: "inherit",
    lineHeight: 1.5,
    transition: "border-color 0.2s ease, box-shadow 0.2s ease",
  },
  row: {
    display: "flex",
    gap: "10px",
    marginTop: "12px",
    flexWrap: "wrap",
  },
  statusPill: {
    display: "inline-flex",
    alignItems: "center",
    gap: "9px",
    fontSize: "13px",
    color: "#7fd7ff",
    marginTop: "16px",
  },
  dot: {
    width: "9px",
    height: "9px",
    borderRadius: "50%",
    background: "#38bdf8",
    boxShadow: "0 0 10px 2px rgba(56,189,248,0.8)",
    animation: "pulse 1s ease-in-out infinite",
  },
  answerBox: {
    marginTop: "20px",
    padding: "20px",
    borderRadius: "13px",
    background:
      "linear-gradient(180deg, rgba(9,16,28,0.9) 0%, rgba(6,11,20,0.9) 100%)",
    border: "1px solid rgba(120,180,255,0.15)",
    whiteSpace: "pre-wrap",
    fontSize: "15px",
    lineHeight: 1.7,
    minHeight: "80px",
    color: "#eef3fb",
  },
  sourceItem: {
    padding: "12px 14px",
    borderRadius: "11px",
    background: "rgba(4,9,16,0.55)",
    border: "1px solid rgba(120,180,255,0.14)",
    marginBottom: "8px",
    fontSize: "13px",
    color: "#dbe4f3",
  },
  sourceMeta: {
    color: "#5fd0f5",
    fontSize: "12px",
    marginBottom: "5px",
    fontWeight: 600,
    letterSpacing: "0.02em",
  },
  empty: {
    color: "#5a6373",
    fontSize: "13px",
    fontStyle: "italic",
  },
};

// ==========================================
// APP
// ==========================================

export default function App() {
  const [tab, setTab] = useState("chat");

  // ---------- PDF ----------
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadOk, setUploadOk] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [deletingId, setDeletingId] = useState(null);
  // ---------- CHAT ----------
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [sources, setSources] = useState([]);
  const controllerRef = useRef(null);

  // ---------- SEARCH ----------
  const [searchQuery, setSearchQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [searching, setSearching] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [searchError, setSearchError] = useState("");

  const hasDocuments = documents.some((d) => d.status === "indexed");

  // ==========================================
  // LOAD DOCUMENTS
  // ==========================================

  async function loadDocuments() {
    try {
      const res = await fetch(`${API_BASE}/pdf/documents`);
      if (!res.ok) throw new Error("Failed to load documents");
      const data = await res.json();

      setDocuments(
        Array.isArray(data)
          ? data
          : data.documents || []
      );
    } catch (err) {
      console.log("[v0] loadDocuments error:", err.message);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  // ==========================================
  // PDF UPLOAD
  // ==========================================
  async function deleteDocument(documentId, filename) {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${filename}"?`
    );

    if (!confirmed) return;

    setDeletingId(documentId);

    try {
      const res = await fetch(
        `${API_BASE}/pdf/${documentId}`,
        {
          method: "DELETE",
        }
      );

      const data = await res.json();

      if (!res.ok) {
        throw new Error(
          data.detail || "Failed to delete document"
        );
      }

      // Remove from UI immediately
      setDocuments((prev) =>
        prev.filter((doc) => doc.id !== documentId)
      );

      // Clear current results because the index changed
      setSearchResults([]);
      setSources([]);

      setUploadMessage(
        `"${filename}" deleted successfully.`
      );

      setUploadOk(true);

    } catch (err) {

      console.error(
        "Delete error:",
        err.message
      );

      setUploadMessage(
        err.message || "Failed to delete document"
      );

      setUploadOk(false);

    } finally {

      setDeletingId(null);
    }
  }
  async function uploadPDF() {
    if (!file) return;

    setUploading(true);
    setUploadMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/pdf/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "PDF upload failed");
      }

      setUploaded(true);
      setUploadOk(true);
      setUploadMessage(
        `Uploaded "${data.filename}" — ${data.chunks} chunks indexed successfully.`
      );
      setFile(null);
      loadDocuments();
    } catch (err) {
      console.log("[v0] upload error:", err.message);
      setUploaded(false);
      setUploadOk(false);
      setUploadMessage(err.message || "PDF upload failed");
    } finally {
      setUploading(false);
    }
  }

  // ==========================================
  // CHAT STREAM (SSE over fetch)
  // ==========================================

  async function sendMessage() {
    if (!question.trim()) return;

    setAnswer("");
    setStatus("");
    setSources([]);
    setLoading(true);

    const controller = new AbortController();
    controllerRef.current = controller;

    try {
      const res = await fetch(`${API_BASE}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: question }),
        signal: controller.signal,
      });

      if (!res.ok) throw new Error("Request failed");
      if (!res.body) throw new Error("Streaming not supported");

      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split("\n\n");
        buffer = events.pop() || "";

        for (const event of events) {
          if (!event.startsWith("data:")) continue;
          const jsonData = event.slice(5).trim();

          try {
            const parsed = JSON.parse(jsonData);

            if (parsed.type === "status") {
              setStatus(parsed.data?.message || "");
            } else if (parsed.type === "token") {
              const content = parsed.data?.content || "";
              setAnswer((prev) => prev + content);
            } else if (parsed.type === "source") {
              setSources((prev) => [
                ...prev,
                {
                  document: parsed.data?.document,
                  page: parsed.data?.page,
                  text: parsed.data?.text,
                },
              ]);
            } else if (parsed.type === "done") {
              setStatus("");
            } else if (parsed.type === "error") {
              setStatus(parsed.data?.message || "Generation failed");
            }
          } catch {
            console.log("[v0] invalid SSE JSON:", jsonData);
          }
        }
      }
    } catch (err) {
      if (err.name === "AbortError") {
        setStatus("Generation stopped");
        return;
      }
      console.log("[v0] chat error:", err.message);
      setStatus("Something went wrong.");
    } finally {
      controllerRef.current = null;
      setLoading(false);
    }
  }

  function stopGeneration() {
    if (controllerRef.current) {
      controllerRef.current.abort();
      controllerRef.current = null;
    }
    setLoading(false);
  }

  function handleChatKeyDown(e) {
    if (e.nativeEvent.isComposing || e.keyCode === 229) return;
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!loading && question.trim()) sendMessage();
    }
  }

  // ==========================================
  // SEARCH
  // ==========================================

  async function runSearch() {
    if (!searchQuery.trim()) return;

    setSearching(true);
    setSearchError("");
    setSearchResults([]);

    try {
      const res = await fetch(`${API_BASE}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: searchQuery,
          top_k: Number(topK) || 5,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Search failed");
      }

      setSearchResults(data.results || []);
    } catch (err) {
      console.log("[v0] search error:", err.message);
      setSearchError(err.message || "Search failed");
    } finally {
      setSearching(false);
    }
  }

  function handleSearchKeyDown(e) {
    if (e.nativeEvent.isComposing || e.keyCode === 229) return;
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!searching && searchQuery.trim()) runSearch();
    }
  }

  // ==========================================
  // RENDER
  // ==========================================

  return (
    <div className="pai-page">
      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
        @keyframes paiFloat { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }
        @keyframes paiFadeUp { from{opacity:0;transform:translateY(14px)} to{opacity:1;transform:translateY(0)} }
        @keyframes paiScan { 0%{transform:translateY(-100%)} 100%{transform:translateY(100%)} }

        * { box-sizing: border-box; }

        .pai-page {
          min-height: 100vh;
          position: relative;
          overflow-x: hidden;
          color: #e7e9ee;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
          background:
            radial-gradient(1000px 500px at 15% -10%, rgba(56,189,248,0.14), transparent 60%),
            radial-gradient(900px 500px at 100% 0%, rgba(99,102,241,0.12), transparent 55%),
            #05080f;
        }
        /* tech grid overlay */
        .pai-page::before {
          content: "";
          position: fixed;
          inset: 0;
          background-image:
            linear-gradient(rgba(120,180,255,0.045) 1px, transparent 1px),
            linear-gradient(90deg, rgba(120,180,255,0.045) 1px, transparent 1px);
          background-size: 44px 44px;
          mask-image: radial-gradient(circle at 50% 20%, #000 0%, transparent 80%);
          -webkit-mask-image: radial-gradient(circle at 50% 20%, #000 0%, transparent 80%);
          pointer-events: none;
        }

        .pai-shell {
          position: relative;
          max-width: 1120px;
          margin: 0 auto;
          padding: 40px 20px 72px;
          animation: paiFadeUp 0.5s ease both;
        }

        .pai-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 28px;
          flex-wrap: wrap;
          gap: 16px;
        }

        .pai-eyebrow {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          font-size: 11px;
          font-weight: 700;
          letter-spacing: 0.22em;
          text-transform: uppercase;
          color: #5fd0f5;
          margin-bottom: 10px;
        }
        .pai-eyebrow span.dotlive {
          width: 7px; height: 7px; border-radius: 50%;
          background: #38bdf8; box-shadow: 0 0 10px 2px rgba(56,189,248,0.8);
          animation: pulse 1.2s ease-in-out infinite;
        }

        .pai-tabs {
          display: inline-flex;
          background: rgba(10,16,28,0.7);
          border: 1px solid rgba(120,180,255,0.18);
          border-radius: 12px;
          padding: 5px;
          gap: 4px;
          backdrop-filter: blur(10px);
        }

        .pai-grid {
          display: grid;
          grid-template-columns: 320px 1fr;
          gap: 20px;
          align-items: start;
        }

        .pai-card {
          position: relative;
          background: linear-gradient(180deg, rgba(14,21,36,0.72) 0%, rgba(8,13,24,0.72) 100%);
          border: 1px solid rgba(120,180,255,0.16);
          border-radius: 18px;
          padding: 22px;
          backdrop-filter: blur(14px);
          box-shadow: 0 24px 60px -30px rgba(0,0,0,0.9), inset 0 1px 0 rgba(255,255,255,0.04);
          overflow: hidden;
        }
        .pai-card::after {
          content: "";
          position: absolute;
          top: 0; left: 0; right: 0;
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(56,189,248,0.6), transparent);
        }

        .pai-doc {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 8px;
          padding: 11px 13px;
          border-radius: 12px;
          background: rgba(4,9,16,0.5);
          border: 1px solid rgba(120,180,255,0.12);
          margin-bottom: 8px;
          transition: border-color 0.2s ease, transform 0.2s ease;
        }
        .pai-doc:hover { border-color: rgba(56,189,248,0.4); transform: translateX(2px); }

        .pai-tabbtn:hover { color: #eef3fb; }
        .pai-ghost:hover { border-color: rgba(56,189,248,0.5); background: rgba(56,189,248,0.06); }
        .pai-primary:not(:disabled):hover { transform: translateY(-1px); filter: brightness(1.05); }
        .pai-primary:not(:disabled):active { transform: translateY(0); }

        textarea:focus, input:focus {
          outline: none;
          border-color: #38bdf8 !important;
          box-shadow: 0 0 0 3px rgba(56,189,248,0.18) !important;
        }

        .pai-title-icon {
          width: 46px; height: 46px; flex-shrink: 0;
          border-radius: 13px;
          display: grid; place-items: center;
          background: linear-gradient(180deg, rgba(56,189,248,0.22), rgba(56,189,248,0.06));
          border: 1px solid rgba(56,189,248,0.35);
          box-shadow: 0 10px 30px -10px rgba(56,189,248,0.6);
          animation: paiFloat 4s ease-in-out infinite;
        }

        @media (max-width: 860px) {
          .pai-grid { grid-template-columns: 1fr; }
        }
        @media (max-width: 640px) {
          .pai-shell { padding: 26px 14px 56px; }
          .pai-header { margin-bottom: 22px; }
          .pai-tabs { width: 100%; }
          .pai-tabbtn { flex: 1; }
          .pai-card { padding: 18px; border-radius: 16px; }
        }
      `}</style>

      <div className="pai-shell">
        <header className="pai-header">
          <div style={{ display: "flex", gap: "14px", alignItems: "center", minWidth: 0 }}>
            <div className="pai-title-icon" aria-hidden="true">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#7fd7ff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <path d="M14 2v6h6" />
                <path d="M9 13h6M9 17h4" />
              </svg>
            </div>
            <div style={{ minWidth: 0 }}>
              <div className="pai-eyebrow">
                <span className="dotlive" /> Neural Document Engine
              </div>
              <h1 style={styles.title}>PDF AI Chat</h1>
              <p style={styles.subtitle}>
                Upload PDFs, ask questions, and search your documents.
              </p>
            </div>
          </div>

          <div className="pai-tabs">
            <button
              className="pai-tabbtn"
              style={styles.tabBtn(tab === "chat")}
              onClick={() => setTab("chat")}
            >
              Chat
            </button>
            <button
              className="pai-tabbtn"
              style={styles.tabBtn(tab === "search")}
              onClick={() => setTab("search")}
            >
              Search
            </button>
          </div>
        </header>

        <div className="pai-grid">
          {/* ============ SIDEBAR ============ */}
          <aside className="pai-card">
            <h2 style={styles.cardTitle}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="M12 5v14M5 12h14" /></svg>
              Upload PDF
            </h2>

            <input
              style={styles.fileInput}
              type="file"
              accept="application/pdf"
              onChange={(e) => {
                setFile(e.target.files[0] || null);
                setUploadMessage("");
              }}
            />

            <button
              className="pai-primary"
              style={styles.button(uploading || !file)}
              onClick={uploadPDF}
              disabled={uploading || !file}
            >
              {uploading ? "Uploading..." : "Upload & Index"}
            </button>

            {uploadMessage && (
              <p style={styles.message(uploadOk)}>
                {uploadMessage}
              </p>
            )}

            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                margin: "24px 0 12px",
              }}
            >
              <h2
                style={{
                  ...styles.cardTitle,
                  margin: 0,
                }}
              >
                Documents
              </h2>

              <button
                onClick={loadDocuments}
                className="pai-ghost"
                style={{
                  ...styles.ghostButton,
                  padding: "5px 12px",
                  fontSize: "12px",
                }}
              >
                Refresh
              </button>
            </div>

            {documents.length === 0 ? (
              <p style={styles.empty}>
                No documents yet.
              </p>
            ) : (
              documents.map((doc) => (
                <div
                  key={doc.id}
                  className="pai-doc"
                >
                  <div
                    style={{
                      minWidth: 0,
                      flex: 1,
                    }}
                  >
                    <div
                      style={styles.docName}
                      title={doc.filename}
                    >
                      {doc.filename}
                    </div>

                    <div
                      style={{
                        marginTop: "6px",
                      }}
                    >
                      <span style={styles.badge(doc.status)}>
                        {doc.status}
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={() =>
                      deleteDocument(
                        doc.id,
                        doc.filename
                      )
                    }
                    disabled={deletingId === doc.id}
                    style={{
                      border: "1px solid rgba(244,63,94,0.35)",
                      background: "rgba(244,63,94,0.06)",
                      color: "#ff8098",
                      borderRadius: "9px",
                      padding: "7px 11px",
                      fontSize: "12px",
                      fontWeight: 700,
                      cursor:
                        deletingId === doc.id
                          ? "not-allowed"
                          : "pointer",
                      opacity:
                        deletingId === doc.id
                          ? 0.5
                          : 1,
                      flexShrink: 0,
                      transition: "all 0.2s ease",
                    }}
                  >
                    {deletingId === doc.id
                      ? "Deleting..."
                      : "Delete"}
                  </button>
                </div>
              ))
            )}
          </aside>

          {/* ============ MAIN ============ */}
          <main>
            {tab === "chat" ? (
              <section className="pai-card">
                <h2 style={styles.cardTitle}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg>
                  Ask a question
                </h2>

                <textarea
                  style={styles.textarea}
                  rows={4}
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={handleChatKeyDown}
                  placeholder={
                    hasDocuments
                      ? "Ask something about your documents... (Enter to send)"
                      : "Upload and index a PDF first..."
                  }
                  disabled={loading}
                />

                <div style={styles.row}>
                  {!loading ? (
                    <button
                      className="pai-primary"
                      style={styles.button(!question.trim())}
                      onClick={sendMessage}
                      disabled={!question.trim()}
                    >
                      Send
                    </button>
                  ) : (
                    <button className="pai-ghost" style={styles.ghostButton} onClick={stopGeneration}>
                      Stop generating
                    </button>
                  )}
                </div>

                {status && (
                  <div style={styles.statusPill}>
                    <span style={styles.dot} />
                    {status}
                  </div>
                )}

                <div style={styles.answerBox}>
                  {answer || (
                    <span style={styles.empty}>
                      The AI response will appear here.
                    </span>
                  )}
                </div>

                {sources.length > 0 && (
                  <div style={{ marginTop: "20px" }}>
                    <h2 style={styles.cardTitle}>Sources</h2>
                    {sources.map((s, i) => (
                      <div key={i} style={styles.sourceItem}>
                        <div style={styles.sourceMeta}>
                          {s.document} — Page {s.page}
                        </div>
                        {s.text && <div>{s.text}</div>}
                      </div>
                    ))}
                  </div>
                )}
              </section>
            ) : (
              <section className="pai-card">
                <h2 style={styles.cardTitle}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="7" /><path d="m21 21-4.3-4.3" /></svg>
                  Semantic search
                </h2>

                <textarea
                  style={styles.textarea}
                  rows={2}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={handleSearchKeyDown}
                  placeholder="Search across indexed documents... (Enter to search)"
                />

                <div style={styles.row}>
                  <label
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      fontSize: "13px",
                      color: "#8a93a6",
                    }}
                  >
                    Top K
                    <input
                      type="number"
                      min={1}
                      max={20}
                      value={topK}
                      onChange={(e) => setTopK(e.target.value)}
                      style={{
                        width: "64px",
                        padding: "9px",
                        borderRadius: "9px",
                        border: "1px solid rgba(120,180,255,0.18)",
                        background: "rgba(4,9,16,0.6)",
                        color: "#eef3fb",
                      }}
                    />
                  </label>
                  <button
                    className="pai-primary"
                    style={{ ...styles.button(searching || !searchQuery.trim()), width: "auto", padding: "11px 22px" }}
                    onClick={runSearch}
                    disabled={searching || !searchQuery.trim()}
                  >
                    {searching ? "Searching..." : "Search"}
                  </button>
                </div>

                {searchError && (
                  <p style={styles.message(false)}>{searchError}</p>
                )}

                <div style={{ marginTop: "20px" }}>
                  {searchResults.length === 0 ? (
                    <p style={styles.empty}>No results yet.</p>
                  ) : (
                    searchResults.map((r, i) => (
                      <div key={r.chunk_id || i} style={styles.sourceItem}>
                        <div style={styles.sourceMeta}>
                          {r.document} — Page {r.page}
                          {typeof r.distance === "number" &&
                            ` · distance ${r.distance.toFixed(3)}`}
                        </div>
                        <div>{r.text}</div>
                      </div>
                    ))
                  )}
                </div>
              </section>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}