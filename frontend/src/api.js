const BASE = import.meta.env.VITE_API_URL || "http://localhost:8001";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  getGrades: () => request("/grades"),
  getSubjects: () => request("/subjects"),
  createStudent: (name, grade) =>
    request("/students", { method: "POST", body: JSON.stringify({ name, grade }) }),
  getStudent: (id) => request(`/students/${id}`),
  getSessions: (studentId) => request(`/students/${studentId}/sessions`),
  createSession: (studentId, subject) =>
    request("/sessions", { method: "POST", body: JSON.stringify({ student_id: studentId, subject }) }),
  getMessages: (sessionId) => request(`/sessions/${sessionId}/messages`),
  sendMessage: (sessionId, message) =>
    request("/chat", { method: "POST", body: JSON.stringify({ session_id: sessionId, message }) }),
};
