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
          <button className="icon-btn" title="Alertas">
            <div style={{ position: "relative" }}>
              <Icon name="bell" size={16}/>
              <span style={{
                position: "absolute", top: -4, right: -4,
                width: 8, height: 8, borderRadius: "50%",
                background: "var(--red)", boxShadow: "0 0 8px var(--red)"
              }}></span>
            </div>
          </button>
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
