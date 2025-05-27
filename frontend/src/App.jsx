import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Signup from './pages/Signup';
import Login from './pages/Login';
import Profile from './pages/Profile';

export default function App() {
  const user = JSON.parse(localStorage.getItem('user'));

  return (
    <BrowserRouter>
      <Layout user={user}>
        <Routes>
          <Route path="/signup" element={<Signup />} />
          <Route path="/login" element={<Login />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
