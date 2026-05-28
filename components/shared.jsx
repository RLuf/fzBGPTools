// Icons + shared components
const { useState, useEffect, useRef, useMemo, useCallback } = React;

const Icon = ({ name, size = 18, stroke = 1.6 }) => {
  const p = { width: size, height: size, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: stroke, strokeLinecap: "round", strokeLinejoin: "round" };
  switch (name) {
    case "dashboard":
      return (<svg {...p}><path d="M3 12l9-9 9 9"/><path d="M5 10v10h14V10"/><path d="M9 20v-6h6v6"/></svg>);
    case "globe":
      return (<svg {...p}><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 010 18M12 3a14 14 0 000 18"/></svg>);
    case "server":
      return (<svg {...p}><rect x="3" y="4" width="18" height="6" rx="2"/><rect x="3" y="14" width="18" height="6" rx="2"/><path d="M7 7h.01M7 17h.01"/></svg>);
    case "tools":
      return (<svg {...p}><path d="M14.7 6.3a4 4 0 015.7 5.7l-6.4 6.4-5.7-5.7 6.4-6.4z"/><path d="M3 21l5-5"/></svg>);
    case "terminal":
      return (<svg {...p}><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 9l3 3-3 3M13 15h4"/></svg>);
    case "settings":
      return (<svg {...p}><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 00.3 1.8l.1.1a2 2 0 11-2.8 2.8l-.1-.1a1.7 1.7 0 00-1.8-.3 1.7 1.7 0 00-1 1.5V21a2 2 0 11-4 0v-.1a1.7 1.7 0 00-1-1.5 1.7 1.7 0 00-1.8.3l-.1.1a2 2 0 11-2.8-2.8l.1-.1a1.7 1.7 0 00.3-1.8 1.7 1.7 0 00-1.5-1H3a2 2 0 110-4h.1a1.7 1.7 0 001.5-1 1.7 1.7 0 00-.3-1.8l-.1-.1a2 2 0 112.8-2.8l.1.1a1.7 1.7 0 001.8.3H9a1.7 1.7 0 001-1.5V3a2 2 0 114 0v.1a1.7 1.7 0 001 1.5 1.7 1.7 0 001.8-.3l.1-.1a2 2 0 112.8 2.8l-.1.1a1.7 1.7 0 00-.3 1.8V9a1.7 1.7 0 001.5 1H21a2 2 0 110 4h-.1a1.7 1.7 0 00-1.5 1z"/></svg>);
    case "search":
      return (<svg {...p}><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>);
    case "plus":
      return (<svg {...p}><path d="M12 5v14M5 12h14"/></svg>);
    case "edit":
      return (<svg {...p}><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 113 3L7 19l-4 1 1-4 12.5-12.5z"/></svg>);
    case "trash":
      return (<svg {...p}><path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/></svg>);
    case "upload":
      return (<svg {...p}><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>);
    case "download":
      return (<svg {...p}><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>);
    case "ping":
      return (<svg {...p}><path d="M3 12h3l3-9 6 18 3-9h3"/></svg>);
    case "route":
      return (<svg {...p}><circle cx="6" cy="19" r="2"/><circle cx="18" cy="5" r="2"/><path d="M6 17V9a4 4 0 014-4h4a4 4 0 014 4v0"/></svg>);
    case "ssh":
      return (<svg {...p}><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 9l3 3-3 3M14 15h4"/></svg>);
    case "telnet":
      return (<svg {...p}><path d="M4 4h16v12H4z"/><path d="M2 20h20"/><path d="M9 8l3 3-3 3"/></svg>);
    case "play":
      return (<svg {...p}><path d="M6 4l14 8-14 8V4z"/></svg>);
    case "pause":
      return (<svg {...p}><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>);
    case "filter":
      return (<svg {...p}><path d="M3 4h18l-7 9v6l-4 2v-8L3 4z"/></svg>);
    case "alert":
      return (<svg {...p}><path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9L1.8 18a2 2 0 001.7 3h17a2 2 0 001.7-3L13.7 3.9a2 2 0 00-3.4 0z"/></svg>);
    case "bell":
      return (<svg {...p}><path d="M6 8a6 6 0 1112 0c0 7 3 9 3 9H3s3-2 3-9M14 21a2 2 0 11-4 0"/></svg>);
    case "x":
      return (<svg {...p}><path d="M18 6L6 18M6 6l12 12"/></svg>);
    case "zoom-in":
      return (<svg {...p}><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3M11 8v6M8 11h6"/></svg>);
    case "zoom-out":
      return (<svg {...p}><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3M8 11h6"/></svg>);
    case "fit":
      return (<svg {...p}><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>);
    case "wifi":
      return (<svg {...p}><path d="M5 12a10 10 0 0114 0M8.5 15.5a5 5 0 017 0M12 19h.01M2 8.8a15 15 0 0120 0"/></svg>);
    case "router":
      return (<svg {...p}><rect x="2" y="14" width="20" height="8" rx="2"/><path d="M6.01 18H6M10 18h.01M15 10V6a3 3 0 016 0M11 10V8a3 3 0 00-3-3 3 3 0 00-3 3"/></svg>);
    case "chevron":
      return (<svg {...p}><path d="M9 18l6-6-6-6"/></svg>);
    case "copy":
      return (<svg {...p}><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>);
    case "refresh":
      return (<svg {...p}><path d="M21 12a9 9 0 11-3-6.7L21 8"/><path d="M21 3v5h-5"/></svg>);
    case "database":
      return (<svg {...p}><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0018 0V5M3 12a9 3 0 0018 0"/></svg>);
    case "radar":
      return (<svg {...p}><path d="M19.07 4.93A10 10 0 0017.62 19a10 10 0 11.93-15"/><path d="M12 12L17 7"/><circle cx="12" cy="12" r="2"/></svg>);
    case "mail":
      return (<svg {...p}><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>);
    case "shield":
      return (<svg {...p}><path d="M12 2l8 4v6c0 5-3.5 9.5-8 10-4.5-.5-8-5-8-10V6l8-4z"/></svg>);
    case "scan":
      return (<svg {...p}><path d="M3 7V5a2 2 0 012-2h2M17 3h2a2 2 0 012 2v2M21 17v2a2 2 0 01-2 2h-2M7 21H5a2 2 0 01-2-2v-2M7 12h10"/></svg>);
    case "eye":
      return (<svg {...p}><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z"/><circle cx="12" cy="12" r="3"/></svg>);
    case "logo":
      return (<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2.1 2.1M16.9 16.9L19 19M5 19l2.1-2.1M16.9 7.1L19 5"/></svg>);
    default: return null;
  }
};

// Pill / Badge helpers (component form not required — using classes)

function Modal({ title, onClose, children, footer, width = 560 }) {
  useEffect(() => {
    const onKey = (e) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);
  return (
    <div className="modal-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="modal" style={{ width: `min(${width}px, 92vw)` }}>
        <div className="modal-header">
          <h3>{title}</h3>
          <div style={{ flex: 1 }}></div>
          <button className="icon-btn" onClick={onClose}><Icon name="x" size={16}/></button>
        </div>
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-footer">{footer}</div>}
      </div>
    </div>
  );
}

function Field({ label, children, full }) {
  return (
    <div className="field" style={full ? { gridColumn: "1 / -1" } : undefined}>
      <label>{label}</label>
      {children}
    </div>
  );
}

function Search({ value, onChange, placeholder = "Buscar...", width }) {
  return (
    <div className="search" style={width ? { width } : undefined}>
      <Icon name="search" size={14}/>
      <input value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} />
    </div>
  );
}

function PageHead({ title, accent, sub, actions }) {
  return (
    <div className="page-head">
      <div className="title-block">
        <h2>{title} <span className="accent">{accent}</span></h2>
        {sub && <div className="sub">{sub}</div>}
      </div>
      {actions && <div className="tools">{actions}</div>}
    </div>
  );
}

window.Icon = Icon;
window.Modal = Modal;
window.Field = Field;
window.Search = Search;
window.PageHead = PageHead;
