-- voters: identity layer
CREATE TABLE voters (
  voter_id UUID PRIMARY KEY,
  username VARCHAR(64) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  mfa_secret TEXT,
  status VARCHAR(16) DEFAULT 'active',
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- tokens: bridge between identity and ballots
CREATE TABLE tokens (
  token_id UUID PRIMARY KEY,
  voter_id UUID NOT NULL REFERENCES voters(voter_id),
  election_id VARCHAR(64) NOT NULL,
  issued_at TIMESTAMP NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  used BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_tokens_voter ON tokens(voter_id);
CREATE INDEX idx_tokens_election ON tokens(election_id);

-- ballots: content layer (no PII)
CREATE TABLE ballots (
  ballot_id UUID PRIMARY KEY,
  election_id VARCHAR(64) NOT NULL,
  district_id VARCHAR(64) NOT NULL,
  choices_json JSONB NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  previous_hash TEXT,
  ballot_hash TEXT NOT NULL
);

CREATE INDEX idx_ballots_election ON ballots(election_id);
CREATE INDEX idx_ballots_hash ON ballots(ballot_hash);

-- audit_log: events
CREATE TABLE audit_log (
  id BIGSERIAL PRIMARY KEY,
  event_type VARCHAR(64) NOT NULL,
  voter_id UUID,
  election_id VARCHAR(64),
  payload_json JSONB,
  ts TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_event ON audit_log(event_type);
CREATE INDEX idx_audit_election ON audit_log(election_id);
