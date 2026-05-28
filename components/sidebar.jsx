// Sidebar
function Sidebar({ active, onChange }) {
  const groups = [
    { label: "Operação", items: [
      { id: "dashboard", icon: "dashboard", label: "Dashboard" },
      { id: "asn", icon: "globe", label: "ASN Manager" },
      { id: "hosts", icon: "server", label: "Host Manager" },
    ]},
    { label: "Diagnóstico", items: [
      { id: "discovery", icon: "radar", label: "Autodescoberta" },
      { id: "tools", icon: "tools", label: "Network Tools" },
      { id: "logs", icon: "terminal", label: "Console de Logs" },
    ]},
    { label: "Sistema", items: [
      { id: "settings", icon: "settings", label: "Configurações" },
    ]},
  ];
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark"><Icon name="logo" size={20}/></div>
        <div>
          <div className="brand-name">fz<span className="accent">BGP</span>Tools</div>
          <div className="brand-sub">Peering Mapper</div>
        </div>
      </div>
      <div className="nav">
        {groups.map(g => (
          <React.Fragment key={g.label}>
            <div className="nav-label">{g.label}</div>
            {g.items.map(it => (
              <div key={it.id}
                   className={"nav-item" + (active === it.id ? " active" : "")}
                   onClick={() => onChange(it.id)}>
                <Icon name={it.icon} size={17}/>
                <span>{it.label}</span>
              </div>
            ))}
          </React.Fragment>
        ))}
      </div>
      <div className="sidebar-footer">
        <div className="status-pill">
          <span className="dot"></span>
          Monitorando
          <small>AS263870</small>
        </div>
        <div className="user-card">
          <div className="user-avatar">NA</div>
          <div>
            <div className="name">netadmin</div>
            <div className="role">Webstorage NOC</div>
          </div>
        </div>
      </div>
    </aside>
  );
}

window.Sidebar = Sidebar;
