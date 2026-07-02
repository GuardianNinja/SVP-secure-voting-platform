const SESSION_STORAGE_KEY = "svp.sessionToken";
const TOKEN_STORAGE_KEY = "svp.currentElectionToken";

let sessionToken = null;
let currentElectionToken = null;

function show(id) {
  document.getElementById(id).classList.remove("hidden");
}

function hide(id) {
  document.getElementById(id).classList.add("hidden");
}

function setText(id, text) {
  document.getElementById(id).textContent = text;
}

function persistSessionState() {
  if (sessionToken) {
    window.localStorage.setItem(SESSION_STORAGE_KEY, sessionToken);
  } else {
    window.localStorage.removeItem(SESSION_STORAGE_KEY);
  }

  if (currentElectionToken) {
    window.localStorage.setItem(TOKEN_STORAGE_KEY, currentElectionToken);
  } else {
    window.localStorage.removeItem(TOKEN_STORAGE_KEY);
  }
}

function restoreSessionState() {
  sessionToken = window.localStorage.getItem(SESSION_STORAGE_KEY);
  currentElectionToken = window.localStorage.getItem(TOKEN_STORAGE_KEY);

  if (sessionToken) {
    show("tokenCard");
    setText("loginStatus", "Existing session restored.");
  }

  if (currentElectionToken) {
    show("ballotCard");
    setText("tokenStatus", `Existing token restored: ${currentElectionToken}`);
  }
}

async function handleLogin() {
  const username = document.getElementById("loginUser").value.trim();
  const password = document.getElementById("loginPass").value;

  if (!username || !password) {
    setText("loginStatus", "Please enter username and password.");
    return;
  }

  setText("loginStatus", "Logging in...");
  try {
    const res = await apiLogin(username, password);
    if (res.mfaRequired) {
      setText("loginStatus", "Password accepted. Two-factor required.");
      show("mfaCard");
      hide("tokenCard");
      hide("ballotCard");
      return;
    }

    sessionToken = res.sessionToken;
    currentElectionToken = null;
    persistSessionState();
    hide("mfaCard");
    show("tokenCard");
    hide("ballotCard");
    setText("loginStatus", "Logged in.");
    setText("tokenStatus", "");
  } catch (e) {
    setText("loginStatus", "Login failed: " + e.message);
  }
}

async function handleMfaVerify() {
  const code = document.getElementById("mfaCode").value.trim();
  if (!/^\d{6}$/.test(code)) {
    setText("mfaStatus", "Enter a valid 6-digit 2FA code.");
    return;
  }

  setText("mfaStatus", "Verifying...");
  try {
    const res = await apiVerifyMfa(code);
    sessionToken = res.sessionToken;
    currentElectionToken = null;
    persistSessionState();
    hide("mfaCard");
    show("tokenCard");
    hide("ballotCard");
    setText("mfaStatus", "Two-factor verified. Session active.");
    setText("loginStatus", "Logged in.");
  } catch (e) {
    setText("mfaStatus", "MFA failed: " + e.message);
  }
}

async function handleTokenRequest() {
  const electionId = document.getElementById("electionSelect").value;
  if (!sessionToken) {
    setText("tokenStatus", "You must be logged in.");
    return;
  }

  setText("tokenStatus", "Requesting token...");
  try {
    const res = await apiRequestToken(electionId, sessionToken);
    currentElectionToken = res.tokenId;
    persistSessionState();
    setText(
      "tokenStatus",
      `Token issued: ${res.tokenId} (expires at ${new Date(
        res.expiresAt * 1000
      ).toLocaleTimeString()})`
    );
    show("ballotCard");
  } catch (e) {
    setText("tokenStatus", "Token request failed: " + e.message);
  }
}

async function handleBallotSubmit() {
  if (!currentElectionToken) {
    setText("ballotStatus", "No active voting token. Request one first.");
    return;
  }

  const districtId = document.getElementById("districtId").value.trim();
  const choice = document.getElementById("choiceSelect").value;

  if (!districtId || !choice) {
    setText("ballotStatus", "Please fill district and choice.");
    return;
  }

  const ballot = {
    electionId: document.getElementById("electionSelect").value,
    districtId,
    choices: [choice]
  };

  setText("ballotStatus", "Submitting ballot...");
  try {
    const res = await apiSubmitBallot(ballot, currentElectionToken);
    setText(
      "ballotStatus",
      `Ballot submitted. ID: ${res.ballotId}, Hash: ${res.ballotHash}`
    );
  } catch (e) {
    setText("ballotStatus", "Ballot submission failed: " + e.message);
  }
}

async function handleVerify() {
  const id = document.getElementById("verifyId").value.trim();
  const out = document.getElementById("verifyResult");
  if (!id) {
    out.textContent = "Enter a ballot ID.";
    return;
  }

  out.textContent = "Checking...";
  try {
    const data = await apiVerifyBallot(id);
    out.textContent = `Ballot found. Hash: ${data.ballotHash}, District: ${data.districtId}`;
  } catch (_) {
    out.textContent = "Ballot not found or invalid.";
  }
}

window.addEventListener("DOMContentLoaded", () => {
  restoreSessionState();

  const loginBtn = document.getElementById("loginBtn");
  const mfaBtn = document.getElementById("mfaBtn");
  const tokenBtn = document.getElementById("tokenBtn");
  const submitBallotBtn = document.getElementById("submitBallotBtn");
  const verifyBtn = document.getElementById("verifyBtn");

  if (loginBtn) {
    loginBtn.addEventListener("click", handleLogin);
  }
  if (mfaBtn) {
    mfaBtn.addEventListener("click", handleMfaVerify);
  }
  if (tokenBtn) {
    tokenBtn.addEventListener("click", handleTokenRequest);
  }
  if (submitBallotBtn) {
    submitBallotBtn.addEventListener("click", handleBallotSubmit);
  }
  if (verifyBtn) {
    verifyBtn.addEventListener("click", handleVerify);
  }
});
