import { useState, useEffect } from 'react';
import axios from 'axios';

export default function Profile() {
  const [user, setUser] = useState(null);
  const [form, setForm] = useState({ email: '', username: '' });

  useEffect(() => {
    axios.get('http://localhost:8000/api/profile/', { withCredentials: true })
      .then(res => {
        setUser(res.data);
        setForm({ email: res.data.email, username: res.data.username });
      });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await axios.put('http://localhost:8000/api/profile/', form, { withCredentials: true });
    alert('Profil mis à jour');
  };

  if (!user) return <p>Chargement...</p>;

  return (
    <form onSubmit={handleSubmit}>
      <h1>Votre compte</h1>
      <p>Bienvenue, {user.username} !</p>
      <input type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
      <input type="text" value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} />
      <button type="submit">Mettre à jour</button>
    </form>
  );
}
