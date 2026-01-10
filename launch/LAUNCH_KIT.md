# Launch Kit: api-governance-skill

Launch assets for distributing api-governance-skill to developer communities.

---

## Twitter/X Threads

### Thread 1: Problem-First

```
1/ API reviews are broken.

Different reviewers catch different issues.
Breaking changes slip through.
Security gaps go unnoticed until production.

We built something to fix this. Thread 👇

2/ The pain points we kept hitting:

- "Which naming convention are we using again?"
- "Did anyone check if this breaks the mobile app?"
- "Why does every service have different error formats?"

3/ Existing tools are either:

- Too basic (just linting)
- Too complex (enterprise governance platforms)
- Missing artifacts (no changelogs, no deprecation plans)

4/ So we built api-governance-skill:

✓ Policy-driven linting
✓ Breaking change detection
✓ Auto-generates: API_REVIEW.md, CHANGELOG.md, DEPRECATION_PLAN.md

5/ Example:

$ api-governor v2.yaml --baseline v1.yaml

BLOCKER: Breaking change - DELETE /users/{id} removed
MAJOR: Missing auth on POST /orders
MINOR: Path '/getUsers' should use kebab-case

6/ The key insight: reviewers need *artifacts*, not just warnings.

We generate merge-ready docs that go into the PR.
No more "I'll write the changelog later."

7/ Try it:

pip install api-governor
api-governor your-spec.yaml

GitHub: github.com/akz4ol/api-governance-skill

MIT licensed. PRs welcome.
```

### Thread 2: Breaking Changes Focus

```
1/ "We shipped a breaking API change and didn't know until customers complained."

Sound familiar? Here's how we automated breaking change detection. 🧵

2/ Breaking changes we detect:

- Removed endpoints
- New required parameters
- Removed response fields
- Narrowed enums
- Changed auth requirements

3/ But detection isn't enough.

When we find breaking changes, we generate a DEPRECATION_PLAN.md with:
- What changed
- Migration steps for consumers
- Suggested deprecation timeline

4/ The workflow:

$ api-governor new-spec.yaml --baseline old-spec.yaml

If breaking changes exist without a deprecation plan → BLOCKER
PR cannot merge until addressed.

5/ This catches breaking changes in CI before they hit production.

No more "we'll deal with it when someone complains."

github.com/akz4ol/api-governance-skill
```

### Thread 3: Security Focus

```
1/ API security issues we catch automatically:

- Endpoints without authentication
- Missing OAuth scopes
- Weak auth schemes
- Sensitive fields without redaction markers

A thread on API security linting 👇

2/ The default is "require auth on everything."

If you genuinely want a public endpoint, mark it explicitly:
x-public: true

This forces intentional decisions about auth.

3/ We also check for OAuth scope hygiene.

If your spec declares OAuth, we verify each endpoint specifies required scopes.
No more "forgot to add scopes" slip-ups.

4/ Findings integrate into your existing review flow.

API_REVIEW.md lists security issues by severity.
BLOCKER issues fail the build.

github.com/akz4ol/api-governance-skill
```

---

## Hacker News Post

### Ask HN: How do you handle API governance at scale?

```
We've been struggling with API consistency across 50+ microservices. Different teams use different error formats, naming conventions, and security patterns.

We built an open-source tool to address this:

- Policy-driven linting for OpenAPI specs
- Breaking change detection (compares spec versions)
- Auto-generates API_REVIEW.md, CHANGELOG.md, DEPRECATION_PLAN.md

It runs in CI and blocks PRs with critical issues.

Example output:

  BLOCKER: Breaking change - removed endpoint without deprecation plan
  MAJOR: POST /orders missing security requirement
  MINOR: Path segment 'getUserById' should be kebab-case

GitHub: https://github.com/akz4ol/api-governance-skill

Curious how others handle this. Do you use Spectral? Custom scripts? Manual review only?
```

---

## Reddit Posts

### r/programming

**Title:** We open-sourced our API governance tool after hitting the "every service has different error formats" wall

```
After the third time debugging a mobile app failure because the backend changed an API without telling anyone, we built a tool to catch this automatically.

api-governance-skill:
- Lints OpenAPI specs against configurable policies
- Detects breaking changes between spec versions
- Generates review reports and deprecation plans

It's like ESLint for API design, plus breaking change detection.

The key insight was that engineers don't just need warnings—they need artifacts. So we generate API_REVIEW.md that goes directly into the PR.

GitHub: https://github.com/akz4ol/api-governance-skill

MIT licensed. Built with Python, no heavy dependencies.
```

### r/devops

**Title:** Automated API governance in CI/CD - catching breaking changes before production

```
We added a CI step that catches API breaking changes before they merge:

$ api-governor v2.yaml --baseline v1.yaml

Output:
- BLOCKER: Removed DELETE /users/{id}
- BLOCKER: Made optional param 'tenant_id' required
- MAJOR: Missing auth on new endpoint

If any BLOCKER exists, PR fails.

More importantly, it generates a DEPRECATION_PLAN.md with migration guidance for consumers.

Been using this for 6 months across 30+ services. Caught 40+ breaking changes that would've hit production.

Open source: https://github.com/akz4ol/api-governance-skill
```

---

## GitHub Discussions Seeds

### Discussion 1: Feature Request Thread

**Title:** What rules would you add?

```
We have rules for security, pagination, error formats, naming, and breaking changes.

What other API design rules would be useful for your team?

Some we're considering:
- Rate limiting headers
- HATEOAS link validation
- Deprecation sunset header requirements
- Request ID propagation

What would you prioritize?
```

### Discussion 2: Integration Stories

**Title:** Share your CI/CD integration setup

```
We'd love to hear how you're integrating api-governance-skill into your workflow.

Questions:
- Which CI platform? (GitHub Actions, GitLab CI, Jenkins, etc.)
- What policy preset do you use? (internal, strict, custom)
- Any interesting customizations?

Share your config snippets!
```

### Discussion 3: Policy Examples

**Title:** Share your custom policies

```
If you've created custom policies for your organization, share them here!

We'll collect interesting patterns and potentially add them as presets.

Especially interested in:
- Industry-specific policies (fintech, healthcare, etc.)
- Multi-team governance setups
- Gradual adoption strategies
```

---

## Adjacent Repo Outreach

See [OUTREACH.md](OUTREACH.md) for the cross-repo integration strategy.
