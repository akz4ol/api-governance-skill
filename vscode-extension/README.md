# API Governor VS Code Extension

Automated API governance for OpenAPI specifications directly in VS Code.

## Features

- **Real-time Linting**: Automatically lint OpenAPI specs on save
- **Breaking Change Detection**: Compare specs against baseline to detect breaking changes
- **Full Report Generation**: Generate comprehensive governance reports

## Requirements

- Python 3.9+
- `api-governor` package installed (`pip install api-governor`)

## Installation

1. Install from VS Code Marketplace (coming soon)
2. Or install manually:
   ```bash
   cd vscode-extension
   npm install
   npm run compile
   npm run package
   code --install-extension api-governor-1.0.0.vsix
   ```

## Usage

### Automatic Linting

The extension automatically lints OpenAPI files when:
- A file is opened
- A file is saved (configurable)

### Manual Commands

Open Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`) and search for:

- **API Governor: Lint Current File** - Run governance checks on current file
- **API Governor: Compare with Baseline** - Detect breaking changes against baseline spec
- **API Governor: Generate Full Report** - Generate detailed markdown report

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `api-governor.policy` | `standard` | Governance policy (strict, standard, relaxed, custom) |
| `api-governor.customPolicyPath` | `""` | Path to custom policy file |
| `api-governor.baselineSpec` | `""` | Path to baseline spec for diff |
| `api-governor.autoLint` | `true` | Auto-lint on save |
| `api-governor.pythonPath` | `python` | Path to Python interpreter |

## Diagnostics

Issues appear in the Problems panel:

- **Errors** (red): BLOCKER findings - must fix before merge
- **Warnings** (yellow): MAJOR findings - should address
- **Info** (blue): MINOR findings - consider addressing
- **Hints** (gray): INFO findings - informational

## Development

```bash
cd vscode-extension
npm install
npm run watch  # Compile in watch mode
```

Press `F5` in VS Code to launch Extension Development Host.

## License

MIT
