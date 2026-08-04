import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { api } from "../api";
import styles from "./Chat.module.css";

const SUBJECT_ICONS = {
  Math: "🔢", Science: "🔬", English: "📖",
  History: "🏛️", Geography: "🌍", General: "💡",
};

const STARTER_PROMPTS = {
  Math: ["Can you explain fractions?", "Help me with multiplication", "What is an equation?"],
  Science: ["What is photosynthesis?", "How do volcanoes work?", "What is gravity?"],
  English: ["Help me write a paragraph", "What is a metaphor?", "Check my grammar"],
  History: ["Tell me about ancient Egypt", "What caused World War 1?", "Who was Gandhi?"],
  Geography: ["What is the water cycle?", "Tell me about continents", "What is climate?"],
  General: ["Help me with my homework", "Explain something to me", "I have a question"],
};

export default function Chat({ student, session, onBack }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    api.getMessages(session.id)
      .then(msgs => setMessages(msgs))
      .catch(() => {})
      .finally(() => setLoadingHistory(false));
  }, [session.id]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage(text) {
    const msg = text || input.trim();
    if (!msg || loading) return;
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: msg }]);
    setLoading(true);
    try {
      const { reply, image } = await api.sendMessage(session.id, msg);
      setMessages(prev => [...prev, { role: "assistant", content: reply, image }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", content: "Sorry, something went wrong. Please try again." }]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  const starters = STARTER_PROMPTS[session.subject] || STARTER_PROMPTS.General;
  const showStarters = messages.length === 0 && !loadingHistory;

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <button className="btn-ghost" onClick={onBack}>← Back</button>
        <div className={styles.headerCenter}>
          <span className={styles.sanaLogo}>✦</span>
          <div>
            <div className={styles.sanaName}>Sana AI</div>
            <div className={styles.studentInfo}>{session.subject} · {student.name} · {student.grade_label}</div>
          </div>
        </div>
        <div style={{ width: 80 }} />
      </header>

      <div className={styles.messages}>
        {loadingHistory && (
          <div className={styles.loadingHistory}>Loading conversation...</div>
        )}

        {showStarters && (
          <div className={styles.welcome}>
            <div className={styles.welcomeEmoji}>{SUBJECT_ICONS[session.subject] || "📚"}</div>
            <h2>Ready to learn {session.subject}?</h2>
            <p>Ask me anything or pick a question to get started:</p>
            <div className={styles.starters}>
              {starters.map(s => (
                <button key={s} className={styles.starterBtn} onClick={() => sendMessage(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`${styles.message} ${styles[msg.role]}`}>
            {msg.role === "assistant" && (
              <div className={`${styles.avatar} ${styles.sanaAvatar}`}>✦</div>
            )}
            <div className={styles.bubbleWrapper}>
              {msg.role === "assistant" && msg.image && (
                <div className={styles.imageCard}>
                  <img
                    src={msg.image.url}
                    alt={msg.image.caption}
                    className={styles.topicImage}
                    onError={e => e.target.parentElement.style.display = "none"}
                  />
                  <span className={styles.imageCaption}>{msg.image.caption}</span>
                </div>
              )}
              <div className={styles.bubble}>
                {msg.role === "assistant" ? (
                  <div className="prose">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                ) : (
                  <p>{msg.content}</p>
                )}
              </div>
            </div>
            {msg.role === "user" && (
              <div className={styles.avatar}>{student.name[0].toUpperCase()}</div>
            )}
          </div>
        ))}

        {loading && (
          <div className={`${styles.message} ${styles.assistant}`}>
            <div className={`${styles.avatar} ${styles.sanaAvatar}`}>✦</div>
            <div className={`${styles.bubble} ${styles.typing}`}>
              <span /><span /><span />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className={styles.inputBar}>
        <textarea
          ref={inputRef}
          className={styles.input}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`Ask about ${session.subject}...`}
          rows={1}
          disabled={loading}
        />
        <button
          className={`btn-primary ${styles.sendBtn}`}
          onClick={() => sendMessage()}
          disabled={loading || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
}
