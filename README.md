# agent-bus

> A real-time message bus for multi-agent AI environments.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-green)](https://modelcontextprotocol.io)

## What is this?

`agent-bus` is a lightweight, SQLite-backed message bus that lets multiple AI agents (Claude, Gemini, Codex, Cursor, etc.) **communicate and coordinate in real time** without a human acting as the middleman.

It also ships with `watcher.py`, an **environment sentinel** that automatically broadcasts alerts whenever critical config files change (MCP configs, agent rules, IDE settings).

## The Problem It Solves

When you run multiple AI agents in the same workspace, they are blind to each other. If Claude disables an MCP server, Gemini will keep trying to call it and freeze for 2+ minutes. There is no shared nervous system.

`agent-bus` is that nervous system.

## Features

- **`bus_send`** Send a structured message to another agent
- **`bus_inbox`** Read pending messages in your inbox
- **`bus_ack`** Confirm message processing
- **`bus_broadcast`** Send global announcement to all agents
- **`bus_status`** Check heartbeat of all agents in the ecosystem
- **`bus_thread`** View full conversation history by thread
- **`bus_lock` / `bus_unlock` / `bus_check_lock`** Distributed file locking
- **`env-watcher`** File sentinel that auto-broadcasts config changes in less than 1 second

## Quick Start

```bash
pip install mcp watchdog
```

Then configure your MCP client to point to `server.py` with `AGENT_NAME` and `AGENT_BUS_DB` env vars.
All agents must share the same `AGENT_BUS_DB` file.

**Windows (auto-start on login):**
```powershell
.\install.ps1
```

**Linux/Mac (systemd):**
```bash
bash install.sh
```

## Real-World Impact

Before: Claude disabled an MCP server. Gemini kept calling it. IDE froze for 2 minutes.

After: Claude disables MCP -> env-watcher detects config change -> alert arrives in Gemini inbox in less than 1 second -> no frozen IDE.

## Built With

- [MCP (Model Context Protocol)](https://modelcontextprotocol.io)
- SQLite with WAL mode
- [watchdog](https://github.com/gorakhargosh/watchdog)

## License

MIT - built by [@Gabrielrtads](https://github.com/Gabrielrtads) with Gemini (Antigravity) + Claude Code.
