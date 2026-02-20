import { useState } from 'react';
import VoiceInput from '../components/VoiceInput';
import { classifyProduct, onboardMSE } from '../api';

const STATES = [
    'Andhra Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Delhi', 'Goa', 'Gujarat',
    'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh',
    'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
    'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh',
    'Uttarakhand', 'West Bengal'
];

const INITIAL_FORM = {
    business_name: '', owner_name: '', phone: '',
    location: '', state: '', product_description: '',
    annual_capacity: '', udyam_number: '', preferred_language: 'hi'
};

export default function Register() {
    const [form, setForm] = useState(INITIAL_FORM);
    const [classify, setClassify] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [classLoading, setClassLoading] = useState(false);
    const [error, setError] = useState('');
    const [step, setStep] = useState(1); // 1=form, 2=preview, 3=done

    const update = (field, val) => setForm(f => ({ ...f, [field]: val }));

    const handleVoiceResult = (translated) => {
        update('product_description', translated);
        // Auto-classify
        handleClassify(translated);
    };

    const handleClassify = async (desc = form.product_description) => {
        if (!desc?.trim()) return;
        setClassLoading(true);
        try {
            const data = await classifyProduct(desc);
            setClassify(data);
        } catch {
            // silent — classifier is optional
        } finally {
            setClassLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!form.business_name || !form.owner_name || !form.location || !form.state || !form.product_description) {
            setError('Please fill in all required fields.');
            return;
        }
        setError('');
        setLoading(true);
        try {
            const payload = { ...form, annual_capacity: form.annual_capacity ? parseInt(form.annual_capacity) : null };
            const data = await onboardMSE(payload);
            setResult(data);
            setStep(3);
        } catch (err) {
            setError(err?.response?.data?.detail || 'Onboarding failed. Please check the backend is running.');
        } finally {
            setLoading(false);
        }
    };

    if (step === 3 && result) {
        return <SuccessView result={result} onNew={() => { setForm(INITIAL_FORM); setClassify(null); setResult(null); setStep(1); }} />;
    }

    return (
        <div className="container">
            <div className="page-title animate-fadeup">Register Your MSE <span className="gradient-text">⚡ AI-Powered</span></div>
            <div className="page-subtitle animate-fadeup delay-1">
                Speak your product details in your language — AI handles the rest in under 4 minutes.
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: '32px', alignItems: 'start' }}>
                {/* Main Form */}
                <form onSubmit={handleSubmit}>
                    {/* Step 1: Voice */}
                    <div className="card animate-fadeup delay-1" style={{ padding: '28px', marginBottom: '24px' }}>
                        <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '4px' }}>
                            🎙️ Step 1 — Voice Input <span className="badge badge-saffron">Bhashini</span>
                        </h2>
                        <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', marginBottom: '16px' }}>
                            Select your language and describe your product verbally.
                        </p>
                        <VoiceInput onResult={handleVoiceResult} onLoading={setClassLoading} />
                    </div>

                    {/* Step 2: Product Details */}
                    <div className="card animate-fadeup delay-2" style={{ padding: '28px', marginBottom: '24px' }}>
                        <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>📦 Step 2 — Product Details</h2>
                        <div className="form-group">
                            <label className="form-label">Product Description *</label>
                            <textarea
                                className="form-textarea"
                                placeholder="e.g. Handmade leather chappal from Agra, 500 units per month"
                                value={form.product_description}
                                onChange={e => { update('product_description', e.target.value); setClassify(null); }}
                                required
                            />
                            <button
                                type="button"
                                className="btn btn-secondary btn-sm"
                                style={{ alignSelf: 'flex-start', marginTop: '6px' }}
                                onClick={() => handleClassify()}
                                disabled={classLoading || !form.product_description}
                            >
                                {classLoading ? <><div className="spinner" style={{ width: 12, height: 12 }} /> Classifying…</> : '🤖 Auto-Classify (AI)'}
                            </button>
                        </div>
                    </div>

                    {/* Step 3: Business Details */}
                    <div className="card animate-fadeup delay-2" style={{ padding: '28px', marginBottom: '24px' }}>
                        <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>🏢 Step 3 — Business Details</h2>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            <div className="form-row">
                                <div className="form-group">
                                    <label className="form-label">Business Name *</label>
                                    <input className="form-input" placeholder="Agra Leather Works" value={form.business_name} onChange={e => update('business_name', e.target.value)} required />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Owner Name *</label>
                                    <input className="form-input" placeholder="Ramesh Kumar" value={form.owner_name} onChange={e => update('owner_name', e.target.value)} required />
                                </div>
                            </div>
                            <div className="form-row">
                                <div className="form-group">
                                    <label className="form-label">City / Location *</label>
                                    <input className="form-input" placeholder="Agra" value={form.location} onChange={e => update('location', e.target.value)} required />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">State *</label>
                                    <select className="form-select" value={form.state} onChange={e => update('state', e.target.value)} required>
                                        <option value="">Select State</option>
                                        {STATES.map(s => <option key={s} value={s}>{s}</option>)}
                                    </select>
                                </div>
                            </div>
                            <div className="form-row">
                                <div className="form-group">
                                    <label className="form-label">Phone</label>
                                    <input className="form-input" placeholder="+91-9876543210" value={form.phone} onChange={e => update('phone', e.target.value)} />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Annual Capacity (units)</label>
                                    <input className="form-input" type="number" placeholder="500" value={form.annual_capacity} onChange={e => update('annual_capacity', e.target.value)} />
                                </div>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Udyam Number (optional)</label>
                                <input className="form-input" placeholder="UDYAM-UP-01-0001234" value={form.udyam_number} onChange={e => update('udyam_number', e.target.value)} />
                            </div>
                        </div>
                    </div>

                    {error && <div className="alert alert-error" style={{ marginBottom: '16px' }}>⚠️ {error}</div>}

                    <button type="submit" className="btn btn-primary btn-lg" disabled={loading} style={{ width: '100%' }}>
                        {loading ? <><div className="spinner" style={{ width: 18, height: 18 }} /> Registering with AI…</> : '🚀 Submit & Get SNP Match'}
                    </button>
                </form>

                {/* Side Panel */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    {/* AI Classification Preview */}
                    <div className="card card-glow-saffron animate-fadeup" style={{ padding: '24px' }}>
                        <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '16px' }}>🤖 AI Classification</h3>
                        {!classify && !classLoading && (
                            <p style={{ fontSize: '13px', color: 'var(--color-text-dim)' }}>
                                Enter a product description and click "Auto-Classify" or use voice input.
                            </p>
                        )}
                        {classLoading && (
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--color-text-muted)' }}>
                                <div className="spinner" /> <span>Classifying with AI…</span>
                            </div>
                        )}
                        {classify && (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                                <div className="field-item" style={{ borderColor: 'rgba(255,153,51,0.3)' }}>
                                    <div className="field-key">ONDC Category</div>
                                    <div className="field-val">{classify.category}</div>
                                </div>
                                <div className="field-item">
                                    <div className="field-key">Subcategory</div>
                                    <div className="field-val" style={{ fontSize: '13px' }}>{classify.subcategory}</div>
                                </div>
                                <div className="field-item">
                                    <div className="field-key">HSN Code</div>
                                    <div className="field-val" style={{ fontFamily: 'monospace', color: 'var(--color-saffron)' }}>{classify.hsn_code}</div>
                                </div>
                                <div>
                                    <div className="field-key" style={{ marginBottom: '6px' }}>Confidence</div>
                                    <div className="score-bar-track">
                                        <div className="score-bar-fill" style={{ width: `${Math.round(classify.confidence * 100)}%` }} />
                                    </div>
                                    <div style={{ textAlign: 'right', fontSize: '12px', marginTop: '4px', color: 'var(--color-green-light)' }}>
                                        {Math.round(classify.confidence * 100)}%
                                    </div>
                                </div>
                                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                                    {classify.keywords?.map(k => <span key={k} className="badge badge-muted">{k}</span>)}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* How it works */}
                    <div className="card animate-fadeup delay-1" style={{ padding: '24px' }}>
                        <h3 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '16px' }}>⚡ How it Works</h3>
                        <div className="steps">
                            {[
                                { icon: '🎙️', label: 'Speak in your language (Bhashini)', color: 'var(--color-saffron)' },
                                { icon: '🤖', label: 'AI classifies to ONDC taxonomy', color: 'var(--color-indigo-light)' },
                                { icon: '🔗', label: 'Vector DB matches you to best SNP', color: 'var(--color-green-light)' },
                                { icon: '✅', label: 'Profile saved to ONDC network', color: 'var(--color-saffron-light)' },
                            ].map((s, i, arr) => (
                                <div key={i} className="step">
                                    <div className="step-connector">
                                        <div className="step-dot" style={{ background: `${s.color}20`, color: s.color }}>{i + 1}</div>
                                        {i < arr.length - 1 && <div className="step-line" />}
                                    </div>
                                    <div className="step-content" style={{ paddingTop: '4px' }}>
                                        <span style={{ fontSize: '13px' }}>{s.icon} {s.label}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function SuccessView({ result, onNew }) {
    return (
        <div className="container" style={{ maxWidth: '720px' }}>
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                <div style={{ fontSize: '56px', marginBottom: '12px' }}>🎉</div>
                <div className="page-title">Onboarding Complete!</div>
                <p style={{ color: 'var(--color-text-muted)' }}>Your MSE is now registered on the ONDC network.</p>
            </div>

            <div className="card card-glow-green" style={{ padding: '28px', marginBottom: '20px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '20px' }}>📋 Registration Summary</h3>
                <div className="fields-grid">
                    <div className="field-item"><div className="field-key">MSE ID</div><div className="field-val">#{result.id}</div></div>
                    <div className="field-item"><div className="field-key">Business Name</div><div className="field-val">{result.business_name}</div></div>
                    <div className="field-item"><div className="field-key">ONDC Category</div><div className="field-val">{result.ondc_category}</div></div>
                    <div className="field-item"><div className="field-key">HSN Code</div><div className="field-val" style={{ fontFamily: 'monospace', color: 'var(--color-saffron)' }}>{result.hsn_code}</div></div>
                </div>
            </div>

            {result.matched_snp && (
                <div className="card card-glow-saffron" style={{ padding: '24px', marginBottom: '20px' }}>
                    <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '16px' }}>🏆 Recommended SNP Partner</h3>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <div style={{ fontSize: '18px', fontWeight: 800 }}>{result.matched_snp.name}</div>
                            <div style={{ fontSize: '13px', color: 'var(--color-text-muted)', marginTop: '4px' }}>{result.matched_snp.domain?.slice(0, 80)}…</div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                            <div style={{ fontSize: '36px', fontWeight: 900, color: 'var(--color-saffron)' }}>
                                {Math.round((result.match_score || 0) * 100)}%
                            </div>
                            <div style={{ fontSize: '11px', color: 'var(--color-text-dim)' }}>Match Score</div>
                        </div>
                    </div>
                </div>
            )}

            <div style={{ display: 'flex', gap: '12px' }}>
                <button className="btn btn-primary btn-lg" style={{ flex: 1 }} onClick={onNew}>+ Register Another MSE</button>
                <a href="/matches" className="btn btn-secondary btn-lg" style={{ flex: 1, textDecoration: 'none' }}>View All Matches →</a>
            </div>
        </div>
    );
}
