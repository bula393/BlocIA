# Security Review Evidence

Checks performed:

- Searched `front/src/**` for `localStorage` and `sessionStorage`.
- Result: no matches.

Conclusion: JWT/access-token state remains in memory and is not persisted in browser storage.
