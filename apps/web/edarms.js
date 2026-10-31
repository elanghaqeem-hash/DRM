/* EDARMS WP1: in-memory OIDC PKCE PoC. No customer/Bank data. */
const el = (id) => document.getElementById(id);
let accessToken = null;
let idToken = null;
let tenantId = null;
let identity = null;
let oidcConfig = null;
let pendingDecision = null;

function feedback(message, isError = false) {
  const node = el("feedback");
  node.textContent = message;
  node.classList.toggle("error", isError);
}
function busy(button, flag) {
  button.disabled = flag;
  button.setAttribute("aria-busy", String(flag));
}
function toggleView(authenticated) {
  el("login-panel").hidden = authenticated;
  el("tenant-panel").hidden = !authenticated;
  el("logout").hidden = !authenticated;
  if (!authenticated) {
    el("work-panels").hidden = true;
    identity = null;
    tenantId = null;
    el("identity").textContent = "Sesi belum aktif";
  }
}
function base64url(bytes) {
  return btoa(String.fromCharCode(...bytes)).replaceAll("+", "-").replaceAll("/", "_").replace(/=+$/, "");
}
async function pkceChallenge(verifier) {
  const hash = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(verifier));
  return base64url(new Uint8Array(hash));
}
async function config() {
  if (!oidcConfig) {
    const response = await fetch("/v1/public/oidc-config", { cache: "no-store" });
    if (!response.ok) throw new Error("Konfigurasi IdP tidak tersedia");
    oidcConfig = await response.json();
  }
  return oidcConfig;
}
function redirectUri() { return new URL("/app", location.origin).toString(); }
async function startLogin() {
  const conf = await config();
  const verifier = base64url(crypto.getRandomValues(new Uint8Array(32)));
  const state = base64url(crypto.getRandomValues(new Uint8Array(24)));
  sessionStorage.setItem("edarms_pkce_v1", verifier);
  sessionStorage.setItem("edarms_state_v1", state);
  const query = new URLSearchParams({
    response_type: "code",
    client_id: conf.client_id,
    scope: "openid profile",
    redirect_uri: redirectUri(),
    code_challenge_method: "S256",
    code_challenge: await pkceChallenge(verifier),
    state,
  });
  location.assign(conf.issuer + "/protocol/openid-connect/auth?" + query.toString());
}
async function handleCallback() {
  const params = new URLSearchParams(location.search);
  if (params.has("error")) throw new Error("IdP menolak otentikasi");
  if (!params.has("code")) return false;
  const state = sessionStorage.getItem("edarms_state_v1");
  const verifier = sessionStorage.getItem("edarms_pkce_v1");
  if (!state || !verifier || params.get("state") !== state) {
    throw new Error("State otentikasi tidak cocok; ulangi login");
  }
  sessionStorage.removeItem("edarms_state_v1");
  sessionStorage.removeItem("edarms_pkce_v1");
  history.replaceState({}, document.title, redirectUri());
  const conf = await config();
  const response = await fetch(conf.issuer + "/protocol/openid-connect/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      client_id: conf.client_id,
      code: params.get("code"),
      redirect_uri: redirectUri(),
      code_verifier: verifier,
    }),
  });
  if (!response.ok) throw new Error("Pertukaran token PKCE ditolak oleh IdP");
  const data = await response.json();
  if (!data.access_token) throw new Error("IdP tidak mengembalikan access token");
  accessToken = data.access_token;
  idToken = data.id_token || null;
  toggleView(true);
  feedback("Login berhasil. Masukkan ID tenant uji yang telah diprovisioning oleh administrator.");
  return true;
}
async function api(path, options = {}) {
  if (!accessToken) throw new Error("Sesi OIDC belum aktif");
  const response = await fetch(path, {
    ...options,
    headers: {
      Authorization: "Bearer " + accessToken,
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(options.headers || {}),
    },
    cache: "no-store",
  });
  if (response.status === 401) {
    accessToken = null;
    idToken = null;
    toggleView(false);
    throw new Error("Sesi telah berakhir, silakan login kembali");
  }
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = payload.detail;
    throw new Error(typeof detail === "string" ? detail : "Request gagal (HTTP " + response.status + ")");
  }
  return payload;
}
async function openWorkspace() {
  const raw = el("tenant-id").value.trim();
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(raw)) {
    throw new Error("Tenant ID harus berformat UUID yang valid");
  }
  const data = await api("/v1/workspace/me?tenant_id=" + encodeURIComponent(raw));
  tenantId = raw;
  identity = data;
  el("identity").textContent = data.subject + " · " + data.roles.join(", ");
  el("create-panel").hidden = !data.abilities.task_create;
  el("work-panels").hidden = false;
  await loadTasks();
  feedback("Akses organisasi terverifikasi. Fitur yang tersedia hanya workflow tugas PoC.");
}
function tag(name, className, value) {
  const n = document.createElement(name);
  if (className) n.className = className;
  if (value !== undefined) n.textContent = value;
  return n;
}
function addDecisionButton(container, task, decision, label) {
  const button = tag("button", "ghost", label);
  button.type = "button";
  button.addEventListener("click", async () => {
    if (!confirm("Konfirmasi keputusan " + label.toLowerCase() + " untuk tugas ini?")) return;
    let reason = null;
    if (decision === "REJECTED") {
      reason = prompt("Alasan penolakan wajib diisi");
      if (!reason || !reason.trim()) { feedback("Alasan penolakan wajib diisi.", true); return; }
    }
    busy(button, true);
    try {
      await api("/v1/workspace/tasks/" + encodeURIComponent(task.id) + "/decision", {
        method: "POST",
        body: JSON.stringify({ tenant_id: tenantId, decision, expected_version: task.version, reason }),
      });
      feedback("Keputusan tersimpan dan dicatat dalam riwayat tugas.");
      await loadTasks();
    } catch (err) { feedback(err.message, true); }
    finally { busy(button, false); }
  });
  container.appendChild(button);
}
function renderTasks(tasks) {
  const container = el("tasks");
  container.replaceChildren();
  if (!tasks.length) {
    container.appendChild(tag("p", "", "Belum ada tugas untuk status dan hak akses Anda."));
    return;
  }
  for (const task of tasks) {
    const item = tag("article", "task");
    const header = tag("div", "task-top");
    header.appendChild(tag("strong", "", task.title));
    const badge = tag("span", "chip " + task.status.toLowerCase(), task.status);
    header.appendChild(badge);
    item.appendChild(header);
    item.appendChild(tag("small", "", "Dibuat oleh: " + task.created_by));
    item.appendChild(tag("small", "", "Ditugaskan kepada: " + task.assigned_to));
    item.appendChild(tag("small", "", "Versi keputusan: " + task.version));
    if (task.decision_reason) item.appendChild(tag("small", "", "Alasan keputusan: " + task.decision_reason));
    if (task.status === "OPEN" && identity?.abilities.task_decide &&
        task.assigned_to === identity.subject && task.created_by !== identity.subject) {
      const actions = tag("div", "task-actions");
      addDecisionButton(actions, task, "APPROVED", "Setujui");
      addDecisionButton(actions, task, "REJECTED", "Tolak");
      item.appendChild(actions);
    }
    container.appendChild(item);
  }
}
async function loadTasks() {
  if (!tenantId) return;
  const status = el("status-filter").value;
  const query = new URLSearchParams({tenant_id: tenantId, limit: "50"});
  if (status) query.set("status_filter", status);
  const data = await api("/v1/workspace/tasks?" + query.toString());
  const items = data.items || [];
  el("count-all").textContent = String(items.length);
  el("count-open").textContent = String(items.filter((x) => x.status === "OPEN").length);
  el("count-closed").textContent = String(items.filter((x) => x.status !== "OPEN").length);
  renderTasks(items);
}
async function createTask() {
  const button = el("save-task");
  busy(button, true);
  try {
    await api("/v1/workspace/tasks", {
      method: "POST",
      headers: {"Idempotency-Key": crypto.randomUUID()},
      body: JSON.stringify({
        tenant_id: tenantId,
        title: el("task-title").value.trim(),
        assigned_to: el("assignee").value.trim(),
      }),
    });
    el("create-form").reset();
    feedback("Tugas tersimpan di database. Notifikasi otomatis belum tersedia.");
    await loadTasks();
  } catch (error) { feedback(error.message, true); }
  finally { busy(button, false); }
}
async function logout() {
  const oldIdToken = idToken;
  accessToken = null; idToken = null;
  sessionStorage.removeItem("edarms_state_v1");
  sessionStorage.removeItem("edarms_pkce_v1");
  toggleView(false);
  feedback("Token browser telah dihapus. Logout/revokasi server lintas sesi belum diimplementasikan di PoC.");
  if (oldIdToken) {
    try {
      const conf = await config();
      const url = new URL(conf.issuer + "/protocol/openid-connect/logout");
      url.searchParams.set("client_id", conf.client_id);
      url.searchParams.set("id_token_hint", oldIdToken);
      url.searchParams.set("post_logout_redirect_uri", redirectUri());
      location.assign(url.toString());
    } catch { /* Browser session already cleared; remote IdP may be unavailable. */ }
  }
}
el("toggle-nav").addEventListener("click", () => {
  if (matchMedia("(max-width: 850px)").matches) {
    const open = document.body.classList.toggle("mobile-nav");
    el("toggle-nav").setAttribute("aria-expanded", String(open));
  } else {
    const collapsed = document.body.classList.toggle("collapsed");
    el("toggle-nav").setAttribute("aria-expanded", String(!collapsed));
  }
});
el("login").addEventListener("click", () => { startLogin().catch(e => feedback(e.message, true)); });
el("logout").addEventListener("click", logout);
el("tenant-form").addEventListener("submit", (e) => { e.preventDefault(); openWorkspace().catch(err => feedback(err.message, true)); });
el("create-form").addEventListener("submit", (e) => { e.preventDefault(); createTask(); });
el("status-filter").addEventListener("change", () => { loadTasks().catch(err => feedback(err.message, true)); });
el("refresh").addEventListener("click", () => { loadTasks().then(() => feedback("Daftar tugas berhasil dimuat ulang.")).catch(e => feedback(e.message, true)); });
handleCallback().catch(e => { feedback(e.message, true); toggleView(false); });