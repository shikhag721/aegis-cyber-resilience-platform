# Development-mode image: runs the Vite dev server directly. This project
# is a local/demo platform (see docs/decisions/0005-synthetic-environment.md),
# so a production Nginx multi-stage build is documented as a future step
# (docs/architecture/limitations.md) rather than built now.
FROM node:20-slim

# Patch OS packages and the npm CLI's own bundled dependencies (both drift
# out of date between node:20-slim publishes) - found via a Phase 12 Trivy
# image scan flagging debian libcap2/libgnutls30 and several CVEs in npm's
# internal deps (tar, glob, minimatch, etc. - not this project's own
# dependencies, which `npm audit` already reports clean).
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*
RUN npm install -g npm@11

WORKDIR /app

COPY frontend/package.json ./
RUN npm install

COPY frontend/ .

EXPOSE 5173

CMD ["npm", "run", "dev"]
