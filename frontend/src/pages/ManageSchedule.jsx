import { useState, useEffect } from "react";
import { apiFetch } from "../api";

export default function ManageSchedule() {
  const [shifts, setShifts] = useState([]);
  const [formData, setFormData] = useState({ day_of_week: "0", start_time: "09:00", end_time: "17:00", slot_duration_mins: 30 });
  const [message, setMessage] = useState({ text: "", isError: false });

  const fetchSchedule = async () => {
    try {
      const data = await apiFetch("/doctors/availability/my");
      setShifts(data.availability);
    } catch (err) {
      setMessage({ text: err.message, isError: true });
    }
  };

  useEffect(() => { fetchSchedule(); }, []);

  const handleAddShift = async (e) => {
    e.preventDefault();
    setMessage({ text: "", isError: false });
    try {
      await apiFetch("/doctors/availability", {
        method: "POST",
        body: JSON.stringify({ day_of_week: parseInt(formData.day_of_week), start_time: formData.start_time, end_time: formData.end_time, slot_duration_mins: parseInt(formData.slot_duration_mins) }),
      });
      setMessage({ text: "Shift added successfully!", isError: false });
      fetchSchedule();
    } catch (err) {
      setMessage({ text: err.message, isError: true });
    }
  };

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  return (
    <div>
      <h2>Manage My Schedule (Working Hours)</h2>
      {message.text && <p style={{ color: message.isError ? "red" : "green", padding: "0.5rem", backgroundColor: message.isError ? "#fee" : "#efe" }}>{message.text}</p>}

      <div style={{ border: "1px solid #ccc", padding: "1.5rem", borderRadius: "8px", marginBottom: "2rem", backgroundColor: "#fdfdfd" }}>
        <h3 style={{ marginTop: 0 }}>Add New Shift</h3>
        <form onSubmit={handleAddShift} style={{ display: "flex", gap: "1rem", alignItems: "flex-end", flexWrap: "wrap" }}>
          <div style={{ flex: 1, minWidth: "150px" }}>
            <label style={{ display: "block", marginBottom: "0.5rem" }}>Day of Week</label>
            <select name="day_of_week" value={formData.day_of_week} onChange={handleChange} style={{ width: "100%", padding: "0.5rem" }}>
              <option value="0">Monday</option><option value="1">Tuesday</option><option value="2">Wednesday</option>
              <option value="3">Thursday</option><option value="4">Friday</option><option value="5">Saturday</option><option value="6">Sunday</option>
            </select>
          </div>
          <div style={{ flex: 1, minWidth: "120px" }}>
            <label style={{ display: "block", marginBottom: "0.5rem" }}>Start Time</label>
            <input type="time" name="start_time" value={formData.start_time} onChange={handleChange} required style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }} />
          </div>
          <div style={{ flex: 1, minWidth: "120px" }}>
            <label style={{ display: "block", marginBottom: "0.5rem" }}>End Time</label>
            <input type="time" name="end_time" value={formData.end_time} onChange={handleChange} required style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }} />
          </div>
          <button type="submit" style={{ padding: "0.6rem 1.5rem", backgroundColor: "#007bff", color: "white", border: "none", borderRadius: "4px", cursor: "pointer", height: "36px" }}>Save Shift</button>
        </form>
      </div>

      <h3>My Weekly Roster</h3>
      {shifts.length === 0 ? <p>No shifts added yet.</p> : (
        <table style={{ width: "100%", borderCollapse: "collapse" }} border="1" cellPadding="12">
          <thead style={{ backgroundColor: "#f8f9fa", textAlign: "left" }}>
            <tr><th>Day</th><th>Start Time</th><th>End Time</th><th>Slot Duration</th></tr>
          </thead>
          <tbody>
            {shifts.map((shift) => (
              <tr key={shift.id}>
                <td>{shift.day_name}</td>
                <td>{shift.start_time}</td>
                <td>{shift.end_time}</td>
                <td>{shift.slot_duration_mins} mins</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}