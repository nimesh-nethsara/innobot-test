import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { apiFetch } from "../api";

export default function Login({ setUser }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const data = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      localStorage.setItem("user", JSON.stringify(data.user));
      setUser(data.user);
      navigate(data.user.role === "DOCTOR" ? "/my-appointments" : "/doctors");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "0 auto", padding: "2rem", border: "1px solid #ccc", borderRadius: "8px" }}>
      <h2 style={{ textAlign: "center", marginBottom: "1.5rem" }}>Login</h2>
      {error && <p style={{ color: "red", backgroundColor: "#fee", padding: "0.5rem", borderRadius: "4px" }}>{error}</p>}
      <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <div>
          <label style={{ display: "block", marginBottom: "0.5rem" }}>Email</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }} />
        </div>
        <div>
          <label style={{ display: "block", marginBottom: "0.5rem" }}>Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }} />
        </div>
        <button type="submit" style={{ padding: "0.75rem", backgroundColor: "#007bff", color: "white", border: "none", borderRadius: "4px", cursor: "pointer", marginTop: "0.5rem" }}>Login</button>
      </form>
      <p style={{ textAlign: "center", marginTop: "1rem" }}>Don't have an account? <Link to="/register">Register</Link></p>
    </div>
  );
}