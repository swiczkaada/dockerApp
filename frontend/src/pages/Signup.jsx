import { useState } from 'react';
import axios from 'axios';

export default function Signup() {
  const [form, setForm] = useState({ email: '', username: '', password: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await axios.post('http://localhost:8000/api/signup/', form, {
      withCredentials: true,
    });
    if (res.status === 201) {
      localStorage.setItem('user', JSON.stringify(res.data.user));
      window.location.href = '/';
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h1>S'inscrire</h1>
      <input type="email" placeholder="Email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
      <input type="text" placeholder="Nom d'utilisateur" value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} />
      <input type="password" placeholder="Mot de passe" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} />
      <button type="submit">S'inscrire</button>
    </form>
  );
}
