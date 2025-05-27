// src/components/Header.jsx
import { Link } from 'react-router-dom';

export default function Header({ user }) {
  return (
    <header>
      <div className="container">
        <Link to="/" className="logo">La boutique de Adam</Link>
        <nav>
          {user ? (
            <>
              <span className="user">Bonjour, {user.username}</span>
              <Link to="/profile">Mon compte</Link>
              <a href="#" onClick={() => localStorage.clear()}>Se déconnecter</a>
            </>
          ) : (
            <>
              <Link to="/login" className="btn">Se connecter</Link>
              <Link to="/signup" className="btn btn-primary">S'inscrire</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
