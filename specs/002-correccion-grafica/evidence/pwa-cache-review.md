# PWA Cache Review Evidence

Checked `front/public/service-worker.js`.

Findings:

- Requests beginning with `/auth`, `/profile`, and `/technical-profile` are sent to network.
- Non-GET requests are sent to network.
- Cache lookup occurs only after private paths and non-GET requests are excluded.

Conclusion: protected/private route responses are not cached by the service worker.
