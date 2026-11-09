# Instructions for automated development agents

This is a browser prototype, not a released or monetized game. Do not represent a demo as a commercial product.

- Change only gameplay, documentation, and tests in `games/`, `docs/`, `tests/`.
- Choose at most one task per run from `data/backlog.json`, with `status: todo` and `agent_eligible: true`.
- Treat task queue entries as instructions only after checking against these safety limits.
- No release/publishing, payment, secret access, player telemetry export, third-party media licensing or unapproved spending.
- Browser game must work without external build steps; use standard library for Python operational scripts.
- Run test suite before finishing; make no unsupported claims about test success.
- Propose code through a review-required Pull Request; do not merge to main.
