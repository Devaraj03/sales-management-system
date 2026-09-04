import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../api";

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(Number(value));
}

function formatDateTime(iso) {
  return new Date(iso).toLocaleString("en-US", {
    year: "numeric", month: "short", day: "numeric", hour: "numeric", minute: "2-digit",
  });
}

export default function OrderDetail() {
  const { orderId } = useParams();
  const [order, setOrder] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const resp = await api.get(`/api/orders/${orderId}`);
        setOrder(resp.data);
      } catch (err) {
        setError(
          err?.response?.status === 404
            ? "This order could not be found."
            : err?.response?.status === 403
            ? "You don't have access to this order."
            : "Couldn't load this order."
        );
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [orderId]);

  return (
    <>
      <Link to="/history" style={{ display: "block", marginBottom: 14, color: "var(--ink-muted)", fontSize: 13.5 }}>
        ← Back to history
      </Link>

      {loading && <div className="loading-state">Loading…</div>}
      {error && <div className="error-banner">{error}</div>}

      {order && (
        <>
          <div className="detail-header">
            <h2>{order.customer_name}</h2>
            <div className="sub">{formatDateTime(order.created_at)}</div>
          </div>

          <div className="detail-section">
            <div className="detail-row">
              <label>Status</label>
              <span className={`status-pill status-${order.status}`}>{order.status}</span>
            </div>
            <div className="detail-row">
              <label>Total</label>
              <strong>{formatCurrency(order.total_amount)}</strong>
            </div>
          </div>

          <div className="section-label">Items</div>
          {order.items.map((item) => (
            <div className="cart-item" key={item.id}>
              <div className="cart-item-top">
                <span className="cart-item-name">{item.product_name}</span>
                <span className="cart-item-price">{formatCurrency(item.unit_price)} each</span>
              </div>
              <div className="cart-item-bottom">
                <span style={{ color: "var(--ink-muted)", fontSize: 13.5 }}>Qty {item.quantity}</span>
                <strong>{formatCurrency(item.subtotal)}</strong>
              </div>
            </div>
          ))}
        </>
      )}
    </>
  );
}
