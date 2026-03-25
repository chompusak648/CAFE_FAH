import { useState, useEffect, useCallback } from 'react';
import { Bot, User, Send, Upload, FileText, Trash2, Loader2, CheckCircle2 } from 'lucide-react';
import { chat, ingestFile, listDocuments, deleteDocument } from './api';

interface Msg {
    role: 'user' | 'bot';
    text: string;
    citations?: any[];
    tool_trace?: any[];
}

interface DocInfo {
    doc_id: string;
    filename: string;
    chunks: number;
}

function App() {
    const [messages, setMessages] = useState<Msg[]>([]);
    const [input, setInput] = useState('');
    const [mode, setMode] = useState('auto');
    const [loading, setLoading] = useState(false);
    const [documents, setDocuments] = useState<DocInfo[]>([]);
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'processing' | 'done' | 'error'>('idle');
    const [uploadMsg, setUploadMsg] = useState('');

    const fetchDocuments = useCallback(async () => {
        try {
            const docs = await listDocuments();
            setDocuments(docs);
        } catch (_) { }
    }, []);

    useEffect(() => {
        fetchDocuments();
        const interval = setInterval(fetchDocuments, 5000);
        return () => clearInterval(interval);
    }, [fetchDocuments]);

    const sendMessage = async () => {
        if (!input.trim()) return;
        const userMsg = input;
        setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
        setInput('');
        setLoading(true);

        try {
            const res = await chat({ message: userMsg, mode });
            setMessages(prev => [...prev, {
                role: 'bot',
                text: res.answer_text,
                citations: res.citations,
                tool_trace: res.tool_trace
            }]);
        } catch (err: any) {
            let errMsg = 'Error connecting to server.';
            if (err?.message) errMsg = err.message;
            setMessages(prev => [...prev, { role: 'bot', text: `⚠️ ${errMsg}` }]);
        }
        setLoading(false);
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            const file = e.target.files[0];
            e.target.value = '';
            setUploadStatus('uploading');
            setUploadMsg(`Uploading ${file.name}...`);
            try {
                await ingestFile(file);
                setUploadStatus('processing');
                setUploadMsg(`Processing ${file.name}... (this may take a moment)`);
                // Poll until the doc appears in the list
                let attempts = 0;
                const poll = setInterval(async () => {
                    attempts++;
                    await fetchDocuments();
                    if (attempts > 20) {
                        clearInterval(poll);
                        setUploadStatus('done');
                        setUploadMsg('Done! Document is ready.');
                        setTimeout(() => setUploadStatus('idle'), 3000);
                    }
                }, 2000);
            } catch (err) {
                setUploadStatus('error');
                setUploadMsg('Upload failed. Please try again.');
                setTimeout(() => setUploadStatus('idle'), 4000);
            }
        }
    };

    const handleDelete = async (doc_id: string, filename: string) => {
        if (!window.confirm(`Delete "${filename}"?`)) return;
        try {
            await deleteDocument(doc_id);
            await fetchDocuments();
        } catch (_) {
            alert('Failed to delete document.');
        }
    };

    return (
        <div className="flex h-screen bg-[#fffdfa] text-[#5c4033] font-sans">
            {/* Sidebar */}
            <div className="w-64 bg-[#fdf8f1] p-4 flex flex-col border-r border-[#f3e8d6] hidden md:flex">
                <h2 className="text-xl font-bold mb-6 flex items-center gap-2 text-[#8b5e3c]">
                    <Bot className="text-[#c29b61]" /> ChatBotสูตรลับคาเฟ่
                </h2>

                {/* Upload area */}
                <div className="mb-4">
                    <label className={`flex items-center justify-center w-full p-4 border-2 border-dashed rounded-lg cursor-pointer transition ${uploadStatus === 'uploading' || uploadStatus === 'processing'
                        ? 'border-[#a8a29e] bg-[#f5f5f4] cursor-not-allowed'
                        : 'border-[#d6d3d1] hover:border-[#8b5e3c] hover:bg-[#fafaf9]'
                        }`}>
                        {uploadStatus === 'uploading' || uploadStatus === 'processing' ? (
                            <Loader2 size={20} className="mr-2 text-yellow-400 animate-spin" />
                        ) : uploadStatus === 'done' ? (
                            <CheckCircle2 size={20} className="mr-2 text-green-400" />
                        ) : (
                            <Upload size={20} className="mr-2 text-gray-400" />
                        )}
                        <span className="text-sm font-medium text-gray-300">
                            {uploadStatus === 'idle' ? 'Upload PDF/Docs' : uploadMsg}
                        </span>
                        <input
                            type="file"
                            className="hidden"
                            onChange={handleFileUpload}
                            accept=".pdf,.txt,.csv,.md"
                            disabled={uploadStatus === 'uploading' || uploadStatus === 'processing'}
                        />
                    </label>
                    {uploadStatus === 'error' && (
                        <p className="text-xs text-red-400 mt-1 text-center">{uploadMsg}</p>
                    )}
                </div>

                {/* Document list */}
                <div className="flex-1 overflow-y-auto">
                    <h3 className="text-xs uppercase text-gray-500 font-semibold mb-2">
                        Documents ({documents.length})
                    </h3>
                    {documents.length === 0 ? (
                        <p className="text-xs text-gray-600 text-center py-4">No documents yet.<br />Upload a file to get started.</p>
                    ) : (
                        documents.map(doc => (
                            <div
                                key={doc.doc_id}
                                className="flex items-center gap-2 p-2 rounded hover:bg-[#f3e8d6] cursor-pointer text-sm group"
                            >
                                <FileText size={16} className="text-[#c29b61] shrink-0" />
                                <span className="flex-1 truncate text-[#8a7b6e]" title={doc.filename}>
                                    {doc.filename}
                                    <span className="text-xs text-gray-500 block">{doc.chunks} chunks</span>
                                </span>
                                <button
                                    onClick={() => handleDelete(doc.doc_id, doc.filename)}
                                    className="opacity-0 group-hover:opacity-100 text-[#a8a29e] hover:text-[#b91c1c] transition"
                                    title="Delete document"
                                >
                                    <Trash2 size={14} />
                                </button>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col">
                {/* Topbar */}
                <header className="h-16 bg-white border-b border-[#f3e8d6] flex items-center justify-between px-6 shadow-sm z-10">
                    <h1 className="text-lg font-bold text-[#8b5e3c]">ChatBotสูตรลับคาเฟ่</h1>
                    <div className="flex bg-[#fdf8f1] rounded-lg p-1">
                        {['auto', 'rag', 'sql'].map(m => (
                            <button
                                key={m}
                                onClick={() => setMode(m)}
                                className={`px-4 py-1.5 text-sm font-medium rounded-md capitalize transition-colors ${mode === m ? 'bg-[#c29b61] text-white shadow' : 'text-[#a8a29e] hover:text-[#5c4033] hover:bg-[#f3e8d6]'
                                    }`}
                            >
                                {m}
                            </button>
                        ))}
                    </div>
                </header>

                {/* Chat Messages */}
                <main className="flex-1 overflow-y-auto p-6 space-y-6">
                    {messages.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-[#a8a29e]">
                            <Bot size={48} className="mb-4 text-[#d6d3d1]" />
                            <p className="text-lg">ถามอะไรฉันก็ได้เกี่ยวกับเอกสารหรือข้อมูลของคุณ!</p>
                            {documents.length > 0 && (
                                <p className="text-sm mt-2 text-green-500">{documents.length} document(s) ready for RAG queries.</p>
                            )}
                        </div>
                    ) : (
                        messages.map((msg, idx) => (
                            <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : ''}`}>
                                {msg.role === 'bot' && (
                                    <div className="w-8 h-8 rounded-full bg-[#8b5e3c] flex items-center justify-center shrink-0">
                                        <Bot size={16} className="text-white" />
                                    </div>
                                )}
                                <div className={`max-w-[75%] p-4 rounded-lg shadow-sm ${msg.role === 'user' ? 'bg-[#c29b61] text-white rounded-br-none' : 'bg-[#fffbeb] text-[#5c4033] border border-[#f3e8d6] rounded-bl-none'
                                    }`}>
                                    <div className="whitespace-pre-wrap leading-relaxed">{msg.text}</div>

                                    {/* Tool Trace & Citations */}
                                    {msg.role === 'bot' && (msg.tool_trace?.length || msg.citations?.length) ? (
                                        <div className="mt-4 pt-4 border-t border-gray-700 text-sm">
                                            {/* Sugar Graph for Barista AI */}
                                            {msg.tool_trace && msg.tool_trace.find(t => t.step === "Adding Sugar Stats") && (
                                                <div className="mb-4 p-4 bg-gray-900/80 rounded-xl border border-gray-700 shadow-inner">
                                                    <p className="text-xs font-bold text-[#c29b61] mb-3 uppercase tracking-widest flex items-center gap-2">
                                                        <span className="w-2 h-2 bg-[#c29b61] rounded-full animate-pulse"></span>
                                                        {msg.tool_trace.find(t => t.step === "Adding Sugar Stats")?.data?.label || "กราฟเปรียบเทียบข้อมูล"}
                                                    </p>
                                                    {(() => {
                                                        const stats = msg.tool_trace.find(t => t.step === "Adding Sugar Stats")?.data;
                                                        if (!stats || !stats.all_stats || stats.all_stats.length === 0) return null;

                                                        // Dynamic scaling
                                                        const values = stats.all_stats.map((s: any) => s.val);
                                                        const maxDataVal = Math.max(...values, 1);
                                                        const maxVal = maxDataVal * 1.2; // Add 20% headroom

                                                        const width = 300;
                                                        const height = 150;
                                                        const padding = 30;
                                                        const chartWidth = width - (padding * 2);
                                                        const chartHeight = height - (padding * 2);

                                                        const barWidth = (chartWidth / stats.all_stats.length) * 0.7;
                                                        const gap = (chartWidth / stats.all_stats.length) * 0.3;

                                                        return (
                                                            <div className="flex flex-col items-center">
                                                                <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} className="overflow-visible">
                                                                    {/* Grid Lines */}
                                                                    {[0, 0.5, 1].map(factor => {
                                                                        const v = factor * maxDataVal;
                                                                        const y = height - padding - (v / maxVal * chartHeight);
                                                                        return (
                                                                            <g key={factor}>
                                                                                <line
                                                                                    x1={padding} y1={y}
                                                                                    x2={width - padding} y2={y}
                                                                                    stroke="#374151" strokeWidth="0.5" strokeDasharray="3"
                                                                                />
                                                                                <text x={padding - 5} y={y + 3} textAnchor="end" fontSize="8" fill="#9ca3af">{v.toFixed(0)}</text>
                                                                            </g>
                                                                        );
                                                                    })}

                                                                    {/* Bars */}
                                                                    {stats.all_stats.map((p: any, i: number) => {
                                                                        const x = padding + (i * (chartWidth / stats.all_stats.length)) + (gap / 2);
                                                                        const barHeight = (p.val / maxVal * chartHeight);
                                                                        const y = height - padding - barHeight;

                                                                        return (
                                                                            <g key={i}>
                                                                                <rect
                                                                                    x={x} y={y}
                                                                                    width={barWidth} height={barHeight}
                                                                                    fill={p.name === stats.current ? "#8b5e3c" : "#c29b61"}
                                                                                    rx="2"
                                                                                    className="transition-all hover:fill-[#a67c52]"
                                                                                />
                                                                                {/* Value Label */}
                                                                                <text
                                                                                    x={x + barWidth / 2} y={y - 5}
                                                                                    textAnchor="middle" fontSize="7" fill="#8b5e3c" className="font-bold"
                                                                                >
                                                                                    {p.val}
                                                                                </text>
                                                                                {/* Name Label */}
                                                                                <text
                                                                                    x={x + barWidth / 2} y={height - padding + 12}
                                                                                    textAnchor="middle" fontSize="7" fill="#8a7b6e"
                                                                                    transform={`rotate(15, ${x + barWidth / 2}, ${height - padding + 12})`}
                                                                                    className="font-medium"
                                                                                >
                                                                                    {p.name.length > 10 ? p.name.substring(0, 8) + '..' : p.name}
                                                                                </text>
                                                                            </g>
                                                                        );
                                                                    })}
                                                                </svg>
                                                                <div className="pt-4 text-[10px] text-[#a8a29e] italic border-t border-[#e7e5e4] w-full mt-4">
                                                                    * {stats.label || "ข้อมูลเปรียบเทียบ"}
                                                                </div>
                                                            </div>
                                                        );
                                                    })()}
                                                </div>
                                            )}

                                            {msg.tool_trace && msg.tool_trace.length > 0 && (
                                                <div className="mb-2">
                                                    <p className="text-[#8a7b6e] font-semibold mb-1">การทำงานของ Agent 🔍</p>
                                                    <ul className="list-disc pl-5 text-[#a8a29e] space-y-1">
                                                        {msg.tool_trace.map((t, i) => (
                                                            <li key={i}>
                                                                {t.step}
                                                                {t.result && <span className="text-[#a8a29e] ml-1">({typeof t.result === 'string' ? t.result.substring(0, 50) + '...' : JSON.stringify(t.result)})</span>}
                                                                {t.query && <span className="text-[#8b5e3c] ml-1">[{t.query}]</span>}
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}
                                            {msg.citations && msg.citations.length > 0 && (
                                                <div>
                                                    <p className="text-[#8a7b6e] font-semibold mb-1">แหล่งอ้างอิง 📚</p>
                                                    <div className="flex flex-wrap gap-2">
                                                        {msg.citations.map((c, i) => (
                                                            <span key={i} className="bg-[#f5f5f4] px-2 py-1 rounded text-[10px] text-[#78716c] border border-[#e7e5e4]">
                                                                Doc: {c.doc_id.substring(0, 6)}... | Chunk: {c.chunk} | Score: {(c.score * 100).toFixed(1)}%
                                                            </span>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    ) : null}
                                </div>
                                {msg.role === 'user' && (
                                    <div className="w-8 h-8 rounded-full bg-[#d6d3d1] flex items-center justify-center shrink-0">
                                        <User size={16} className="text-[#78716c]" />
                                    </div>
                                )}
                            </div>
                        ))
                    )}
                    {loading && (
                        <div className="flex gap-4">
                            <div className="w-8 h-8 rounded-full bg-[#8b5e3c] flex items-center justify-center shrink-0">
                                <Bot size={16} className="text-white" />
                            </div>
                            <div className="p-4 bg-white rounded-lg border border-[#e7e5e4] animate-pulse">
                                <span>กำลังคิด...</span>
                            </div>
                        </div>
                    )}
                </main>

                {/* Input Area */}
                <footer className="p-4 bg-[#fdf8f1] border-t border-[#f3e8d6]">
                    <div className="max-w-4xl mx-auto flex items-end gap-2 bg-white rounded-xl border border-[#f3e8d6] p-2 focus-within:ring-2 ring-[#c29b61] focus-within:border-transparent transition-all">
                        <textarea
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={e => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    sendMessage();
                                }
                            }}
                            placeholder="พิมพ์ข้อความ... (Shift+Enter เพื่อขึ้นบรรทัดใหม่)"
                            className="flex-1 max-h-32 min-h-[44px] bg-transparent resize-none outline-none py-2 px-3 text-[#5c4033] placeholder-[#d1ccb9]"
                            rows={1}
                        />
                        <button
                            onClick={sendMessage}
                            disabled={loading || !input.trim()}
                            className="p-3 bg-[#c29b61] text-white rounded-lg hover:bg-[#a67c52] disabled:opacity-50 disabled:cursor-not-allowed transition-colors shrink-0 mb-0.5"
                        >
                            <Send size={18} />
                        </button>
                    </div>
                </footer>
            </div>
        </div>
    );
}

export default App;
