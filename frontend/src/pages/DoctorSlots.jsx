import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiFetch } from "../api";

export default function DoctorSlots() {
  const { doctorId } = useParams();
  const navigate = useNavigate();
  // Default to tomorrow's date
  const [date, setDate] = useState(() => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split("T")[0];
  });
  const [slots, setSlots] = useState([]);
  const [notes, setNotes] = useState("");
  const [message, setMessage] = useState({ text: "", isError: false });

  const fetchSlots = async () => {
    try {
      const data = await apiFetch(`/doctors/${doctorId}/available-slots?date=${date}`);
      setSlots(data.slots);
    } catch (err) {
      setMessage({ text: err.message, isError: true });
      setSlots([]);
    }
  };

  useEffect(() => { fetchSlots(); }, [date, doctorId]);

  const handleBook = async (slot) => {
    setMessage({ text: "", isError: false });
    try {
      await apiFetch("/appointments", {
        method: "POST",
        body: JSON.stringify({ doctor_id: parseInt(doctorId), appointment_date: date, start_time: slot.start_time, end_time: slot.end_time, notes }),
      });
      navigate("/my-appointments");
    } catch (err) {
      setMessage({ text: err.message, isError: true });
    }
  };

  return (
    <div style={{ maxWidth: "600px" }}>
      <h2>Select Appointment Slot</h2>
      
      <div style={{ marginBottom: "1.5rem" }}>
        <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "bold" }}>Date</label>
        <input type="date" value={date} onChange={(e) => setDate(e.target.value)} style={{ padding: "0.5rem", width: "100%", boxSizing: "border-box" }} />
      </div>

      <div style={{ marginBottom: "1.5rem" }}>
        <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "bold" }}>Reason for Visit (Optional)</label>
        <textarea rows="3" value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="e.g. Annual checkup..." style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box", resize: "vertical" }} />
      </div>

      {message.text && <p style={{ color: message.isError ? "red" : "green", padding: "0.5rem", backgroundColor: message.isError ? "#fee" : "#efe" }}>{message.text}</p>}

      <h3>Available Slots</h3>
      {slots.length === 0 ? (
        <p style={{ color: "#666" }}>No available slots for this date. (Note: Ensure you select a date matching the doctor's working schedule).</p>
      ) : (
        <div style={{ display: "grid", gap: "1rem" }}>
          {slots.map((slot, index) => (
            <div key={index} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "1rem", border: "1px solid #ddd", borderRadius: "6px", backgroundColor: "#fff" }}>
              <span style={{ fontSize: "1.1rem" }}>{slot.start_time} - {slot.end_time}</span>
              <button onClick={() => handleBook(slot)} style={{ padding: "0.5rem 1rem", backgroundColor: "#28a745", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}>Book Slot</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}