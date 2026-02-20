import { useState } from 'react';
import MatchCard from '../components/MatchCard';
import { matchSNP } from '../api';

export default function Matches() {
    const [query, setQuery] = useState({ product_desc: '', location: '', capacity: '' });
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query.product_desc.trim()) {
            setError('Please enter a product description.');
            return;
        }
        setError('');
        setLoading(true);
        setResults(null);
        try {
            const data = await matchSNP({
                product_desc: query.product_desc,
                location: query.location || undefined,
                capacity: query.capacity ? parseInt(query.capacity) : undefined,
                top_k: 3,
            });
            setResults(data);
        } catch (err) {
            setError(err?.response?.data?.detail || 'Matching failed. Ensure the backend is running.');
        } finally {
            setLoading(false);
        }
    };

    const DEMOS = [
        'Handmade leather chappal from Agra',
        'Organic spices and masala from Rajasthan',
        'Hand-woven silk sarees from Varanasi',
        'Brass home decor items from Moradabad',
        'Ayurvedic herbal skincare products',
        'Auto ancillary machined components',
    ];

    return (
        <div className="container">
            <div className="page-title animate-fadeup">SNP Match Engine <span className="gradient-text">🔗 Vector AI</span></div>
            <div className="page-subtitle animate-fadeup delay-1">
                Enter your product profile to find the best-matched Seller Network Participants on ONDC.
            </div>

            {/* Search Form */}
            <div className="card animate-fadeup delay-1" style={{ padding: '28px', marginBottom: '32px' }}>
                <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '16px' }}>🎯 Find Your SNP Match</h3>
                <form onSubmit={handleSearch} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <div className="form-group">
                        <label className="form-label">Product Description *</label>
                        <input
                            className="form-input"
                            placeholder="e.g. Handmade leather chappal, 500 units/month, Agra"
                            value={query.product_desc}
                            onChange={e => setQuery(q => ({ ...q, product_desc: e.target.value }))}
                        />
                    </div>
                    <div className="form-row">
                        <div className="form-group">
                            <label className="form-label">Location (optional)</label>
                            <input className="form-input" placeholder="Agra, Uttar Pradesh" value={query.location} onChange={e => setQuery(q => ({ ...q, location: e.target.value }))} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Annual Capacity (units)</label>
                            <input className="form-input" type="number" placeholder="500" value={query.capacity} onChange={e => setQuery(q => ({ ...q, capacity: e.target.value }))} />
                        </div>
                    </div>
                    {error && <div className="alert alert-error">⚠️ {error}</div>}
                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? <><div className="spinner" style={{ width: 16, height: 16 }} /> Finding matches…</> : '🔍 Find Best SNP Matches'}
                    </button>
                </form>

                {/* Demo Queries */}
                <div style={{ marginTop: '20px', borderTop: '1px solid var(--color-border)', paddingTop: '16px' }}>
                    <div className="field-key" style={{ marginBottom: '10px' }}>Try these examples:</div>
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                        {DEMOS.map(d => (
                            <button key={d} className="btn btn-secondary btn-sm" onClick={() => setQuery(q => ({ ...q, product_desc: d }))}>
                                {d.slice(0, 30)}…
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Results */}
            {loading && (
                <div style={{ textAlign: 'center', padding: '48px 0', color: 'var(--color-text-muted)' }}>
                    <div className="spinner" style={{ width: 36, height: 36, margin: '0 auto 16px' }} />
                    <div>Running vector similarity search across {8} SNP profiles…</div>
                </div>
            )}

            {results && (
                <>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                        <div>
                            <div style={{ fontSize: '18px', fontWeight: 700 }}>
                                Top {results.matches.length} SNP Matches
                            </div>
                            <div style={{ fontSize: '13px', color: 'var(--color-text-muted)' }}>
                                Evaluated {results.total_snps_evaluated} SNPs · Query: "{results.query}"
                            </div>
                        </div>
                        <span className="badge badge-green">✓ Search Complete</span>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '20px' }}>
                        {results.matches.map((match, i) => (
                            <MatchCard key={match.snp_id} match={match} rank={i + 1} />
                        ))}
                    </div>

                    {/* Explanation */}
                    <div className="card animate-fadeup" style={{ padding: '24px', marginTop: '32px' }}>
                        <h3 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px' }}>📊 How Match Scores Are Calculated</h3>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                            <div>
                                <div style={{ fontSize: '13px', color: 'var(--color-text-muted)', lineHeight: 1.6 }}>
                                    <strong style={{ color: 'var(--color-text)' }}>Semantic Similarity (Cosine)</strong><br />
                                    Your product description is encoded into a 384-dimensional vector using <code style={{ color: 'var(--color-saffron)' }}>all-MiniLM-L6-v2</code>.
                                    Cosine similarity is computed against each SNP's domain vector.
                                </div>
                            </div>
                            <div>
                                <div style={{ fontSize: '13px', color: 'var(--color-text-muted)', lineHeight: 1.6 }}>
                                    <strong style={{ color: 'var(--color-text)' }}>Weighted Final Score</strong><br />
                                    Final Score = Cosine Similarity × Operational Capacity. This ensures high-similarity but overloaded SNPs rank below available ones.
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
