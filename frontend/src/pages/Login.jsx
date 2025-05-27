export default function Login() {
  const [form, setForm] = useState({ email: '', password: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await axios.post('http://localhost:8000/api/login/', form, {
      withCredentials: true,
    });
    if (res.status === 200) {
      localStorage.setItem('user', JSON.stringify(res.data.user));
      window.location.href = '/';
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h1>Se connecter</h1>
      <input type="email" placeholder="Email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
      <input type="password" placeholder="Mot de passe" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} />
      <button type="submit">Se connecter</button>
    </form>
  );
}
