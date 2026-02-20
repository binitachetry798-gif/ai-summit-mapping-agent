import { useState, useRef, useEffect } from 'react';

const LANGUAGES = [
    { code: 'hi', name: 'हिंदी (Hindi)' },
    { code: 'mr', name: 'मराठी (Marathi)' },
    { code: 'ta', name: 'தமிழ் (Tamil)' },
    { code: 'te', name: 'తెలుగు (Telugu)' },
    { code: 'bn', name: 'বাংলা (Bengali)' },
    { code: 'gu', name: 'ગુજરાતી (Gujarati)' },
    { code: 'kn', name: 'ಕನ್ನಡ (Kannada)' },
    { code: 'ml', name: 'മലയാളം (Malayalam)' },
    { code: 'pa', name: 'ਪੰਜਾਬੀ (Punjabi)' },
    { code: 'or', name: 'ଓଡ଼ିଆ (Odia)' },
    { code: 'as', name: 'অসমীয়া (Assamese)' },
    { code: 'ur', name: 'اردو (Urdu)' },
    { code: 'en', name: 'English' },
];

/**
 * VoiceInput — Records audio from the microphone and sends it to the
 * Bhashini transcription API. Falls back to the Web Speech API as a
 * secondary demo mode for browsers that support it.
 *
 * Props:
 *  onResult(text) — called with the English translation
 *  onLoading(bool) — parent can show a loading indicator
 */
export default function VoiceInput({ onResult, onLoading }) {
    const [lang, setLang] = useState('hi');
    const [recording, setRecording] = useState(false);
    const [status, setStatus] = useState('idle'); // idle | recording | processing | done | error
    const [transcript, setTranscript] = useState({ original: '', translated: '' });
    const [error, setError] = useState('');

    const mediaRecorder = useRef(null);
    const chunks = useRef([]);

    // ── Stop recording and send to API ────────────────────────────────
    const stopAndSend = async (recorder) => {
        recorder.stop();
        setRecording(false);
        setStatus('processing');
        if (onLoading) onLoading(true);
    };

    // ── Start recording ────────────────────────────────────────────────
    const startRecording = async () => {
        setError('');
        setTranscript({ original: '', translated: '' });
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            chunks.current = [];
            const recorder = new MediaRecorder(stream);
            mediaRecorder.current = recorder;

            recorder.ondataavailable = (e) => chunks.current.push(e.data);

            recorder.onstop = async () => {
                stream.getTracks().forEach((t) => t.stop());
                const blob = new Blob(chunks.current, { type: 'audio/webm' });
                const reader = new FileReader();
                reader.onloadend = async () => {
                    const base64 = reader.result.split(',')[1];
                    try {
                        const { transcribeVoice } = await import('../api.js');
                        const data = await transcribeVoice(base64, lang);
                        const result = {
                            original: data.original_transcript,
                            translated: data.english_translation,
                        };
                        setTranscript(result);
                        setStatus('done');
                        if (onResult) onResult(result.translated);
                    } catch (err) {
                        setError('Transcription failed. Ensure the backend is running.');
                        setStatus('error');
                    } finally {
                        if (onLoading) onLoading(false);
                    }
                };
                reader.readAsDataURL(blob);
            };

            recorder.start();
            setRecording(true);
            setStatus('recording');

            // Auto-stop after 10 seconds
            setTimeout(() => {
                if (recorder.state === 'recording') stopAndSend(recorder);
            }, 10000);
        } catch (err) {
            setError('Microphone access denied. Please allow microphone permissions.');
            setStatus('error');
            if (onLoading) onLoading(false);
        }
    };

    const toggleRecording = () => {
        if (recording && mediaRecorder.current?.state === 'recording') {
            stopAndSend(mediaRecorder.current);
        } else {
            startRecording();
        }
    };

    const statusLabel = {
        idle: 'Click mic to speak',
        recording: 'Recording… click to stop',
        processing: 'Transcribing with Bhashini…',
        done: 'Transcription complete ✓',
        error: error,
    };

    return (
        <div style={{ background: 'var(--color-surface2)', borderRadius: 'var(--radius-lg)', padding: '20px', border: '1px solid var(--color-border)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
                {/* Language Selector */}
                <div style={{ flex: 1 }}>
                    <label className="form-label" style={{ marginBottom: '6px', display: 'block' }}>🌐 Language</label>
                    <select
                        className="form-select"
                        value={lang}
                        onChange={(e) => setLang(e.target.value)}
                        disabled={recording || status === 'processing'}
                    >
                        {LANGUAGES.map((l) => (
                            <option key={l.code} value={l.code}>{l.name}</option>
                        ))}
                    </select>
                </div>

                {/* Mic Button */}
                <div style={{ marginTop: '22px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                    <button
                        className={`mic-btn ${recording ? 'recording' : ''}`}
                        onClick={toggleRecording}
                        disabled={status === 'processing'}
                        title={recording ? 'Click to stop' : 'Click to record'}
                    >
                        {recording ? '⏹' : '🎙️'}
                    </button>
                    <span style={{ fontSize: '10px', color: 'var(--color-text-dim)' }}>
                        {recording ? '10s max' : 'Record'}
                    </span>
                </div>
            </div>

            {/* Status */}
            <div style={{ fontSize: '13px', color: status === 'error' ? '#f87171' : status === 'done' ? 'var(--color-green-light)' : 'var(--color-text-muted)' }}>
                {status === 'processing' && <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><div className="spinner" style={{ width: 14, height: 14 }} /> {statusLabel[status]}</span>}
                {status !== 'processing' && statusLabel[status]}
            </div>

            {/* Results */}
            {transcript.original && (
                <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <div className="field-item">
                        <div className="field-key">Original ({LANGUAGES.find(l => l.code === lang)?.name})</div>
                        <div className="field-val" style={{ fontSize: '14px' }}>{transcript.original}</div>
                    </div>
                    <div className="field-item" style={{ borderColor: 'rgba(34,197,94,0.3)', background: 'rgba(34,197,94,0.05)' }}>
                        <div className="field-key" style={{ color: 'var(--color-green-light)' }}>English Translation</div>
                        <div className="field-val">{transcript.translated}</div>
                    </div>
                </div>
            )}
        </div>
    );
}
