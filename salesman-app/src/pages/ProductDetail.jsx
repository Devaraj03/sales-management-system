import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../api";
import { useCart } from "../context/CartContext";

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(Number(value));
}

export default function ProductDetail() {
  const { productId } = useParams();
  const [product, setProduct] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [added, setAdded] = useState(false);
  const { addItem } = useCart();

  useEffect(() => {
    async function load() {
      try {
        const resp = await api.get(`/api/products/${productId}`);
        setProduct(resp.data);
      } catch (err) {
        setError(err?.response?.status === 404 ? "Product not found." : "Couldn't load product.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [productId]);

  function handleAdd() {
    addItem(product, 1);
    setAdded(true);
    setTimeout(() => setAdded(false), 1500);
  }

  if (loading) return <div className="loading-state">Loading…</div>;
  if (error) return <div className="error-banner">{error}</div>;
  if (!product) return null;

  return (
    <>
      <Link to="/products" className="back-link" style={{ display: "block", marginBottom: 14, color: "var(--ink-muted)", fontSize: 13.5 }}>
        ← Back to products
      </Link>

      <div className="detail-header">
        <h2>{product.name}</h2>
        <div className="sub">{product.sku}</div>
      </div>

      {added && <div className="success-banner">Added to current order.</div>}

      <div className="detail-section">
        <div className="detail-row">
          <label>Price</label>
          <span>{formatCurrency(product.price)}</span>
        </div>
        <div className="detail-row">
          <label>In stock</label>
          <span>{product.stock_quantity}</span>
        </div>
        {product.description && (
          <div className="detail-row" style={{ display: "block" }}>
            <label>Description</label>
            <p style={{ margin: "6px 0 0", fontSize: 14 }}>{product.description}</p>
          </div>
        )}
      </div>

      <button className="btn-primary" onClick={handleAdd} disabled={product.stock_quantity === 0}>
        {product.stock_quantity === 0 ? "Out of stock" : "Add to order"}
      </button>
    </>
  );
}
