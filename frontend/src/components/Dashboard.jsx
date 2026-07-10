import { useState, useEffect } from "react";
import { api } from "../api";
import styles from "./Dashboard.module.css";

const SUBJECT_ICONS = {
  Math: "🔢",
  Science: "🔬",
  English: "📖",
  History: "🏛️",
  Geography: "🌍",
  General: "💡",
};

export default function Dashboard({ student, onStartSession, onLogout }) {
  const [subjects, setSubjects] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [starting, setStarting] = useState(null);

  useEffect(() => {
    api.getSubjects().then(setSubjects);
    api.getSessions(student.id).then(setSessions).catch(() => {});
  }, [student.id]);

  async function handleSubjectClick(subject) {
    setStarting(subject);
    try {
      const session = await api.createSession(student.id, subject);
      onStartSession(session);
    } catch {
      setStarting(null);
    }
  }

  async function handleContinueSession(session) {
    onStartSession(session);
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <div className={styles.greeting}>
            <span className={styles.greetingEmoji}>👋</span>
            <div>
              <h1 className={styles.name}>Hello, {student.name}!</h1>
              <p className={styles.grade}>{student.grade_label} Student</p>
            </div>
          </div>
          <button className="btn-ghost" onClick={onLogout}>Sign out</button>
        </div>
      </header>

      <main className={styles.main}>
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>What would you like to learn today?</h2>
          <div className={styles.subjectGrid}>
            {subjects.map(subject => (
              <button
                key={subject}
                className={styles.subjectCard}
                onClick={() => handleSubjectClick(subject)}
                disabled={starting !== null}
              >
                <span className={styles.subjectIcon}>{SUBJECT_ICONS[subject] || "📚"}</span>
                <span className={styles.subjectName}>{subject}</span>
                {starting === subject && <span className={styles.loading}>Starting...</span>}
              </button>
            ))}
          </div>
        </section>

        {sessions.length > 0 && (
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Recent sessions</h2>
            <div className={styles.sessionList}>
              {sessions.slice(-5).reverse().map(session => (
                <button
                  key={session.id}
                  className={styles.sessionCard}
                  onClick={() => handleContinueSession(session)}
                >
                  <span className={styles.sessionIcon}>{SUBJECT_ICONS[session.subject] || "📚"}</span>
                  <div className={styles.sessionInfo}>
                    <span className={styles.sessionSubject}>{session.subject}</span>
                    <span className={styles.sessionMeta}>
                      {session.message_count} messages · {new Date(session.started_at).toLocaleDateString()}
                    </span>
                  </div>
                  <span className={styles.sessionArrow}>→</span>
                </button>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
