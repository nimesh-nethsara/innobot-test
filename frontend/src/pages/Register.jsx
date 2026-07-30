import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { apiFetch } from "../api";

export default function Register() {
  const [formData, setFormData] = useState({ full_name: "", email: "", password: "", role: "PATIENT", specialty: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await apiFetch("/auth/register", { method: "POST", body: JSON.stringify(formData) });
      navigate("/login");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "0 auto", padding: "2rem", border: "1px solid #ccc", borderRadius: "8px" }}>
      <h2 style={{ textAlign: "center", marginBottom: "1.5rem" }}>Register</h2>
      {error && <p style={{ color: "red", backgroundColor: "#fee", padding: "0.5rem", borderRadius: "4px" }}>{error}</p>}
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <input type="text" name="full_name" placeholder="Full Name" onChange={handleChange} required style={{ padding: "0.5rem" }} />
        <input type="email" name="email" placeholder="Email Address" onChange={handleChange} required style={{ padding: "0.5rem" }} />
        <input type="password" name="password" placeholder="Password" onChange={handleChange} required style={{ padding: "0.5rem" }} />
        <select name="role" value={formData.role} onChange={handleChange} style={{ padding: "0.5rem" }}>
          <option value="PATIENT">Patient</option>
          <option value="DOCTOR">Doctor</option>
        </select>
        {formData.role === "DOCTOR" && (
          <input type="text" name="specialty" placeholder="Medical Specialty (e.g. Cardiology)" onChange={handleChange} required style={{ padding: "0.5rem" }} />
        )}
        <button type="submit" style={{ padding: "0.75rem", backgroundColor: "#28a745", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}>Create Account</button>
      </form>
      <p style={{ textAlign: "center", marginTop: "1rem" }}>Already registered? <Link to="/login">Login</Link></p>
    </div>
  );
}