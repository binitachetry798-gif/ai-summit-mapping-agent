import { useState } from 'react';
import { searchContracts } from '../api';

const PORTALS = ['GeM', 'NSIC', 'SIDBI', 'KVIC', 'ONDC', 'TradeIndia', 'IndiaMart', 'CPPP', 'TReDS', 'ZED', 'SC/ST Hub', 'DC MSME', 'NIC Tenders'];

const typeColors = {
    contract: '#22c55e',
    scheme: '#3b82f6',
    marketplace: '#f59e0b',
    finance: '#8b5cf6',
    platform: '#06b6d4',
    tender: '#ef4444',
};

export default function Contracts() {
    const [form, setForm] = useState({ product_desc: '', location: '', state: '' });
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!form.product_desc.trim()) return;
        setLoading(true);
        setError('');
        try {
            const data = await searchContracts({ ...form, top_k: 12 });
            setResults(data);
        } catch (err) {
            setError('Search failed. Make sure the backend is running.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="contracts-page">
            <div className="contracts-hero">
                <h1>🔍 Live MSME Contract Search</h1>
                <p>Search across <strong>13 Indian portals</strong> — GeM, NSIC, SIDBI, ONDC, CPPP & more. Sorted by relevance to your business.</p>
                <div className="portal-badges">
                    {PORTALS.map(p => <span key={p} className="portal-badge">{p}</span>)}
                </div>
            </div>

            <div className="contracts-search-box">
                <form onSubmit={handleSearch} className="search-form">
                    <div className="search-row">
                        <div className="field-group">
                            <label>Product / Service Description *</label>
                            <input
                                type="text"
                                placeholder="e.g. handmade leather shoes, organic rice, handloom sarees"
                                value={form.product_desc}
                                onChange={e => setForm({ ...form, product_desc: e.target.value })}
                                required
                            />
                        </div>
                    </div>
                    <div className="search-row two-col">
                        <div className="field-group">
                            <label>City / District</label>
                            <input
                                type="text"
                                placeholder="e.g. Agra, Surat, Mysuru"
                                value={form.location}
                                onChange={e => setForm({ ...form, location: e.target.value })}
                            />
                        </div>
                        <div className="field-group">
                            <label>State</label>
                            <input
                                type="text"
                                placeholder="e.g. Uttar Pradesh, Gujarat"
                                value={form.state}
                                onChange={e => setForm({ ...form, state: e.target.value })}
                            />
                        </div>
                    </div>
                    <button type="submit" className="search-btn" disabled={loading}>
                        {loading ? '🔄 Searching 13 portals...' : '🔍 Find Opportunities'}
                    </button>
                </form>
            </div>

            {error && <div className="error-banner">⚠️ {error}</div>}

            {results && (
                <div className="contracts-results">
                    <div className="results-header">
                        <div className="results-stats">
                            <span className="stat">✅ {results.results.length} results shown</span>
                            <span className="stat">🏛️ {results.total_found} total found</span>
                            <span className="stat">📡 {results.live_count} live tenders</span>
                            <span className="stat">📋 {results.curated_count} curated schemes</span>
                        </div>
                    </div>

                    <div className="contracts-grid">
                        {results.results.map((opp, i) => (
                            <div key={opp.id || i} className="contract-card">
                                <div className="card-header">
                                    <span
                                        className="type-badge"
                                        style={{ background: typeColors[opp.type] || '#6b7280' }}
                                    >
                                        {opp.type?.toUpperCase()}
                                    </span>
                                    <span className="match-score">
                                        {Math.round((opp.match_score || 0) * 100)}% match
                                    </span>
                                </div>
                                <h3 className="card-title">{opp.title}</h3>
                                <div className="card-portal">
                                    <a href={opp.portal_url} target="_blank" rel="noopener noreferrer">
                                        🏛️ {opp.portal}
                                    </a>
                                </div>
                                <p className="card-desc">{opp.description}</p>
                                <div className="card-meta">
                                    <span>💰 {opp.value_range}</span>
                                    <span>⏳ {opp.deadline}</span>
                                </div>
                                <div className="card-eligibility">
                                    <strong>Eligibility:</strong> {opp.eligibility}
                                </div>
                                <a
                                    href={opp.link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="apply-btn"
                                >
                                    Apply / View →
                                </a>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {!results && !loading && (
                <div className="empty-state">
                    <div className="empty-icon">🏭</div>
                    <h3>Search for contracts tailored to your MSME</h3>
                    <p>Enter your product description above to find relevant government tenders, marketplace opportunities, and financial schemes.</p>
                </div>
            )}

            <style>{`
        .contracts-page { max-width: 1100px; margin: 0 auto; padding: 2rem 1rem; }
        .contracts-hero { text-align: center; margin-bottom: 2rem; }
        .contracts-hero h1 { font-size: 2rem; color: #1e293b; margin-bottom: 0.5rem; }
        .contracts-hero p { color: #64748b; font-size: 1.05rem; margin-bottom: 1rem; }
        .portal-badges { display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; }
        .portal-badge { background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 20px; padding: 0.25rem 0.75rem; font-size: 0.78rem; color: #475569; font-weight: 500; }
        .contracts-search-box { background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 24px rgba(0,0,0,0.08); margin-bottom: 2rem; }
        .search-form { display: flex; flex-direction: column; gap: 1rem; }
        .search-row { display: flex; gap: 1rem; }
        .two-col { display: grid; grid-template-columns: 1fr 1fr; }
        .field-group { flex: 1; display: flex; flex-direction: column; gap: 0.4rem; }
        .field-group label { font-size: 0.85rem; font-weight: 600; color: #374151; }
        .field-group input { border: 1.5px solid #e2e8f0; border-radius: 10px; padding: 0.65rem 1rem; font-size: 0.95rem; outline: none; transition: border-color 0.2s; }
        .field-group input:focus { border-color: #6366f1; }
        .search-btn { background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; border: none; border-radius: 12px; padding: 0.85rem 2rem; font-size: 1rem; font-weight: 600; cursor: pointer; transition: opacity 0.2s; }
        .search-btn:disabled { opacity: 0.7; cursor: not-allowed; }
        .error-banner { background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; }
        .results-header { margin-bottom: 1.5rem; }
        .results-stats { display: flex; gap: 1rem; flex-wrap: wrap; }
        .stat { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.4rem 0.8rem; font-size: 0.85rem; color: #475569; font-weight: 500; }
        .contracts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem; }
        .contract-card { background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 12px rgba(0,0,0,0.07); border: 1px solid #f1f5f9; display: flex; flex-direction: column; gap: 0.75rem; transition: transform 0.2s, box-shadow 0.2s; }
        .contract-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
        .card-header { display: flex; justify-content: space-between; align-items: center; }
        .type-badge { color: white; border-radius: 6px; padding: 0.2rem 0.6rem; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.05em; }
        .match-score { background: #f0fdf4; color: #16a34a; border-radius: 6px; padding: 0.2rem 0.6rem; font-size: 0.8rem; font-weight: 700; }
        .card-title { font-size: 1rem; font-weight: 700; color: #1e293b; line-height: 1.4; }
        .card-portal a { color: #6366f1; font-size: 0.85rem; text-decoration: none; font-weight: 600; }
        .card-desc { color: #64748b; font-size: 0.88rem; line-height: 1.5; }
        .card-meta { display: flex; gap: 1rem; font-size: 0.82rem; color: #475569; }
        .card-eligibility { font-size: 0.82rem; color: #374151; background: #f8fafc; border-radius: 8px; padding: 0.5rem 0.75rem; }
        .apply-btn { background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; border-radius: 10px; padding: 0.6rem 1.2rem; text-align: center; text-decoration: none; font-weight: 600; font-size: 0.9rem; margin-top: auto; transition: opacity 0.2s; }
        .apply-btn:hover { opacity: 0.9; }
        .empty-state { text-align: center; padding: 4rem 2rem; color: #94a3b8; }
        .empty-icon { font-size: 4rem; margin-bottom: 1rem; }
        .empty-state h3 { font-size: 1.3rem; color: #475569; margin-bottom: 0.5rem; }
        @media (max-width: 600px) { .two-col { grid-template-columns: 1fr; } .contracts-grid { grid-template-columns: 1fr; } }
      `}</style>
        </div>
    );
}
