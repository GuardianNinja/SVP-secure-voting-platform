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
- `main.py` — FastAPI backend with matching `/api` handlers used by the frontend

## Backend quick start

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Run the app:
   - `uvicorn main:app --reload`
3. Open:
   - `http://127.0.0.1:8000/index.html`

## Demo account

- Username: `demo`
- Password: `demo123`

If TOTP is enabled, login requires MFA verification using the code from `/api/auth/totp/setup`.
