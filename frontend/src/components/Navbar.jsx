import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const initials = user?.name?.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);

  return (
    <nav className="navbar">
      <Link to="/dashboard" className="navbar-brand">
        <span className="logo-icon">🗂️</span>
        <span>TaskFlow</span>
      </Link>
      <div className="navbar-actions">
        <div className="user-badge">
          <div className="user-avatar">{initials}</div>
          {user?.name}
        </div>
        <button className="btn btn-ghost btn-sm" onClick={logout}>
          Logout
        </button>
      </div>
    </nav>
  );
}
