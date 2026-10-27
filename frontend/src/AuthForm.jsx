import { useState } from 'react';
import './styles/auth.css';

const API = '/api';

export default function AuthForm({ onAuth }) {
  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (mode === 'register') {
        const res = await fetch(`${API}/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });
        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.detail || `HTTP ${res.status}`);
        }
      }

      const loginRes = await fetch(`${API}/auth/jwt/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username: email, password }),
      });
      if (!loginRes.ok) {
        throw new Error('Неверный email или пароль');
      }
      const { access_token } = await loginRes.json();
      localStorage.setItem('token', access_token);
      onAuth();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-form">
      <h2>{mode === 'login' ? 'Вход' : 'Регистрация'}</h2>
      <form onSubmit={submit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={6}
        />
        <button type="submit" disabled={loading}>
          {loading ? '...' : mode === 'login' ? 'Войти' : 'Зарегистрироваться'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      <p className="auth-switch">
        {mode === 'login' ? 'Нет аккаунта? ' : 'Уже есть аккаунт? '}
        <button
          type="button"
          className="link"
          onClick={() => {
            setMode(mode === 'login' ? 'register' : 'login');
            setError(null);
          }}
        >
          {mode === 'login' ? 'Зарегистрироваться' : 'Войти'}
        </button>
      </p>
    </div>
  );
}