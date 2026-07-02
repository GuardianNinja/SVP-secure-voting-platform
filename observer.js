const observerElectionSelect = document.getElementById("observerElectionSelect");
const observerRefreshBtn = document.getElementById("observerRefreshBtn");
const observerStatus = document.getElementById("observerStatus");
const observerLookupBtn = document.getElementById("observerLookupBtn");
const observerBallotId = document.getElementById("observerBallotId");
const observerLookupResult = document.getElementById("observerLookupResult");
const observerChainHead = document.getElementById("observerChainHead");
const observerEntries = document.getElementById("observerEntries");

function setObserverStatus(message, isError = false) {
  observerStatus.textContent = message;
  observerStatus.style.color = isError ? "#b60205" : "#111827";
}

function renderJson(el, data) {
  el.textContent = JSON.stringify(data, null, 2);
}

async function refreshObserverData() {
  const electionId = observerElectionSelect.value;
  setObserverStatus("Loading observer data...");
  try {
    const [head, entries] = await Promise.all([
      apiGetObserverChainHead(electionId),
      apiGetObserverEntries(electionId, 10)
    ]);
    renderJson(observerChainHead, head);
    renderJson(observerEntries, entries);
    setObserverStatus("Observer data updated.");
  } catch (err) {
    setObserverStatus(err.message, true);
  }
}

async function lookupBallot() {
  const ballotId = observerBallotId.value.trim();
  if (!ballotId) {
    setObserverStatus("Enter a ballot ID to lookup.", true);
    return;
  }
  setObserverStatus("Looking up ballot...");
  try {
    const ballot = await apiVerifyBallot(ballotId);
    renderJson(observerLookupResult, ballot);
    setObserverStatus("Ballot lookup complete.");
  } catch (err) {
    observerLookupResult.textContent = "";
    setObserverStatus(err.message, true);
  }
}

observerRefreshBtn?.addEventListener("click", refreshObserverData);
observerLookupBtn?.addEventListener("click", lookupBallot);
refreshObserverData();

