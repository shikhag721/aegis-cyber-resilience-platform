# ADR 0006: Password hashing — Argon2id, not bcrypt/passlib

## Status
Accepted

## Context
While building authentication (Phase 0), `passlib[bcrypt]` — a common
choice in tutorials — failed its own internal self-test against the
currently-installed `bcrypt` package:

```
ValueError: password cannot be longer than 72 bytes, truncate manually if necessary
```

This is a known, unresolved incompatibility: `passlib` has been
unmaintained since 2020, and modern `bcrypt` releases (4.1+) tightened
their 72-byte input validation in a way `passlib`'s own internal
backend-detection self-test does not handle. This is not a problem with
this project's passwords — it happens during passlib's own startup
self-check, before any real password is hashed.

## Decision
Use **Argon2id** directly via `argon2-cffi` (actively maintained, no
`passlib` dependency) instead of bcrypt/passlib.

## Why this is also the better security choice, not just a workaround
- OWASP's Password Storage Cheat Sheet lists **Argon2id as the first
  recommended choice** for new applications, ahead of bcrypt, specifically
  because it is memory-hard (configurable memory cost), which makes
  large-scale GPU/ASIC cracking of a stolen password database
  significantly more expensive than bcrypt's CPU-only cost function.
- `argon2-cffi` is maintained and has no equivalent version-compatibility
  trap at the time of writing.

## Consequences
- `backend/app/core/security.py` calls `argon2.PasswordHasher` directly —
  no abstraction layer (like passlib's `CryptContext`) is needed for a
  single supported algorithm, keeping the module simpler.
- If a future migration to a different algorithm is ever needed, existing
  Argon2 hashes are self-describing (the hash string encodes its own
  parameters), so a gradual re-hash-on-login migration remains possible
  without a big-bang cutover.
