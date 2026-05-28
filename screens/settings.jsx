// Settings screen

function Settings() {
  const tables = [
    { name: "asns",     count: 247, size: "412 KB" },
    { name: "hosts",    count:  38, size: "118 KB" },
    { name: "sessions", count:  14, size: " 64 KB" },
    { name: "logs",     count: 18429, size: "21.4 MB" },
    { name: "traces",   count:  892, size: "8.7 MB" },
    { name: "snapshots",count:   12, size: "152 MB" },
  ];

  return (
    <div data-screen-label="06 Settings">
      <PageHead
        title=""
        accent="Configurações"
        sub="Backup, restore, importação e informações do sistema."
      />

      <InstallerCard/>

      <div className="settings-grid">
        <div className="card">
          <div className="card-header">
            <Icon name="database" size={16}/>
            <h3>Banco de Dados <span className="accent">SQLite</span></h3>
          </div>          <div className="card-body" style={{ display: "grid", gap: 14 }}>
            <dl className="kv">
              <dt>Arquivo</dt><dd>/var/lib/fzbgp/peering.db</dd>
              <dt>Tamanho</dt><dd>182.3 MB <span style={{ color: "var(--text-mute)" }}>/ 2.0 GB</span></dd>
              <dt>Última escrita</dt><dd>2026-05-26 14:08:51</dd>
              <dt>Esquema</dt><dd>v3.4.2 (migrações aplicadas)</dd>
              <dt>Integridade</dt><dd style={{ color: "var(--green)" }}>OK · PRAGMA integrity_check</dd>
            </dl>
            <div className="bar"><span style={{ width: "9%" }}></span></div>

            <div style={{ marginTop: 6, fontSize: 11.5, color: "var(--text-mute)", textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 600 }}>Registros por tabela</div>
            <table className="t" style={{ background: "transparent" }}>
              <tbody>
                {tables.map(t => (
                  <tr key={t.name}>
                    <td style={{ padding: "8px 0", borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                      <span className="mono" style={{ fontSize: 12 }}>{t.name}</span>
                    </td>
                    <td style={{ padding: "8px 0", textAlign: "right", borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                      <span className="mono" style={{ color: "var(--text-dim)" }}>{t.count.toLocaleString()}</span>
                    </td>
                    <td style={{ padding: "8px 0", textAlign: "right", borderBottom: "1px solid rgba(255,255,255,0.04)", width: 90 }}>
                      <span className="mono" style={{ color: "var(--text-mute)", fontSize: 11.5 }}>{t.size}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <button className="btn btn-primary"><Icon name="download" size={13}/>Backup (.db)</button>
              <button className="btn"><Icon name="upload" size={13}/>Restore (.db)</button>
              <button className="btn btn-danger"><Icon name="trash" size={13}/>Resetar BD</button>
            </div>
          </div>
        </div>

        <div style={{ display: "grid", gap: 18 }}>
          <SmtpAlertsCard/>
          <div className="card">
            <div className="card-header">
              <Icon name="upload" size={16}/>
              <h3>Importar / <span className="accent">Exportar</span></h3>
            </div>
            <div className="card-body" style={{ display: "grid", gap: 12 }}>
              <SettingRow
                title="Configuração completa (JSON)"
                desc="Exporta todo o estado do sistema — ASNs, hosts, sessões, configurações."
                actions={<>
                  <button className="btn btn-sm"><Icon name="upload" size={12}/>Importar</button>
                  <button className="btn btn-sm btn-primary"><Icon name="download" size={12}/>Exportar</button>
                </>}
              />
              <SettingRow
                title="Lista de ASNs (CSV)"
                desc="Importe ASNs em massa: ASN, org, ranges, país, tipo."
                actions={<button className="btn btn-sm"><Icon name="upload" size={12}/>Importar CSV</button>}
              />
              <SettingRow
                title="Lista de Hosts (CSV)"
                desc="Importe hosts em massa: hostname, IP, porta, usuário, tipo, fabricante."
                actions={<button className="btn btn-sm"><Icon name="upload" size={12}/>Importar CSV</button>}
              />
              <SettingRow
                title="Snapshot de prefixos BGP"
                desc="Exporte tabela RIB completa em formato MRT ou JSON."
                actions={<>
                  <button className="btn btn-sm">MRT</button>
                  <button className="btn btn-sm">JSON</button>
                </>}
              />
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <Icon name="settings" size={16}/>
              <h3>Sobre o <span className="accent">Sistema</span></h3>
            </div>
            <div className="card-body">
              <dl className="kv">
                <dt>Versão</dt><dd>fzBGPTools v3.4.2 <span className="badge badge-green" style={{ marginLeft: 8 }}>estável</span></dd>
                <dt>Build</dt><dd>#2026.05.26-a91f3c4</dd>
                <dt>Sistema operacional</dt><dd>Linux Debian 12.5 · kernel 6.1.0-20-amd64</dd>
                <dt>Python</dt><dd>3.11.8</dd>
                <dt>Node.js</dt><dd>20.12.2 LTS</dd>
                <dt>SQLite</dt><dd>3.45.1</dd>
                <dt>Uptime</dt><dd>14d 6h 22m</dd>
                <dt>Licença</dt><dd>MIT · github.com/fznetwork/fzbgptools</dd>
              </dl>
              <div style={{ display: "flex", gap: 8, marginTop: 14 }}>
                <button className="btn btn-sm"><Icon name="refresh" size={12}/>Verificar atualizações</button>
                <button className="btn btn-sm">Documentação</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function SettingRow({ title, desc, actions }) {
  return (
    <div style={{
      display: "flex", gap: 12, alignItems: "center",
      padding: 12, borderRadius: 10,
      border: "1px solid var(--border)",
      background: "rgba(255,255,255,0.015)"
    }}>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 13, fontWeight: 600 }}>{title}</div>
        <div style={{ fontSize: 11.5, color: "var(--text-mute)", marginTop: 2 }}>{desc}</div>
      </div>
      <div style={{ display: "flex", gap: 6 }}>{actions}</div>
    </div>
  );
}

function SmtpAlertsCard() {
  const [smtp, setSmtp] = useState({
    host: "smtp.sendgrid.net",
    port: 587,
    user: "apikey",
    password: "SG.********************",
    from: "noc@webstorage.net",
    fromName: "fzBGPTools NOC",
    tls: "STARTTLS",
    enabled: true,
  });
  const [recipients, setRecipients] = useState([
    { email: "noc@webstorage.net",       sev: ["CRITICAL", "ERROR"],          desc: "Plantão 24/7" },
    { email: "peering@webstorage.net",   sev: ["CRITICAL", "ERROR", "WARN"],  desc: "Eventos BGP" },
    { email: "infra-lead@webstorage.net",sev: ["CRITICAL"],                    desc: "Apenas críticos" },
  ]);
  const [adding, setAdding] = useState(false);
  const [newEmail, setNewEmail] = useState({ email: "", sev: ["CRITICAL"], desc: "" });
  const [testStatus, setTestStatus] = useState(null);

  const set = (k, v) => setSmtp({ ...smtp, [k]: v });

  const sendTest = () => {
    setTestStatus("sending");
    setTimeout(() => setTestStatus("ok"), 1400);
    setTimeout(() => setTestStatus(null), 4000);
  };

  const toggleSev = (idx, sev) => {
    setRecipients(prev => prev.map((r, i) => {
      if (i !== idx) return r;
      const next = r.sev.includes(sev) ? r.sev.filter(s => s !== sev) : [...r.sev, sev];
      return { ...r, sev: next };
    }));
  };

  return (
    <div className="card">
      <div className="card-header">
        <Icon name="mail" size={16}/>
        <h3>SMTP & <span className="accent">Alertas por Email</span></h3>
        <div className="spacer"></div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }}>
          <span style={{ fontSize: 11.5, color: smtp.enabled ? "var(--green)" : "var(--text-mute)" }}>
            {smtp.enabled ? "Ativo" : "Desativado"}
          </span>
          <input type="checkbox" checked={smtp.enabled} onChange={(e) => set("enabled", e.target.checked)} style={{ display: "none" }}/>
          <div style={{
            width: 36, height: 20, borderRadius: 10,
            background: smtp.enabled ? "var(--neon)" : "rgba(255,255,255,0.08)",
            position: "relative", transition: "all .2s",
            boxShadow: smtp.enabled ? "0 0 12px rgba(61,169,252,0.5)" : "none",
          }}>
            <div style={{
              position: "absolute", top: 2, left: smtp.enabled ? 18 : 2,
              width: 16, height: 16, borderRadius: "50%",
              background: smtp.enabled ? "#061122" : "var(--text-dim)",
              transition: "left .2s",
            }}></div>
          </div>
        </label>
      </div>
      <div className="card-body" style={{ display: "grid", gap: 14 }}>
        <div style={{ fontSize: 10.5, color: "var(--text-mute)", textTransform: "uppercase", letterSpacing: "0.12em", fontWeight: 600 }}>
          Servidor SMTP
        </div>
        <div className="grid-2">
          <Field label="Host"><input className="input" value={smtp.host} onChange={(e) => set("host", e.target.value)}/></Field>
          <Field label="Porta"><input className="input" type="number" value={smtp.port} onChange={(e) => set("port", +e.target.value)}/></Field>
        </div>
        <div className="grid-2">
          <Field label="Usuário"><input className="input" value={smtp.user} onChange={(e) => set("user", e.target.value)}/></Field>
          <Field label="Senha / API Key"><input className="input" type="password" value={smtp.password} onChange={(e) => set("password", e.target.value)}/></Field>
        </div>
        <div className="grid-2">
          <Field label="De (email)"><input className="input" value={smtp.from} onChange={(e) => set("from", e.target.value)}/></Field>
          <Field label="De (nome)"><input className="input" value={smtp.fromName} onChange={(e) => set("fromName", e.target.value)}/></Field>
        </div>
        <Field label="Criptografia">
          <select className="select" value={smtp.tls} onChange={(e) => set("tls", e.target.value)}>
            <option>STARTTLS</option><option>SSL/TLS</option><option>Nenhuma</option>
          </select>
        </Field>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <button className="btn btn-primary" onClick={sendTest}>
            <Icon name="mail" size={13}/>{testStatus === "sending" ? "Enviando..." : "Enviar teste"}
          </button>
          <button className="btn">Salvar SMTP</button>
          {testStatus === "ok" && <span className="badge badge-green"><span className="ix-dot"></span>Teste entregue</span>}
        </div>

        <div style={{ height: 1, background: "var(--border)", margin: "6px 0" }}></div>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ fontSize: 10.5, color: "var(--text-mute)", textTransform: "uppercase", letterSpacing: "0.12em", fontWeight: 600 }}>
            Destinatários
          </div>
          <div style={{ flex: 1 }}></div>
          <button className="btn btn-sm" onClick={() => setAdding(true)}><Icon name="plus" size={12}/>Adicionar</button>
        </div>

        <div style={{ display: "grid", gap: 6 }}>
          {recipients.map((r, i) => (
            <div key={i} style={{
              display: "grid", gridTemplateColumns: "1fr auto auto", gap: 10, alignItems: "center",
              padding: "10px 12px", borderRadius: 10, border: "1px solid var(--border)", background: "rgba(255,255,255,0.015)"
            }}>
              <div>
                <div style={{ fontWeight: 600, fontSize: 13 }}>{r.email}</div>
                <div style={{ fontSize: 11, color: "var(--text-mute)", marginTop: 2 }}>{r.desc}</div>
              </div>
              <div style={{ display: "flex", gap: 4 }}>
                {["CRITICAL","ERROR","WARN","INFO"].map(s => (
                  <span key={s}
                        onClick={() => toggleSev(i, s)}
                        className={"sev sev-" + s}
                        style={{
                          cursor: "pointer",
                          opacity: r.sev.includes(s) ? 1 : 0.25,
                          fontSize: 10, padding: "3px 7px",
                        }}>
                    {s}
                  </span>
                ))}
              </div>
              <button className="btn btn-sm btn-icon btn-danger"
                      onClick={() => setRecipients(prev => prev.filter((_, j) => j !== i))}>
                <Icon name="trash" size={12}/>
              </button>
            </div>
          ))}
        </div>

        <div style={{
          padding: "10px 12px",
          background: "rgba(33,212,253,0.05)",
          border: "1px solid rgba(33,212,253,0.18)",
          borderRadius: 10, display: "flex", gap: 10, alignItems: "flex-start",
        }}>
          <Icon name="shield" size={14}/>
          <div style={{ fontSize: 11.5, color: "var(--text-dim)", lineHeight: 1.5 }}>
            Alertas seguem rate-limit de 1 email/min por destinatário e agrupam eventos da mesma severidade dentro de uma janela de 60s.
          </div>
        </div>
      </div>

      {adding && (
        <Modal
          title="Novo destinatário"
          onClose={() => setAdding(false)}
          footer={<>
            <button className="btn" onClick={() => setAdding(false)}>Cancelar</button>
            <button className="btn btn-primary" onClick={() => {
              if (newEmail.email) {
                setRecipients([...recipients, newEmail]);
                setNewEmail({ email: "", sev: ["CRITICAL"], desc: "" });
                setAdding(false);
              }
            }}>Adicionar</button>
          </>}
        >
          <Field label="Email"><input className="input" placeholder="usuario@empresa.com" value={newEmail.email} onChange={(e) => setNewEmail({ ...newEmail, email: e.target.value })}/></Field>
          <Field label="Descrição / Equipe"><input className="input" placeholder="ex: Plantão NOC" value={newEmail.desc} onChange={(e) => setNewEmail({ ...newEmail, desc: e.target.value })}/></Field>
          <Field label="Severidades">
            <div style={{ display: "flex", gap: 6 }}>
              {["CRITICAL","ERROR","WARN","INFO"].map(s => (
                <span key={s}
                      className={"sev sev-" + s}
                      style={{ cursor: "pointer", opacity: newEmail.sev.includes(s) ? 1 : 0.3, fontSize: 11, padding: "5px 10px" }}
                      onClick={() => setNewEmail({ ...newEmail, sev: newEmail.sev.includes(s) ? newEmail.sev.filter(x => x !== s) : [...newEmail.sev, s] })}>
                  {s}
                </span>
              ))}
            </div>
          </Field>
        </Modal>
      )}
    </div>
  );
}

window.Settings = Settings;
window.SmtpAlertsCard = SmtpAlertsCard;

// ─── Installer Card ──────────────────────────────────────────────────────
function InstallerCard() {
  const [os, setOs] = useState("windows");
  const [copied, setCopied] = useState(false);

  const builds = {
    windows: [
      { name: "fzBGPTools-Setup-3.4.2.exe",      size: "84.2 MB",  arch: "x64",   note: "Instalador NSIS · auto-update · cria atalho no menu Iniciar" },
      { name: "fzBGPTools-3.4.2-portable.zip",   size: "78.6 MB",  arch: "x64",   note: "Portátil · não requer instalação · roda do pendrive" },
      { name: "fzBGPTools-3.4.2-win-arm64.exe",  size: "82.1 MB",  arch: "ARM64", note: "Windows on ARM (Surface Pro X, etc.)" },
    ],
    linux: [
      { name: "fzbgptools_3.4.2_amd64.deb",      size: "71.4 MB", arch: "x86_64", note: "Debian / Ubuntu · instala systemd unit fzbgptoolsd.service" },
      { name: "fzbgptools-3.4.2-1.x86_64.rpm",   size: "71.8 MB", arch: "x86_64", note: "RHEL / Fedora / Rocky / AlmaLinux" },
      { name: "fzBGPTools-3.4.2.AppImage",       size: "82.0 MB", arch: "x86_64", note: "Portátil · qualquer distro · chmod +x e executar" },
      { name: "fzbgptools-3.4.2-linux-arm64.tar.gz", size: "70.2 MB", arch: "ARM64", note: "Raspberry Pi 4/5 · servidores ARM" },
    ],
  };

  const scripts = {
    windows: `# PowerShell — instalador silencioso (admin)
iwr https://dl.fzbgptools.dev/win/fzBGPTools-Setup-3.4.2.exe -OutFile setup.exe
.\\setup.exe /S /D=C:\\Program Files\\fzBGPTools

# Iniciar serviço
sc.exe create fzbgptoolsd binPath= "C:\\Program Files\\fzBGPTools\\fzbgptoolsd.exe" start= auto
sc.exe start fzbgptoolsd

# Abrir UI em http://localhost:8443`,
    linux: `# Linux — Debian/Ubuntu (one-liner)
curl -fsSL https://dl.fzbgptools.dev/install.sh | sudo bash

# ou manualmente
wget https://dl.fzbgptools.dev/linux/fzbgptools_3.4.2_amd64.deb
sudo apt install ./fzbgptools_3.4.2_amd64.deb

sudo systemctl enable --now fzbgptoolsd
sudo systemctl status fzbgptoolsd

# UI: https://<host>:8443  · CLI: fzbgptools --help`,
  };

  const copy = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(scripts[os]);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    }
  };

  return (
    <div className="card" style={{ marginBottom: 18, overflow: "hidden" }}>
      <div className="card-header">
        <Icon name="download" size={16}/>
        <h3>Instalação <span className="accent">Standalone</span></h3>
        <div className="spacer"></div>
        <span className="badge badge-green">v3.4.2 · estável</span>
        <span className="badge badge-gray" style={{ marginLeft: 6 }}>SHA256 verificado</span>
      </div>
      <div className="card-body">
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 18 }}>
          <OsCard
            active={os === "windows"}
            onClick={() => setOs("windows")}
            os="windows"
            title="Windows"
            sub="10 / 11 · Server 2019/2022"
          />
          <OsCard
            active={os === "linux"}
            onClick={() => setOs("linux")}
            os="linux"
            title="Linux"
            sub="Debian · Ubuntu · RHEL · Fedora · Arch"
          />
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18, alignItems: "start" }}>
          <div>
            <div style={{ fontSize: 10.5, color: "var(--text-mute)", textTransform: "uppercase", letterSpacing: "0.12em", fontWeight: 600, marginBottom: 10 }}>
              Pacotes disponíveis
            </div>
            <div style={{ display: "grid", gap: 8 }}>
              {builds[os].map(b => (
                <div key={b.name} style={{
                  display: "grid", gridTemplateColumns: "1fr auto", gap: 10, alignItems: "center",
                  padding: "12px 14px", borderRadius: 10,
                  border: "1px solid var(--border)", background: "rgba(255,255,255,0.015)",
                }}>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span className="mono" style={{ fontSize: 12.5, fontWeight: 600 }}>{b.name}</span>
                      <span className="badge badge-blue" style={{ fontSize: 9.5 }}>{b.arch}</span>
                    </div>
                    <div style={{ fontSize: 11, color: "var(--text-mute)", marginTop: 3, lineHeight: 1.4 }}>{b.note}</div>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
                    <span className="mono" style={{ fontSize: 11, color: "var(--text-dim)" }}>{b.size}</span>
                    <button className="btn btn-sm btn-primary"><Icon name="download" size={11}/>Baixar</button>
                  </div>
                </div>
              ))}
            </div>

            <div style={{
              marginTop: 14, padding: "10px 12px",
              background: "rgba(74,222,128,0.05)",
              border: "1px solid rgba(74,222,128,0.18)",
              borderRadius: 10, display: "flex", gap: 10, alignItems: "flex-start",
            }}>
              <Icon name="shield" size={14}/>
              <div style={{ fontSize: 11.5, color: "var(--text-dim)", lineHeight: 1.5 }}>
                Todas as builds incluem <strong style={{ color: "var(--text)" }}>todas as dependências embutidas</strong> (Node 20, Python 3.11, SQLite, drivers SSH/Telnet). Não requer instalação separada de runtime.
              </div>
            </div>
          </div>

          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
              <div style={{ fontSize: 10.5, color: "var(--text-mute)", textTransform: "uppercase", letterSpacing: "0.12em", fontWeight: 600 }}>
                Instalação via script
              </div>
              <div style={{ flex: 1 }}></div>
              <button className="btn btn-sm" onClick={copy}>
                <Icon name="copy" size={12}/>{copied ? "Copiado" : "Copiar"}
              </button>
            </div>

            <div className="card card-tight" style={{ overflow: "hidden" }}>
              <div className="term-bar">
                <div className="dot-r"></div><div className="dot-y"></div><div className="dot-g"></div>
                <div className="term-title">{os === "windows" ? "PowerShell (Admin)" : "bash"}</div>
              </div>
              <pre className="term" style={{
                margin: 0, borderRadius: 0, border: "none",
                fontSize: 11.5, whiteSpace: "pre-wrap", lineHeight: 1.6,
                minHeight: 220, maxHeight: 260, overflow: "auto",
              }}>
{scripts[os]}
              </pre>
            </div>

            <div style={{ marginTop: 14, display: "grid", gap: 6 }}>
              <RequirementRow ok label="CPU" value="x86_64 ou ARM64"/>
              <RequirementRow ok label="RAM" value="2 GB mínimo · 4 GB recomendado"/>
              <RequirementRow ok label="Disco" value="500 MB + crescimento do BD"/>
              <RequirementRow ok label="Portas" value="8443 (UI) · 179 (BGP-listener opcional)"/>
              <RequirementRow ok label="Privilégios" value={os === "windows" ? "Administrator" : "root / sudo"}/>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function OsCard({ active, onClick, os, title, sub }) {
  return (
    <div onClick={onClick} style={{
      padding: "16px 18px",
      borderRadius: 12,
      border: "1px solid " + (active ? "var(--border-strong)" : "var(--border)"),
      background: active
        ? "linear-gradient(135deg, rgba(61,169,252,0.12), rgba(161,140,255,0.08))"
        : "rgba(255,255,255,0.015)",
      cursor: "pointer",
      display: "flex", alignItems: "center", gap: 14,
      position: "relative",
      transition: "all .18s",
      boxShadow: active ? "inset 0 0 0 1px rgba(255,255,255,0.04), 0 12px 36px -16px rgba(61,169,252,0.5)" : "none",
    }}>
      <div style={{
        width: 48, height: 48, borderRadius: 12,
        display: "grid", placeItems: "center",
        background: active ? "var(--neon)" : "rgba(255,255,255,0.04)",
        color: active ? "#061122" : "var(--text-dim)",
      }}>
        {os === "windows" ? (
          <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M3 5.5l8-1.1v8.1H3V5.5zm0 8.5h8v8.1l-8-1.1V14zm9-9.7L22 3v10h-10V4.3zM12 14h10v8.7l-10-1.4V14z"/></svg>
        ) : (
          <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2c-1.7 0-2.5 1.6-2.5 3 0 1.1.4 1.7.4 2.6 0 .7-.3 1.4-.9 2C8 10.5 7 12.2 7 14c0 1.2.4 2 1.2 2.7.1 1-.1 1.7-.7 2.4-.3.3-.4.6-.4 1 0 .9.7 1.5 1.8 1.7 1.4.3 2.5.2 3.4-.2.7-.3 1.4-.4 2-.4.7 0 1.4.1 2.1.4.9.4 2 .5 3.4.2 1.1-.2 1.8-.8 1.8-1.7 0-.4-.1-.7-.4-1-.6-.7-.8-1.4-.7-2.4.8-.7 1.2-1.5 1.2-2.7 0-1.8-1-3.5-2-4.4-.6-.6-.9-1.3-.9-2 0-.9.4-1.5.4-2.6 0-1.4-.8-3-2.5-3-1.4 0-2.5 1.2-2.5 2.5"/></svg>
        )}
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 16, fontWeight: 700 }}>{title}</div>
        <div style={{ fontSize: 11.5, color: "var(--text-mute)", marginTop: 2 }}>{sub}</div>
      </div>
      <div style={{
        width: 20, height: 20, borderRadius: "50%",
        border: "1.5px solid " + (active ? "transparent" : "var(--border-strong)"),
        background: active ? "var(--neon)" : "transparent",
        display: "grid", placeItems: "center",
      }}>
        {active && <svg width="11" height="11" viewBox="0 0 12 12" fill="none" stroke="#061122" strokeWidth="2.5" strokeLinecap="round"><path d="M2 6l3 3 5-6"/></svg>}
      </div>
    </div>
  );
}

function RequirementRow({ ok, label, value }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 12 }}>
      <div style={{
        width: 16, height: 16, borderRadius: "50%",
        background: ok ? "rgba(74,222,128,0.18)" : "rgba(154,166,194,0.12)",
        color: ok ? "var(--green)" : "var(--text-mute)",
        display: "grid", placeItems: "center", flexShrink: 0,
      }}>
        <svg width="9" height="9" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="M2 6l3 3 5-6"/></svg>
      </div>
      <span style={{ color: "var(--text-mute)", width: 90, fontSize: 11, textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 600 }}>{label}</span>
      <span style={{ color: "var(--text-dim)" }}>{value}</span>
    </div>
  );
}

window.InstallerCard = InstallerCard;
