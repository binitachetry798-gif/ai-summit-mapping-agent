import { Link } from 'react-router-dom';

const STATS = [
    { value: '4 min', label: 'Avg. Registration Time', color: 'var(--color-saffron)' },
    { value: '22', label: 'Indian Languages Supported', color: 'var(--color-green-light)' },
    { value: '8+', label: 'ONDC SNP Partners', color: 'var(--color-indigo-light)' },
    { value: '92%', label: 'Avg. Match Accuracy', color: 'var(--color-saffron-light)' },
];

const FEATURES = [
    {
        icon: '🎙️',
        title: 'Voice-First Onboarding',
        desc: 'MSEs register by speaking in their native language. Bhashini ASR + NMT handles 22 Indian languages including Hindi, Marathi, Tamil, Telugu, and Odia.',
        color: 'var(--color-saffron)',
        link: '/register',
        badge: 'Bhashini ULCA',
    },
    {
        icon: '🤖',
        title: 'AI Product Classifier',
        desc: 'Google Gemini zero-shot classifies raw product descriptions → ONDC taxonomy + HSN code in under 1 second. Works even for Hinglish inputs.',
        color: 'var(--color-indigo-light)',
        link: '/register',
        badge: 'Gemini AI',
    },
    {
        icon: '🔗',
        title: 'Intelligent SNP Matcher',
        desc: 'Vector embeddings (all-MiniLM-L6-v2) + cosine similarity match each MSE to the most compatible Seller Network Participants by domain + operational capacity.',
        color: 'var(--color-green-light)',
        link: '/matches',
        badge: 'ChromaDB',
    },
    {
        icon: '🔍',
        title: 'Document Verification',
        desc: 'OCR-powered scanning of Udyam Certificates and GSTIN documents. Extracts Udyam Number, Enterprise Name, GSTIN, and PAN — eliminating manual NSIC review.',
        color: 'var(--color-saffron-light)',
        link: '/verify',
        badge: 'Tesseract OCR',
    },
];

export default function Home() {
    return (
        <div>
            {/* Hero */}
            <div className="hero">
                <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginBottom: '20px', flexWrap: 'wrap' }}>
                    <span className="badge badge-saffron">🇮🇳 MSME TEAM Initiative</span>
                    <span className="badge badge-green">ONDC-Ready</span>
                    <span className="badge badge-indigo">DPI-Compliant</span>
                </div>
                <h1 className="hero-title">
                    MSE <span className="gradient-text">Agent Mapping</span><br />Tool
                </h1>
                <p className="hero-desc">
                    Zero-entry onboarding for Micro & Small Enterprises — from 4 days to <strong>4 minutes</strong>.
                    Voice-first, AI-powered, and built on India's Digital Public Infrastructure.
                </p>

                <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
                    <Link to="/register" className="btn btn-primary btn-lg">
                        🚀 Register an MSE
                    </Link>
                    <Link to="/matches" className="btn btn-secondary btn-lg">
                        🔗 Find SNP Match
                    </Link>
                </div>
            </div>

            <div className="container">
                {/* Stats */}
                <div className="stats-row animate-fadeup">
                    {STATS.map(({ value, label, color }) => (
                        <div key={label} className="stat-card">
                            <div className="stat-value" style={{ color }}>{value}</div>
                            <div className="stat-label">{label}</div>
                        </div>
                    ))}
                </div>

                {/* Problem Statement Banner */}
                <div className="card card-glow-saffron animate-fadeup delay-1" style={{ padding: '28px', marginBottom: '40px' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                        <div>
                            <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '12px', color: 'var(--color-saffron)' }}>
                                🔴 The Problem
                            </h2>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                {[
                                    'Manual data entry takes 3–4 business days',
                                    'Claim verification by NSIC is error-prone',
                                    'Rural MSEs can\'t navigate English-only forms',
                                    'No automated mapping to ONDC taxonomy',
                                ].map(p => (
                                    <div key={p} style={{ display: 'flex', gap: '8px', fontSize: '14px', color: 'var(--color-text-muted)' }}>
                                        <span style={{ color: '#f87171' }}>✕</span> {p}
                                    </div>
                                ))}
                            </div>
                        </div>
                        <div>
                            <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '12px', color: 'var(--color-green-light)' }}>
                                🟢 Our Solution
                            </h2>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                {[
                                    'Voice registration → 4 minutes, any Indian language',
                                    'AI auto-verifies Udyam certificates via OCR',
                                    'Zero-shot AI maps products to ONDC taxonomy',
                                    'Vector DB instantly matches MSE → best SNP',
                                ].map(s => (
                                    <div key={s} style={{ display: 'flex', gap: '8px', fontSize: '14px', color: 'var(--color-text-muted)' }}>
                                        <span style={{ color: 'var(--color-green-light)' }}>✓</span> {s}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Feature Cards */}
                <h2 style={{ fontSize: '22px', fontWeight: 800, marginBottom: '20px' }}>Core Capabilities</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px', marginBottom: '48px' }}>
                    {FEATURES.map(({ icon, title, desc, color, link, badge }) => (
                        <Link key={title} to={link} style={{ textDecoration: 'none' }}>
                            <div className="card animate-fadeup" style={{ padding: '24px', height: '100%', cursor: 'pointer' }}>
                                <div style={{ fontSize: '36px', marginBottom: '12px' }}>{icon}</div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                                    <h3 style={{ fontSize: '16px', fontWeight: 700 }}>{title}</h3>
                                </div>
                                <span className="badge badge-muted" style={{ marginBottom: '12px', display: 'inline-flex' }}>{badge}</span>
                                <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', lineHeight: 1.6 }}>{desc}</p>
                            </div>
                        </Link>
                    ))}
                </div>

                {/* Tech Stack */}
                <div className="card animate-fadeup" style={{ padding: '28px', marginBottom: '40px' }}>
                    <h2 style={{ fontSize: '18px', fontWeight: 800, marginBottom: '20px' }}>🏗️ Architecture Stack</h2>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                        {[
                            { layer: 'Voice Layer', tech: 'Bhashini ULCA API', detail: 'ASR + NMT Pipeline', icon: '🎙️' },
                            { layer: 'AI/ML Layer', tech: 'Gemini + SentenceTransformers', detail: 'Classification + Embeddings', icon: '🧠' },
                            { layer: 'Vector DB', tech: 'ChromaDB', detail: 'Cosine Similarity Search', icon: '🔢' },
                            { layer: 'Backend', tech: 'FastAPI + Python', detail: 'REST API • Async', icon: '⚡' },
                            { layer: 'Database', tech: 'PostgreSQL / SQLite', detail: 'MSE + SNP Profiles', icon: '🗄️' },
                            { layer: 'Frontend', tech: 'React + Vite', detail: 'Mobile-first Dashboard', icon: '🖥️' },
                        ].map(({ layer, tech, detail, icon }) => (
                            <div key={layer} className="field-item" style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                                <span style={{ fontSize: '24px' }}>{icon}</span>
                                <div>
                                    <div className="field-key">{layer}</div>
                                    <div style={{ fontWeight: 700, fontSize: '14px' }}>{tech}</div>
                                    <div style={{ fontSize: '12px', color: 'var(--color-text-dim)' }}>{detail}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* CTA */}
                <div style={{ textAlign: 'center', padding: '32px 0 16px' }}>
                    <Link to="/register" className="btn btn-primary btn-lg">
                        🇮🇳 Start Onboarding an MSE →
                    </Link>
                </div>
            </div>
        </div>
    );
}
