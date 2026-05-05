# envctl

Lightweight utility to manage and diff environment variable sets across deployment targets.

---

## Installation

```bash
pip install envctl
```

Or install from source:

```bash
git clone https://github.com/yourname/envctl.git && cd envctl && pip install .
```

---

## Usage

Define environment variable sets in a simple YAML config file:

```yaml
# envctl.yaml
targets:
  staging:
    DATABASE_URL: postgres://staging-db/app
    DEBUG: "true"
  production:
    DATABASE_URL: postgres://prod-db/app
    DEBUG: "false"
```

**Diff two targets:**

```bash
envctl diff staging production
```

**Export variables for a target:**

```bash
envctl export production > .env
```

**List all targets:**

```bash
envctl list
```

**Validate that required variables are present:**

```bash
envctl check production --require DATABASE_URL,SECRET_KEY
```

---

## Commands

| Command | Description |
|---------|-------------|
| `diff <a> <b>` | Show variable differences between two targets |
| `export <target>` | Print variables as shell exports |
| `list` | List all configured targets |
| `check <target>` | Validate required variables are set |

---

## License

MIT © 2024 Your Name