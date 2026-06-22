export function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton-line" style={{ width: '35%', height: '14px', marginBottom: '16px' }} />
      <div className="skeleton-line" style={{ width: '70%', height: '22px', marginBottom: '8px' }} />
      <div className="skeleton-line" style={{ width: '90%', height: '14px', marginBottom: '4px' }} />
      <div className="skeleton-line" style={{ width: '60%', height: '14px', marginBottom: '20px' }} />
      <div className="skeleton-line" style={{ width: '40%', height: '36px', borderRadius: '999px' }} />
    </div>
  );
}

const COL_W = [75, 55, 85, 65, 45, 70, 60, 50];
const ROW_W = [65, 50, 80, 55, 70, 60, 45, 75];

export function SkeletonTable({ rows = 4, cols = 4 }) {
  return (
    <div className="skeleton-table">
      <div className="skeleton-row skeleton-header">
        {Array.from({ length: cols }).map((_, i) => (
          <div key={i} className="skeleton-line" style={{ width: `${COL_W[i % COL_W.length]}%`, height: '14px' }} />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, r) => (
        <div key={r} className="skeleton-row">
          {Array.from({ length: cols }).map((_, c) => (
            <div key={c} className="skeleton-line" style={{ width: `${ROW_W[(r * cols + c) % ROW_W.length]}%`, height: '14px' }} />
          ))}
        </div>
      ))}
    </div>
  );
}
