# SVP-secure-voting-platform

A demo secure digital voting concept with static frontend flows for login, 2FA, token issuance, ballot submission, and ballot verification.

## Included pages

- `index.html` — portal landing page
- `vote.html` — voting and ballot verification flow
- `totp.html` — TOTP enrollment flow

## Supporting files

- `auth.js` — login/MFA UI state handling with session persistence
- `api.js` — fetch wrappers for the expected backend API
- `clear.css` — shared Clear Voting Seal styling
- `schema.sql` — example SQL schema for voters, tokens, ballots, and audit events
