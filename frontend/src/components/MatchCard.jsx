export default function MatchCard({ match, rank }) {
    const pct = Math.round(match.final_score * 100);
    const simPct = Math.round(match.similarity_score * 100);
    const capPct = Math.round(match.operational_capacity * 100);

    const rankColors = ['var(--color-saffron)', 'var(--color-green-light)', 'var(--color-indigo-light)'];
    const rankColor = rankColors[rank - 1] || 'var(--color-text-muted)';
    const rankLabels = ['🥇 Best Match', '🥈 Runner-up', '🥉 Third Pick'];
    const rankLabel = rankLabels[rank - 1] || `#${rank}`;

    return (
        <div className="card animate-fadeup" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
                        <span style={{ fontSize: '22px', fontWeight: 900, color: rankColor }}>#{rank}</span>
                        <h3 style={{ fontSize: '17px', fontWeight: 700 }}>{match.name}</h3>
                    </div>
                    <span className="badge badge-muted">{rankLabel}</span>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '32px', fontWeight: 900, color: rankColor }}>{pct}%</div>
                    <div style={{ fontSize: '11px', color: 'var(--color-text-dim)' }}>Match Score</div>
                </div>
            </div>

            {/* Score Bar */}
            <div style={{ marginBottom: '20px' }}>
                <div className="score-bar-track">
                    <div className="score-bar-fill" style={{ width: `${pct}%`, background: `linear-gradient(90deg, ${rankColor}, var(--color-saffron))` }} />
                </div>
            </div>

            {/* Stats Row */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                <div className="field-item">
                    <div className="field-key">Semantic Similarity</div>
                    <div className="field-val">{simPct}%</div>
                </div>
                <div className="field-item">
                    <div className="field-key">Operational Capacity</div>
                    <div className="field-val">{capPct}%</div>
                </div>
            </div>

            {/* Domain */}
            <div style={{ marginBottom: '16px' }}>
                <div className="field-key" style={{ marginBottom: '6px' }}>Domain</div>
                <div style={{ fontSize: '13px', color: 'var(--color-text-muted)', lineHeight: 1.5, fontStyle: 'italic' }}>
                    {match.domain}
                </div>
            </div>

            {/* Sectors */}
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '12px' }}>
                {match.sectors.map((s) => (
                    <span key={s} className="badge badge-indigo">{s}</span>
                ))}
            </div>

            {/* Regions */}
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '16px' }}>
                {match.regions.map((r) => (
                    <span key={r} className="badge badge-muted">📍 {r}</span>
                ))}
            </div>

            {/* Footer */}
            <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: '14px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ fontSize: '12px', color: 'var(--color-text-dim)' }}>
                    ONDC ID: <span style={{ fontFamily: 'monospace', color: 'var(--color-text-muted)' }}>{match.ondc_id}</span>
                </div>
                <a href={`mailto:${match.contact}`} className="btn btn-sm btn-secondary">
                    📧 Contact SNP
                </a>
            </div>
        </div>
    );
}
