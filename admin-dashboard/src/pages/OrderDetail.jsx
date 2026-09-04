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
      <Link to="/orders" className="back-link">← Back to orders</Link>
      <h1 className="page-title">Order detail</h1>

      {loading && <div className="loading-state">Loading…</div>}
      {error && <div className="error-banner">{error}</div>}

      {order && (
        <>
          <div className="detail-card">
            <div className="detail-grid">
              <div className="detail-row">
                <label>Customer</label>
                <div className="value">{order.customer_name}</div>
              </div>
              <div className="detail-row">
                <label>Salesman</label>
                <div className="value">{order.salesman_name}</div>
              </div>
              <div className="detail-row">
                <label>Date placed</label>
                <div className="value">{formatDateTime(order.created_at)}</div>
              </div>
              <div className="detail-row">
                <label>Status</label>
                <div className="value">
                  <span className={`status-pill status-${order.status}`}>{order.status}</span>
                </div>
              </div>
            </div>
          </div>

          <table className="ledger-table">
            <thead>
              <tr>
                <th>Product</th>
                <th className="num">Quantity</th>
                <th className="num">Unit price</th>
                <th className="num">Subtotal</th>
              </tr>
            </thead>
            <tbody>
              {order.items.map((item) => (
                <tr key={item.id} style={{ cursor: "default" }}>
                  <td>{item.product_name}</td>
                  <td className="num">{item.quantity}</td>
                  <td className="num">{formatCurrency(item.unit_price)}</td>
                  <td className="num">{formatCurrency(item.subtotal)}</td>
                </tr>
              ))}
              <tr style={{ cursor: "default" }}>
                <td colSpan={3} style={{ textAlign: "right", fontWeight: 600 }}>Total</td>
                <td className="num" style={{ fontWeight: 600 }}>{formatCurrency(order.total_amount)}</td>
              </tr>
            </tbody>
          </table>
        </>
      )}
    </>
  );
}
