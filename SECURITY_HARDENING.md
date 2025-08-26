# Fuel Tracker — Security Hardening Path (Phase 2+)

**Current (Phase 1):**
- Repo-level secret `EIA_API_KEY`
- `.env` for local dev (gitignored)
- Step-scoped secret usage in CI
- Pre-commit: detect-secrets + ruff

**Upgrade Path (later):**
1) Secrets via OIDC + Cloud Secret Manager (AWS/GCP/Azure)
   - Minimal role: read-only access to one secret
   - CI permissions: `contents:read`, `id-token:write`
   - Fetch at runtime; no GitHub-stored secret

2) GitHub Environments (e.g., `prod`)
   - Required reviewers / approvals
   - Branch restrictions and protected deployments

3) Action hardening
   - Pin critical actions to commit SHAs
   - CODEOWNERS on `.github/workflows/**`
   - Secret scanning + push protection enforced

4) Operational hygiene
   - Rotate EIA key on schedule
   - Cloud audit logs for secret access
   - Short-lived artifact retention; no sensitive data
