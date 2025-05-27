// src/components/Layout.jsx
import Header from './Header';

export default function Layout({ children, user }) {
  return (
    <>
      <Header user={user} />
      <main className="container">{children}</main>
    </>
  );
}
