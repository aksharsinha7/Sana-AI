import { useState, useEffect } from "react";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";
import Chat from "./components/Chat";

export default function App() {
  const [student, setStudent] = useState(null);
  const [activeSession, setActiveSession] = useState(null);

  useEffect(() => {
    const saved = localStorage.getItem("student");
    if (saved) setStudent(JSON.parse(saved));
  }, []);

  function handleLogin(studentData) {
    localStorage.setItem("student", JSON.stringify(studentData));
    setStudent(studentData);
  }

  function handleLogout() {
    localStorage.removeItem("student");
    setStudent(null);
    setActiveSession(null);
  }

  if (!student) return <Login onLogin={handleLogin} />;
  if (activeSession) return (
    <Chat
      student={student}
      session={activeSession}
      onBack={() => setActiveSession(null)}
    />
  );
  return (
    <Dashboard
      student={student}
      onStartSession={setActiveSession}
      onLogout={handleLogout}
    />
  );
}
