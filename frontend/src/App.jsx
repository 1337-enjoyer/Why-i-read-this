import { useEffect, useState } from 'react';
import AuthForm from './AuthForm';
import './styles/app.css';

const API = '/api';

export default function App() {
  const [article, setArticle] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [user, setUser] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [showAuth, setShowAuth] = useState(false);

  const loadHistory = async () => {
    const token = localStorage.getItem('token');
    if (!token) { setHistory([]); return; }
    const res = await fetch(`${API}/wiki/history`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) setHistory(await res.json());
  };

  const loadUser = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setUser(null);
      setHistory([]);
      setAuthChecked(true);
      return;
    }
    const res = await fetch(`${API}/users/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) {
      setUser(await res.json());
      await loadHistory();
    } else {
      localStorage.removeItem('token');
      setUser(null);
      setHistory([]);
    }
    setAuthChecked(true);
  };

  useEffect(() => { loadUser(); }, []);

  const fetchRandom = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const url = token ? `${API}/wiki/random/auth` : `${API}/wiki/random`;
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const res = await fetch(url, { headers });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setArticle(await res.json());
      if (token) loadHistory();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchArticleById = async (pageId) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/wiki/article/${pageId}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setArticle(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setHistory([]);
    setArticle(null);
  };

  if (!authChecked) {
    return <div className="loading-screen">Загрузка...</div>;
  }

  return (
    <div className="app">
      {user && (
        <aside className="sidebar">
          <div className="sidebar-user">
            <div className="label">Вы вошли как</div>
            <div className="email">{user.email}</div>
            <button className="secondary" onClick={logout}>Выйти</button>
          </div>

          <h3>Прочитано</h3>
          {history.length === 0 ? (
            <p className="history-empty">Пока пусто</p>
          ) : (
            <ul className="history-list">
              {history.map((h) => (
                <li
                  key={h.id}
                  className="history-item"
                  onClick={() => fetchArticleById(h.page_id)}
                >
                  {h.title}
                </li>
              ))}
            </ul>
          )}
        </aside>
      )}

      <main className="main">
        <header className="header">
          <h1>Why I Read This</h1>
          <p>Случайная статья из Википедии.</p>
        </header>

        <div className="auth-block">
          {user ? (
            <div className="auth-status">Вы авторизованы. История сохраняется.</div>
          ) : (
            <>
              <button
                className="secondary"
                onClick={() => setShowAuth(!showAuth)}
              >
                {showAuth ? 'Скрыть вход' : 'Войти / Зарегистрироваться'}
              </button>
              {showAuth && (
                <AuthForm
                  onAuth={async () => {
                    await loadUser();
                    setShowAuth(false);
                  }}
                />
              )}
            </>
          )}
        </div>

        <button className="random-btn" onClick={fetchRandom} disabled={loading}>
          {loading ? 'Загрузка...' : 'Случайная статья'}
        </button>

        {error && <p className="error">{error}</p>}

        {article && (
          <article className="article">
            {article.image_url && (
              <img
                src={article.image_url}
                alt={article.title}
                className="article-image"
              />
            )}
            <h2>{article.title}</h2>
            <p className="article-body">{article.extract}</p>
          </article>
        )}
      </main>
    </div>
  );
}