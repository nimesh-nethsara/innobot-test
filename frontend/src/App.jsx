import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import Login from "./pages/Login";
import Register from "./pages/Register";
import DoctorsList from "./pages/DoctorsList";
import DoctorSlots from "./pages/DoctorSlots";
import MyAppointments from "./pages/MyAppointments";
import ManageSchedule from "./pages/ManageSchedule";

export default function App() {
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem("user") || "null"));

  const logout = () => {
    localStorage.removeItem("user");
    setUser(null);
  };

  return (
    <BrowserRouter>
      <Navbar user={user} onLogout={logout} />
      <div style={{ maxWidth: "1000px", margin: "0 auto", padding: "2rem 1rem" }}>
        <Routes>
          <Route path="/login" element={<Login setUser={setUser} />} />
          <Route path="/register" element={<Register />} />
          
          <Route path="/doctors" element={user ? <DoctorsList /> : <Navigate to="/login" />} />
          <Route path="/doctors/:doctorId/slots" element={user ? <DoctorSlots /> : <Navigate to="/login" />} />
          <Route path="/my-appointments" element={user ? <MyAppointments /> : <Navigate to="/login" />} />
          
          <Route 
            path="/manage-schedule" 
            element={user && user.role === "DOCTOR" ? <ManageSchedule /> : <Navigate to="/" />} 
          />
          
          <Route path="*" element={<Navigate to={user ? "/my-appointments" : "/login"} />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}