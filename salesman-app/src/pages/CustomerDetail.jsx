import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import api from "../api";
import { useCart } from "../context/CartContext";

export default function CustomerDetail() {
  const { customerId } = useParams();
  const [customer, setCustomer] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { setCustomer: setCartCustomer } = useCart();

  useEffect(() => {
    async function load() {
      try {
        const resp = await api.get(`/api/customers/${customerId}`);
        setCustomer(resp.data);
      } catch (err) {
        setError(err?.response?.status === 404 ? "Customer not found." : "Couldn't load customer.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [customerId]);

  function startOrder() {
    setCartCustomer(customer);
    navigate("/new-order");
  }

  if (loading) return <div className="loading-state">Loading…</div>;
  if (error) return <div className="error-banner">{error}</div>;
  if (!customer) return null;

  return (
    <>
      <Link to="/" className="back-link" style={{ display: "block", marginBottom: 14, color: "var(--ink-muted)", fontSize: 13.5 }}>
        ← Back to customers
      </Link>

      <div className="detail-header">
        <h2>{customer.name}</h2>
        <div className="sub">Customer details</div>
      </div>

      <div className="detail-section">
        <div className="detail-row">
          <label>Phone</label>
          <span>{customer.phone || "—"}</span>
        </div>
        <div className="detail-row">
          <label>Email</label>
          <span>{customer.email || "—"}</span>
        </div>
        <div className="detail-row">
          <label>Address</label>
          <span style={{ textAlign: "right", maxWidth: 220 }}>{customer.address || "—"}</span>
        </div>
      </div>

      <button className="btn-primary" onClick={startOrder}>
        Start order for {customer.name}
      </button>
    </>
  );
}
