import { NavLink, Outlet, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const TITLES = {
  "/": "Customers",
  "/products": "Products",
  "/new-order": "New Order",
  "/history": "Order History",
};

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  const title = TITLES[location.pathname] || "Fieldbook";

  return (
    <div className="app-frame">
      <div className="top-bar">
        <h1>{title}</h1>
        <div className="top-bar-actions">
          <button onClick={handleLogout}>Log out</button>
        </div>
      </div>

      <div className="screen-body">
        <Outlet />
      </div>

      <nav className="bottom-nav">
        <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
          <span className="nav-icon">👥</span>
          Customers
        </NavLink>
        <NavLink to="/products" className={({ isActive }) => (isActive ? "active" : "")}>
          <span className="nav-icon">📦</span>
          Products
        </NavLink>
        <NavLink to="/new-order" className={({ isActive }) => (isActive ? "active" : "")}>
          <span className="nav-icon">➕</span>
          New Order
        </NavLink>
        <NavLink to="/history" className={({ isActive }) => (isActive ? "active" : "")}>
          <span className="nav-icon">🧾</span>
          History
        </NavLink>
      </nav>
    </div>
  );
}
