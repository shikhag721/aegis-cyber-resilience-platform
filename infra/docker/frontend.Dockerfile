# Development-mode image: runs the Vite dev server directly. This project
# is a local/demo platform (see docs/decisions/0005-synthetic-environment.md),
# so a production Nginx multi-stage build is documented as a future step
# (docs/architecture/limitations.md) rather than built now.
FROM node:20-slim

WORKDIR /app

COPY frontend/package.json ./
RUN npm install

COPY frontend/ .

EXPOSE 5173

CMD ["npm", "run", "dev"]
