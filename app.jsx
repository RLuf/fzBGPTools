// Main app shell — routes + tweaks

const SCREEN_TITLES = {
  dashboard: { crumb: "Operação", page: "Dashboard" },
  asn:       { crumb: "Operação", page: "ASN Manager" },
  hosts:     { crumb: "Operação", page: "Host Manager" },
  discovery: { crumb: "Diagnóstico", page: "Autodescoberta" },
  tools:     { crumb: "Diagnóstico", page: "Network Tools" },
  logs:      { crumb: "Diagnóstico", page: "Console de Logs" },
  settings:  { crumb: "Sistema", page: "Configurações" },
};

// Mock alerts — em runtime real virá da tabela `alerts` do SQLite
const TOPBAR_ALERTS = [
  { id: 1, sev: "critical", title: "Prepend detection",
    desc: "AS174 está fazendo AS-Path prepend (3x) em 200.149.0.0/16",
    time: "há 3 min" },
  { id: 2, sev: "critical", title: "Route flapping",
    desc: "Prefixo 187.45.128.0/19 oscilou 8 vezes em 15 min via AS12956",
    time: "há 7 min" },
  { id: 3, sev: "warn",     title: "MED change",
    desc: "Telefônica alterou MED de 100 → 250 em 17 prefixos",
    time: "há 12 min" },
];

function AlertsButton() {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  const count = TOPBAR_ALERTS.length;
  const criticalCount = TOPBAR_ALERTS.filter(a => a.sev === "critical").length;
  const hasCritical = criticalCount > 0;

  // Fecha ao clicar fora
  useEffect(() => {
    if (!open) return;
    const onClick = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    const onKey = (e) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", onClick);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onClick);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  return (
    <div className="alerts-wrap" ref={ref}>
      <button
        className={"alerts-btn" + (hasCritical ? " has-critical" : "") + (open ? " is-open" : "")}
        title={`${count} alerta${count !== 1 ? "s" : ""}`}
        onClick={() => setOpen(o => !o)}>
        <Icon name="bell" size={16}/>
        {count > 0 && <span className="alerts-count">{count > 99 ? "99+" : count}</span>}
      </button>

      {open && (
        <div className="alerts-dropdown">
          <div className="alerts-head">
            <Icon name="bell" size={14}/>
            <span>Alertas BGP</span>
            <span className="badge badge-red" style={{ marginLeft: "auto" }}>
              {criticalCount} crítico{criticalCount !== 1 ? "s" : ""}
            </span>
          </div>
          <div className="alerts-list">
            {TOPBAR_ALERTS.map(a => (
              <div key={a.id} className={"alerts-item sev-" + a.sev}>
                <div className={"alerts-ico " + a.sev}>
                  <Icon name="alert" size={14}/>
                </div>
                <div className="alerts-body">
                  <div className="alerts-title">{a.title}</div>
                  <div className="alerts-desc">{a.desc}</div>
                  <div className="alerts-time">{a.time}</div>
                </div>
              </div>
            ))}
          </div>
          <div className="alerts-foot">
            <button className="btn btn-sm btn-ghost" onClick={() => setOpen(false)}>
              Marcar tudo como lido
            </button>
            <button className="btn btn-sm btn-primary"
                    onClick={() => { setOpen(false); /* navegar p/ dashboard */ }}>
              Ver no Dashboard
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "theme": "aurora",
  "density": "comfortable",
  "headline": "fzBGPTools"
}/*EDITMODE-END*/;

function App() {
  const [screen, setScreen] = useState("dashboard");
  const [t, setTweak] = window.useTweaks ? window.useTweaks(TWEAK_DEFAULTS) : [TWEAK_DEFAULTS, () => {}];

  const cls = "app theme-" + (t.theme || "aurora") + (t.density === "dense" ? " dense" : "");
  const titleMeta = SCREEN_TITLES[screen];

  return (
    <div className={cls}>
      <Sidebar active={screen} onChange={setScreen}/>
      <main className="main">
        <div className="topbar">
          <div className="crumb">{titleMeta.crumb} / <b>{titleMeta.page}</b></div>
          <div className="spacer"></div>
          <Search value="" onChange={() => {}} placeholder="Buscar ASN, IP, hostname..." width={320}/>
          <span className="kbd">⌘K</span>
          <AlertsButton/>
          <button className="icon-btn" title="Atualizar"><Icon name="refresh" size={16}/></button>
        </div>

        <div className="view">
          {screen === "dashboard" && <Dashboard/>}
          {screen === "asn"       && <AsnManager/>}
          {screen === "hosts"     && <HostManager/>}
          {screen === "discovery" && <Discovery/>}
          {screen === "tools"     && <NetworkTools/>}
          {screen === "logs"      && <LogsConsole/>}
          {screen === "settings"  && <Settings/>}
        </div>
      </main>

      {/* Tweaks panel */}
      {window.TweaksPanel && (
        <window.TweaksPanel title="Tweaks">
          <window.TweakSection label="Tema visual">
            <window.TweakRadio
              label="Paleta neon"
              value={t.theme}
              onChange={(v) => setTweak("theme", v)}
              options={[
                { value: "aurora",  label: "Aurora" },
                { value: "emerald", label: "Emerald" },
                { value: "magenta", label: "Magenta" },
                { value: "amber",   label: "Amber" },
              ]}
            />
            <window.TweakRadio
              label="Densidade"
              value={t.density}
              onChange={(v) => setTweak("density", v)}
              options={[
                { value: "comfortable", label: "Confortável" },
                { value: "dense",       label: "Densa" },
              ]}
            />
          </window.TweakSection>
        </window.TweaksPanel>
      )}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
