async function apiRequest(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  if (!res.ok) {
    let msg = "Request failed";
    try {
      const errText = await res.text();
      if (errText) {
        const err = JSON.parse(errText);
        msg = err.detail || JSON.stringify(err);
      }
    } catch (_) {
      // Ignore non-JSON error bodies and use the default message.
    }
    throw new Error(msg);
  }

  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

async function apiLogin(username, password) {
  return apiRequest("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password })
  });
}

async function apiVerifyMfa(code) {
  return apiRequest("/auth/mfa", {
    method: "POST",
    body: JSON.stringify({ code })
  });
}

async function apiRequestToken(electionId, sessionToken) {
  return apiRequest("/auth/token", {
    method: "POST",
    headers: { Authorization: "Bearer " + sessionToken },
    body: JSON.stringify({ electionId })
  });
}

async function apiSubmitBallot(ballot, tokenId) {
  const payload = { ...ballot, tokenId };
  return apiRequest("/ballot/submit", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

async function apiVerifyBallot(ballotId) {
  return apiRequest(`/verify/${encodeURIComponent(ballotId)}`, {
    method: "GET"
  });
}
