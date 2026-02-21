import { NavLink } from 'react-router-dom';

const NAVLINKS = [
    { to: '/', label: 'Home', icon: '🏠', exact: true },
    { to: '/register', label: 'Register MSE', icon: '📝', badge: 'AI' },
    { to: '/matches', label: 'SNP Matches', icon: '🔗' },
    { to: '/verify', label: 'Verify Docs', icon: '🔍' },
    { to: '/contracts', label: 'Contracts', icon: '🏛️', badge: 'LIVE' },
];

export default function Navbar() {
    return (
        <nav className="navbar">
            <div className="navbar-inner">
                <NavLink to="/" className="navbar-brand">
                    <div className="navbar-logo">🇮🇳</div>
                    <div>
                        <div className="navbar-title">MSE Mapper</div>
                        <div className="navbar-subtitle">ONDC · TEAM Initiative</div>
                    </div>
                </NavLink>

                <div className="navbar-nav">
                    {NAVLINKS.map(({ to, label, icon, badge, exact }) => (
                        <NavLink
                            key={to}
                            to={to}
                            end={exact}
                            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
                        >
                            <span>{icon}</span>
                            <span>{label}</span>
                            {badge && <span className="nav-badge">{badge}</span>}
                        </NavLink>
                    ))}
                </div>
            </div>
        </nav>
    );
}
