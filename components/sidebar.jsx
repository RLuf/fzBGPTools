// Sidebar
function Sidebar({ active, onChange }) {
  const [checkingUpdate, setCheckingUpdate] = useState(false);
  const [updateState, setUpdateState] = useState("idle"); // idle | checking | uptodate | available

  const checkUpdate = () => {
    // TODO: futuramente consultar https://fzrepo.rogerluft.com.br (Gitea API)
    // GET /api/v1/repos/webstorage/fzBGPTools/releases/latest → compare tag_name com __version__
    setCheckingUpdate(true);
    setUpdateState("checking");
    setTimeout(() => {
      setCheckingUpdate(false);
      // Mock: 50% chance — só pra ilustrar o estado visual
      setUpdateState(Math.random() > 0.5 ? "available" : "uptodate");
      setTimeout(() => setUpdateState("idle"), 4000);
    }, 1400);
  };

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
          <div className="brand-copyright">© Webstorage Tecnologia</div>
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

        {/* Upgrade button — placeholder; futuramente consultará fzrepo.rogerluft.com.br */}
        <button className={"upgrade-btn upgrade-" + updateState} onClick={checkUpdate} disabled={checkingUpdate}>
          <Icon name={updateState === "available" ? "download" : "refresh"} size={14}/>
          <span>
            {updateState === "checking"  && "Verificando…"}
            {updateState === "available" && "Atualização disponível"}
            {updateState === "uptodate"  && "✓ Atualizado"}
            {updateState === "idle"      && "Verificar atualização"}
          </span>
        </button>

        <div className="user-card">
          <div className="user-avatar">NA</div>
          <div>
            <div className="name">netadmin</div>
            <div className="role">Webstorage NOC</div>
          </div>
        </div>

        {/* Author + Licença CC BY 4.0 */}
        <div className="sidebar-author">
          Eng. <a href="https://about.rogerluft.com.br" target="_blank" rel="noopener" title="roger@webstorage.com.br">Roger Luft</a>
        </div>
        <div className="sidebar-license">
          <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">
            <span className="cc-icon">CC</span>
            <span className="cc-icon">BY</span>
            <span>4.0</span>
          </a>
        </div>
      </div>
    </aside>
  );
}

window.Sidebar = Sidebar;
