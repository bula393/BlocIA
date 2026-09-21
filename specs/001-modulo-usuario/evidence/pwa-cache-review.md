# PWA Cache Review Evidence

Checked `front/public/service-worker.js`.

Findings:

- Requests whose path starts with `/auth`, `/profile`, or `/technical-profile` are treated as private and sent to network.
- Non-GET requests are sent to network.
- Cache lookup is used only after private paths and non-GET requests are excluded.

Conclusion: private user responses are not cached by the service worker.
