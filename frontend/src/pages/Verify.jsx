import { useState, useRef } from 'react';
import { verifyDocument } from '../api';

const ACCEPTED_TYPES = ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff', 'image/bmp'];
const ACCEPTED_EXT = '.pdf,.jpg,.jpeg,.png,.tiff,.bmp';

const STATUS_CONFIG = {
    verified: { color: 'var(--color-green-light)', icon: '✅', label: 'Verified' },
    partial: { color: 'var(--color-saffron)', icon: '⚠️', label: 'Partially Verified' },
    not_verified: { color: '#f87171', icon: '❌', label: 'Not Verified' },
    verified_demo: { color: 'var(--color-indigo-light)', icon: '🧪', label: 'Demo Result' },
    unreadable: { color: '#f87171', icon: '❌', label: 'Unreadable' },
    error: { color: '#f87171', icon: '❌', label: 'Error' },
};

const DOC_LABELS = {
    udyam_certificate: 'Udyam Registration Certificate',
    gst_certificate: 'GST Certificate',
    pan_card: 'PAN Card',
    unknown_document: 'Unknown Document',
};

const FIELD_LABELS = {
    udyam_number: 'Udyam Number',
    gstin: 'GSTIN',
    pan: 'PAN Number',
    enterprise_name: 'Enterprise Name',
    owner_name: 'Owner Name',
    registration_date: 'Registration Date',
    nic_activity_code: 'NIC Activity Code',
};

export default function Verify() {
    const [file, setFile] = useState(null);
    const [drag, setDrag] = useState(false);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');
    const inputRef = useRef();

    const handleFile = (f) => {
        if (!f) return;
        if (!ACCEPTED_TYPES.includes(f.type)) {
            setError('Unsupported file type. Upload PDF, JPG, or PNG.');
            return;
        }
        setFile(f);
        setResult(null);
        setError('');
    };

    const handleVerify = async () => {
        if (!file) return;
        setLoading(true);
        setError('');
        try {
            const data = await verifyDocument(file);
            setResult(data);
        } catch (err) {
            setError(err?.response?.data?.detail || 'Verification failed. Ensure the backend is running.');
        } finally {
            setLoading(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDrag(false);
        const f = e.dataTransfer.files[0];
        if (f) handleFile(f);
    };

    const statusConf = result ? STATUS_CONFIG[result.verification_status] || STATUS_CONFIG.error : null;

    return (
        <div className="container" style={{ maxWidth: '860px' }}>
            <div className="page-title animate-fadeup">Document Verification <span className="gradient-text">🔍 OCR AI</span></div>
            <div className="page-subtitle animate-fadeup delay-1">
                Upload your Udyam Registration Certificate or GST certificate — AI extracts and verifies fields instantly.
            </div>

            {/* Upload Zone */}
            <div className="card animate-fadeup delay-1" style={{ padding: '28px', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '16px' }}>📄 Upload Document</h3>

                <div
                    className={`drop-zone ${drag ? 'drag-over' : ''}`}
                    onClick={() => inputRef.current?.click()}
                    onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
                    onDragLeave={() => setDrag(false)}
                    onDrop={handleDrop}
                >
                    <div className="drop-zone-icon">{file ? '📎' : '☁️'}</div>
                    {file ? (
                        <>
                            <div style={{ fontWeight: 700, marginBottom: '4px' }}>{file.name}</div>
                            <div style={{ fontSize: '13px', color: 'var(--color-text-muted)' }}>
                                {(file.size / 1024).toFixed(1)} KB · {file.type}
                            </div>
                        </>
                    ) : (
                        <>
                            <div style={{ fontWeight: 700, marginBottom: '8px' }}>Drag & drop or click to upload</div>
                            <div style={{ fontSize: '13px', color: 'var(--color-text-muted)' }}>Supports PDF, JPG, PNG, TIFF · Max 10MB</div>
                        </>
                    )}
                </div>

                <input
                    ref={inputRef}
                    type="file"
                    accept={ACCEPTED_EXT}
                    style={{ display: 'none' }}
                    onChange={(e) => handleFile(e.target.files[0])}
                />

                {error && <div className="alert alert-error" style={{ marginTop: '12px' }}>⚠️ {error}</div>}

                <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
                    <button
                        className="btn btn-primary"
                        onClick={handleVerify}
                        disabled={!file || loading}
                        style={{ flex: 1 }}
                    >
                        {loading
                            ? <><div className="spinner" style={{ width: 16, height: 16 }} /> Scanning with OCR…</>
                            : '🔍 Verify Document'}
                    </button>
                    {file && (
                        <button className="btn btn-secondary" onClick={() => { setFile(null); setResult(null); }}>
                            ✕ Clear
                        </button>
                    )}
                </div>
            </div>

            {/* Result */}
            {result && (
                <div className="card animate-fadeup" style={{ padding: '28px', borderColor: statusConf.color + '40' }}>
                    {/* Header */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
                        <div>
                            <div style={{ fontSize: '20px', fontWeight: 800, marginBottom: '6px' }}>
                                {statusConf.icon} {statusConf.label}
                            </div>
                            <div className="badge badge-muted">{DOC_LABELS[result.document_type] || result.document_type}</div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                            <div style={{ fontSize: '36px', fontWeight: 900, color: statusConf.color }}>
                                {Math.round(result.confidence * 100)}%
                            </div>
                            <div style={{ fontSize: '11px', color: 'var(--color-text-dim)' }}>Confidence</div>
                        </div>
                    </div>

                    {/* Confidence Bar */}
                    <div style={{ marginBottom: '24px' }}>
                        <div className="score-bar-track">
                            <div className="score-bar-fill" style={{ width: `${Math.round(result.confidence * 100)}%`, background: `linear-gradient(90deg, ${statusConf.color}, var(--color-saffron))` }} />
                        </div>
                    </div>

                    {/* Extracted Fields */}
                    {Object.keys(result.extracted_fields || {}).length > 0 ? (
                        <>
                            <h4 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '14px' }}>📋 Extracted Fields</h4>
                            <div className="fields-grid" style={{ marginBottom: '20px' }}>
                                {Object.entries(result.extracted_fields).map(([k, v]) => (
                                    <div key={k} className="field-item">
                                        <div className="field-key">{FIELD_LABELS[k] || k}</div>
                                        <div className="field-val" style={{ fontFamily: k.includes('number') || k === 'gstin' || k === 'pan' ? 'monospace' : 'inherit', fontSize: '14px', color: 'var(--color-saffron)' }}>
                                            {v}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </>
                    ) : (
                        <div className="alert alert-warning" style={{ marginBottom: '16px' }}>
                            No structured fields could be extracted. The document may be low resolution or handwritten.
                        </div>
                    )}

                    {/* Raw Text Preview */}
                    {result.raw_text_preview && (
                        <div>
                            <h4 style={{ fontSize: '13px', fontWeight: 700, marginBottom: '8px', color: 'var(--color-text-muted)' }}>🔤 OCR Raw Text Preview</h4>
                            <pre style={{
                                background: 'var(--color-surface2)', borderRadius: 'var(--radius-md)',
                                padding: '14px', fontSize: '12px', color: 'var(--color-text-muted)',
                                overflowX: 'auto', whiteSpace: 'pre-wrap', border: '1px solid var(--color-border)'
                            }}>
                                {result.raw_text_preview}
                            </pre>
                        </div>
                    )}
                </div>
            )}

            {/* Info Panel */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '24px' }}>
                {[
                    { icon: '📜', title: 'Udyam Certificate', desc: 'Extracts Udyam Number, Enterprise Name, NIC Code, Owner Name, and Registration Date.' },
                    { icon: '🧾', title: 'GST Certificate', desc: 'Extracts GSTIN, registered business name, and PAN linkage for verification.' },
                ].map(({ icon, title, desc }) => (
                    <div key={title} className="card animate-fadeup" style={{ padding: '20px' }}>
                        <div style={{ fontSize: '28px', marginBottom: '8px' }}>{icon}</div>
                        <div style={{ fontWeight: 700, marginBottom: '6px' }}>{title}</div>
                        <div style={{ fontSize: '13px', color: 'var(--color-text-muted)', lineHeight: 1.5 }}>{desc}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}
