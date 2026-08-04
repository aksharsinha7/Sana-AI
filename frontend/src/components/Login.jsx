import { useState, useEffect } from "react";
import { api } from "../api";
import styles from "./Login.module.css";

export default function Login({ onLogin }) {
  const [name, setName] = useState("");
  const [grade, setGrade] = useState("");
  const [grades, setGrades] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getGrades().then(setGrades).catch(() => setError("Cannot connect to server. Is the backend running?"));
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!name.trim() || grade === "") return;
    setLoading(true);
    setError("");
    try {
      const student = await api.createStudent(name.trim(), parseInt(grade));
      onLogin(student);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.logoRow}>
          <span className={styles.logoIcon}>✦</span>
          <span className={styles.logoText}>Sana AI</span>
        </div>
        <p className={styles.subtitle}>Your personal learning companion</p>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label htmlFor="name">Your name</label>
            <input
              id="name"
              type="text"
              placeholder="Enter your name"
              value={name}
              onChange={e => setName(e.target.value)}
              autoFocus
            />
          </div>

          <div className={styles.field}>
            <label htmlFor="grade">Your grade</label>
            <select
              id="grade"
              value={grade}
              onChange={e => setGrade(e.target.value)}
            >
              <option value="">Select your grade...</option>
              {grades.map(g => (
                <option key={g.value} value={g.value}>{g.label}</option>
              ))}
            </select>
          </div>

          {error && <p className={styles.error}>{error}</p>}

          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !name.trim() || grade === ""}
            style={{ width: "100%", fontSize: "1.05rem", padding: "0.85rem" }}
          >
            {loading ? "Starting..." : "Start Learning →"}
          </button>
        </form>
      </div>
    </div>
  );
}
