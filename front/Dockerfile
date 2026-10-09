# syntax=docker/dockerfile:1
ARG NODE_IMAGE=node:22-alpine@sha256:0a7108bf6c7bf5de370ffb1a3ed6be93d405b43ff159f681a8d18c0e2bc2e402
ARG NGINX_IMAGE=nginxinc/nginx-unprivileged:stable-alpine@sha256:15c994d10d6d78658721c3bcafff14cb281fba2a4bdf9d5ba92c416a472516e3
FROM ${NODE_IMAGE} AS build
ARG RELEASE_TAG=development
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build
RUN node -e 'require("node:fs").writeFileSync("dist/version.json", JSON.stringify({ release: process.env.RELEASE_TAG || "development" }) + "\n")'

FROM ${NGINX_IMAGE} AS runtime
ENV PORT=8080 \
    BLOCIA_API_UPSTREAM=api:8000 \
    NGINX_ENVSUBST_FILTER=^(BLOCIA_API_UPSTREAM|PORT)$
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q -O /dev/null "http://127.0.0.1:${PORT}/healthz" || exit 1
STOPSIGNAL SIGQUIT
