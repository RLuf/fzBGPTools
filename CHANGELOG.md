# Changelog — fzBGPTools

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-05-28
### Added
- Integrated PyQt5 desktop interface matching the React app design system.
- Live BGP Topology mapping visualization with dotted routing lines and dynamic animation (`DashboardScreen` and `BGPGraphWidget`).
- Asynchronous non-blocking network tool diagnostics for Ping and Traceroute running in parallel (`PingRunner` and `TracerouteRunner`).
- RDAP WHOIS lookup for ASN and organization name mapping (`asn_resolver.py`) with a local in-memory cache and 2-second fallback timeouts.
- Configurable interactive SSH and Telnet terminal sessions with custom Echo feedback supporting MikroTik, Cisco, and generic nodes.
- Local SQLite database layer (`fzbgptools.db`) storing monitored ASNs, active alerts, host nodes, and console log output.
- Backup, restore, and database reset tools directly within the system settings pane.
- Automated Debian packaging (`.deb`) generator script (`build_deb.sh`).
- Git versioning and `.gitignore` file.
