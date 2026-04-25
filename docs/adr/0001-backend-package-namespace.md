# ADR-0001: Use `litigation_api` as the Canonical Backend Package Namespace

## Status
Accepted

## Context

The backend code was reorganized into a `src` layout under `backend/src/litigation_api`. During the move, some source files and tests continued importing the old `app.*` package path, which broke test collection and created ambiguity about the real import contract.

## Decision

The canonical backend Python package name is `litigation_api`.

All backend source imports should use either:

- absolute imports rooted at `litigation_api`, or
- relative imports within the `litigation_api` package

The old `app.*` import path is obsolete and should not be reintroduced.

## Consequences

- New backend modules should live under `backend/src/litigation_api/`.
- Tests should import from `litigation_api.*`.
- Tooling that runs pytest from the repo root must ensure `backend/src` is importable during collection.

## Guidance for Tools

- Do not generate new files under `backend/app/`.
- Do not suggest `from app...` imports.
- If you need a backend import path, assume `litigation_api`.
