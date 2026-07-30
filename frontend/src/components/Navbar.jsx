import { Link } from 'react-router-dom';

export default function Navbar({ user, onLogout }) {
  return (
    <nav style={{ padding: '1rem 2rem', backgroundColor: '#f8f9fa', borderBottom: '1px solid #dee2e6', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <Link to="/" style={{ fontWeight: 'bold', fontSize: '1.2rem', textDecoration: 'none', color: '#333' }}>
        ClinicCare
      </Link>
      
      <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
        {user ? (
          <>
            <span style={{ color: '#555' }}>Welcome, <strong>{user.full_name}</strong></span>
            
            {user.role === 'PATIENT' && (
              <Link to="/doctors" style={{ textDecoration: 'none', color: '#007bff', fontWeight: '500' }}>Find Doctors</Link>
            )}
            
            {user.role === 'DOCTOR' && (
              <Link to="/manage-schedule" style={{ textDecoration: 'none', color: '#28a745', fontWeight: '500' }}>Manage Schedule</Link>
            )}
            
            <Link to="/my-appointments" style={{ textDecoration: 'none', color: '#007bff', fontWeight: '500' }}>My Appointments</Link>
            
            <button onClick={onLogout} style={{ padding: '0.4rem 0.8rem', backgroundColor: '#dc3545', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" style={{ textDecoration: 'none', color: '#007bff' }}>Login</Link>
            <Link to="/register" style={{ textDecoration: 'none', color: '#007bff' }}>Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}