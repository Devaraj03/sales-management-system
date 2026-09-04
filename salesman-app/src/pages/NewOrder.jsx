import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api";
import { useCart } from "../context/CartContext";

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(Number(value));
}

function CustomerPicker({ onSelect }) {
  const [search, setSearch] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const timeout = setTimeout(async () => {
      setLoading(true);
      try {
        const resp = await api.get("/api/customers", { params: search ? { search } : {} });
        setResults(resp.data);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);
    return () => clearTimeout(timeout);
  }, [search]);

  return (
    <>
      <p style={{ color: "var(--ink-muted)", fontSize: 14, marginBottom: 12 }}>
        Choose a customer to start this order.
      </p>
      <input
        className="search-input"
        type="text"
        placeholder="Search customers…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        autoFocus
      />
      {loading && <div className="loading-state">Loading…</div>}
      <div className="card-list">
        {results.map((c) => (
          <div key={c.id} className="list-card" onClick={() => onSelect(c)}>
            <div>
              <div className="list-card-title">{c.name}</div>
              <div className="list-card-sub">{c.phone || c.email || "No contact info"}</div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

export default function NewOrder() {
  const { customer, setCustomer, items, updateQuantity, removeItem, clearCart, total } = useCart();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit() {
    setError("");

    if (!customer) {
      setError("Select a customer first.");
      return;
    }
    if (items.length === 0) {
      setError("Add at least one product to the order.");
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        customer_id: customer.id,
        items: items.map((i) => ({ product_id: i.product.id, quantity: i.quantity })),
      };
      const resp = await api.post("/api/orders", payload);
      clearCart();
      navigate(`/history/${resp.data.id}`, { replace: true });
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Couldn't submit the order. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  if (!customer) {
    return <CustomerPicker onSelect={setCustomer} />;
  }

  return (
    <>
      <div className="detail-section" style={{ marginBottom: 16 }}>
        <div className="detail-row">
          <label>Customer</label>
          <span>{customer.name}</span>
        </div>
        <button
          className="btn-secondary"
          style={{ marginTop: 10 }}
          onClick={() => setCustomer(null)}
        >
          Change customer
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="section-label">Items ({items.length})</div>

      {items.length === 0 && (
        <div className="empty-state">
          No items yet.
          <br />
          <Link to="/products" style={{ color: "var(--blue)", fontWeight: 600 }}>
            Browse products →
          </Link>
        </div>
      )}

      {items.map((i) => (
        <div className="cart-item" key={i.product.id}>
          <div className="cart-item-top">
            <span className="cart-item-name">{i.product.name}</span>
            <span className="cart-item-price">{formatCurrency(i.product.price)} each</span>
          </div>
          <div className="cart-item-bottom">
            <div className="stepper">
              <button onClick={() => updateQuantity(i.product.id, i.quantity - 1)}>−</button>
              <span>{i.quantity}</span>
              <button
                onClick={() => updateQuantity(i.product.id, i.quantity + 1)}
                disabled={i.quantity >= i.product.stock_quantity}
              >
                +
              </button>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <strong>{formatCurrency(i.product.price * i.quantity)}</strong>
              <button className="remove-link" onClick={() => removeItem(i.product.id)}>
                Remove
              </button>
            </div>
          </div>
        </div>
      ))}

      {items.length > 0 && (
        <Link to="/products" style={{ display: "block", textAlign: "center", color: "var(--blue)", fontWeight: 600, fontSize: 14, marginTop: 10 }}>
          + Add another product
        </Link>
      )}

      {items.length > 0 && (
        <div className="order-total-bar">
          <div className="order-total-row">
            <span className="label">Order total</span>
            <span className="value">{formatCurrency(total)}</span>
          </div>
          <button className="btn-primary" onClick={handleSubmit} disabled={submitting}>
            {submitting ? "Submitting…" : "Submit order"}
          </button>
        </div>
      )}
    </>
  );
}
