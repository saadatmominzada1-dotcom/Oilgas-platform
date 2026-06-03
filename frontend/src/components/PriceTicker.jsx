import { useState, useEffect } from 'react';
import { fetchPrices } from '../utils/api';

export default function PriceTicker() {
  const [prices, setPrices] = useState([]);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchPrices();
        setPrices(data);
      } catch (e) {
        // Fail silently
      }
    };
    load();
    const interval = setInterval(load, 5 * 60 * 1000); // refresh every 5 min
    return () => clearInterval(interval);
  }, []);

  if (!prices.length) return null;

  // Duplicate for seamless scroll animation
  const doubled = [...prices, ...prices];

  return (
    <div className="ticker-bar">
      <div className="ticker-label">LIVE</div>
      <div className="ticker-items">
        {doubled.map((p, i) => (
          <div key={i} className="ticker-item">
            <span className="ticker-name">{p.label}</span>
            <span className="ticker-value">{p.value?.toFixed(2)}</span>
            <span className={`ticker-change ${p.change >= 0 ? 'up' : 'down'}`}>
              {p.change >= 0 ? '+' : ''}{p.change?.toFixed(2)} {p.unit}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
