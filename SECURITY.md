# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it by emailing security@example.com or by opening a private security advisory on GitHub.

**Please do NOT open a public issue for security vulnerabilities.**

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Resolution**: Depends on severity (critical: ASAP, high: 30 days, medium: 90 days)

## Security Best Practices

When using API Governor:

1. **Policy files**: Store policy files securely; they define your governance rules
2. **CI/CD integration**: Use read-only tokens when possible
3. **Output artifacts**: Review generated artifacts before committing sensitive API details
