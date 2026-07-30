import { useState, useEffect } from "react";
import { apiFetch } from "../api";

export default function MyAppointments() {
  const [appointments, setAppointments] = useState([]);
  const [error, setError] = useState("");
  const user = JSON.parse(localStorage.getItem("user") || "{}");

  const loadAppointments = async () => {
    try {
      const data = await apiFetch("/appointments/my");
      setAppointments(data.appointments);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => { loadAppointments(); }, []);

  const handleCancel = async (id) => {
    if (!window.confirm("Are you sure you want to cancel this appointment?")) return;
    try {
      await apiFetch(`/appointments/${id}/cancel`, { method: "PATCH" });
      loadAppointments();
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div>
      <h2>{user.role === "DOCTOR" ? "My Roster" : "My Upcoming Appointments"}</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      
      {appointments.length === 0 ? (
        <p>No appointments found.</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem" }} border="1" cellPadding="12">
          <thead style={{ backgroundColor: "#f8f9fa", textAlign: "left" }}>
            <tr>
              <th>ID</th>
              <th>Date</th>
              <th>Time</th>
              <th>Status</th>
              {user.role === "PATIENT" && <th>Action</th>}
            </tr>
          </thead>
          <tbody>
            {appointments.map((appt) => (
              <tr key={appt.id} style={{ backgroundColor: appt.status === "CANCELLED" ? "#fafafa" : "#fff", opacity: appt.status === "CANCELLED" ? 0.6 : 1 }}>
                <td>#{appt.id}</td>
                <td>{appt.date}</td>
                <td>{appt.start_time} - {appt.end_time}</td>
                <td style={{ fontWeight: "bold", color: appt.status === "BOOKED" ? "green" : "red" }}>{appt.status}</td>
                {user.role === "PATIENT" && (
                  <td>
                    {appt.status === "BOOKED" && (
                      <button onClick={() => handleCancel(appt.id)} style={{ padding: "0.4rem 0.8rem", backgroundColor: "#dc3545", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}>Cancel</button>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}