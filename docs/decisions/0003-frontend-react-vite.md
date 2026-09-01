# ADR 0003: Frontend — React + Vite (TypeScript)

## Status
Accepted

## Context
The platform needs ~20 distinct application areas (dashboard, inventory,
risk register, controls, AI security, etc.) with drill-down navigation
from executive summaries to technical detail, per the "Final Portfolio
Standard" in the README.

## Decision
Use React with Vite and TypeScript, calling the FastAPI backend over REST
with a JWT bearer token.

## Why
- Vite gives a fast, simple dev server and build with minimal
  configuration — no need for a heavier meta-framework (e.g. Next.js)
  since this is a client-rendered internal tool, not a public marketing
  site needing SSR/SEO.
- TypeScript catches a meaningful class of bugs at the API-contract
  boundary (matching backend Pydantic schemas to frontend types) which
  matters more here than in a throwaway script, given the number of
  distinct data shapes across ~20 modules.
- React's component model maps cleanly onto the module list (one route +
  a small set of components per domain), keeping the frontend
  understandable module-by-module rather than as one large app.

## Consequences
- A component library (kept intentionally small and consistent, see
  `frontend/src/components/`) is used for tables, badges (risk rating
  colors), and cards, rather than hand-rolling ad hoc styling per page —
  this keeps ~20 pages visually consistent without a heavy design system.
- No server-side rendering; the SPA assumes it's used by authenticated
  internal staff, not indexed by search engines.
