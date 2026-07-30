import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../api";

export default function DoctorsList() {
  const [doctors, setDoctors] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [error, setError] = useState("");

  const fetchDoctors = async (queryText = "") => {
    try {
      // Pass the general 'search' query to the new backend logic
      const query = queryText ? `?search=${encodeURIComponent(queryText)}` : "";
      const data = await apiFetch(`/doctors${query}`);
      setDoctors(data.doctors);
    } catch (err) {
      setError(err.message);
    }
  };

  // Fetch all doctors on first load
  useEffect(() => { 
    fetchDoctors(""); 
  }, []);

  // Live search: Trigger fetch every time the user types
  const handleSearchChange = (e) => {
    const text = e.target.value;
    setSearchTerm(text);
    fetchDoctors(text);
  };

  return (
    <div>
      <h2>Find a Doctor</h2>
      
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "2rem" }}>
        <input 
          type="text" 
          placeholder="Search by name or specialty..." 
          value={searchTerm} 
          onChange={handleSearchChange} 
          style={{ flex: 1, padding: "0.75rem", maxWidth: "500px", borderRadius: "4px", border: "1px solid #ccc" }} 
        />
        {searchTerm && (
          <button 
            type="button" 
            onClick={() => { setSearchTerm(""); fetchDoctors(""); }} 
            style={{ padding: "0.5rem 1rem", cursor: "pointer", borderRadius: "4px", border: "1px solid #ccc" }}
          >
            Clear
          </button>
        )}
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}
      
      <div style={{ display: "grid", gap: "1rem" }}>
        {doctors.length === 0 && !error ? (
          <p>No doctors found matching your search.</p>
        ) : (
          doctors.map((doc) => (
            <div key={doc.id} style={{ border: "1px solid #ddd", borderRadius: "8px", padding: "1.5rem", display: "flex", justifyContent: "space-between", alignItems: "center", backgroundColor: "#fafafa" }}>
              <div>
                <h3 style={{ margin: "0 0 0.5rem 0" }}>{doc.name}</h3>
                <p style={{ margin: 0, color: "#555", fontWeight: "bold" }}>{doc.specialty}</p>
              </div>
              <Link to={`/doctors/${doc.id}/slots`} style={{ backgroundColor: "#007bff", color: "white", padding: "0.5rem 1rem", borderRadius: "4px", textDecoration: "none" }}>
                Book Appointment
              </Link>
            </div>
          ))
        )}
      </div>
    </div>
  );
}