"""Custom Swagger UI page: dark 'Aurora' theme, user banner, password eye toggle, response tables."""

SWAGGER_HTML = r"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Event Management System API - Swagger UI</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        /* ===== Aurora theme colours ===== */
        :root {
            --surface: rgba(30, 24, 48, 0.82);
            --surface-2: rgba(44, 36, 68, 0.95);
            --input: #1b1530;
            --border: rgba(255, 255, 255, 0.08);
            --text: #f4f1fb;
            --muted: #a49cbc;
            --amber: #f59e0b;
            --magenta: #d946ef;
            --gradient: linear-gradient(90deg, #f59e0b, #ec4899, #8b5cf6);
            --radius: 22px;
        }
        html, body { margin: 0; min-height: 100%; }
        body {
            color: var(--text);
            font-family: "Poppins", "Segoe UI", Arial, sans-serif;
            background:
                radial-gradient(ellipse 55% 40% at 0% 0%, rgba(236, 72, 153, 0.22), transparent 60%),
                radial-gradient(ellipse 50% 40% at 100% 10%, rgba(139, 92, 246, 0.25), transparent 60%),
                linear-gradient(180deg, #120c22 0%, #1a1233 45%, #231a40 100%);
            background-attachment: fixed;
        }
        .swagger-ui, .swagger-ui .opblock-tag, .swagger-ui .btn, .swagger-ui input,
        .swagger-ui select, .swagger-ui textarea, .swagger-ui table, .swagger-ui label {
            font-family: "Poppins", "Segoe UI", Arial, sans-serif !important;
        }
        .swagger-ui pre, .swagger-ui code, .swagger-ui .microlight,
        .swagger-ui .opblock .opblock-summary-path { font-family: "JetBrains Mono", Consolas, monospace !important; }

        /* ===== Top banner ===== */
        #banner {
            position: sticky; top: 0; z-index: 999;
            display: flex; align-items: center; justify-content: space-between;
            padding: 14px 28px;
            background: rgba(18, 12, 34, 0.75);
            backdrop-filter: blur(14px);
            border-bottom: 1px solid var(--border);
        }
        #brand { display: flex; align-items: center; gap: 12px; font-size: 18px; font-weight: 700; }
        #brand-logo {
            width: 40px; height: 40px; border-radius: 12px;
            background: var(--gradient);
            display: flex; align-items: center; justify-content: center; font-size: 20px;
        }
        #brand small { display: block; font-size: 12px; font-weight: 400; color: var(--muted); }
        #user-box { display: flex; align-items: center; gap: 12px; }
        #user-chip {
            display: flex; align-items: center; gap: 10px;
            background: var(--surface-2); padding: 6px 18px 6px 6px; border-radius: 999px;
        }
        #avatar {
            width: 34px; height: 34px; border-radius: 50%; background: #3b3352;
            display: flex; align-items: center; justify-content: center; font-weight: 700;
        }
        #user-name { font-size: 14px; font-weight: 600; }
        #user-email { font-size: 12px; color: var(--muted); }
        #role-pill { display: none; padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; color: #fff; }
        #logout-btn {
            display: none; background: transparent; color: var(--text);
            border: 1px solid var(--border); padding: 10px 22px; border-radius: 999px;
            font-weight: 600; cursor: pointer;
        }
        #logout-btn:hover { background: var(--surface-2); }

        /* ===== Hero ===== */
        #hero { max-width: 1100px; margin: 26px auto 0; padding: 0 20px; }
        #hero-card {
            border-radius: var(--radius); padding: 22px 26px;
            background: var(--surface); border: 1px solid var(--border);
            position: relative; overflow: hidden;
        }
        #hero-card:before { content: ""; position: absolute; left: 0; top: 0; right: 0; height: 4px; background: var(--gradient); }
        #hero-card h1 { margin: 0 0 6px; font-size: 26px; }
        #hero-card p { margin: 0; color: var(--muted); font-size: 14px; }
        .steps { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
        .step { background: var(--surface-2); border-radius: 999px; padding: 6px 14px; font-size: 13px; }

        /* ===== Swagger dark theme ===== */
        .swagger-ui .topbar, .swagger-ui .models, .swagger-ui .info { display: none !important; }
        .swagger-ui { max-width: 1100px; margin: 0 auto; padding: 10px 20px 40px; }
        .swagger-ui, .swagger-ui .opblock-tag, .swagger-ui .opblock .opblock-summary-path,
        .swagger-ui .opblock .opblock-summary-description, .swagger-ui .opblock .opblock-section-header h4,
        .swagger-ui .parameter__name, .swagger-ui .parameter__type, .swagger-ui table thead tr th,
        .swagger-ui table thead tr td, .swagger-ui .response-col_status, .swagger-ui .response-col_description,
        .swagger-ui .responses-inner h4, .swagger-ui .responses-inner h5, .swagger-ui .tab li, .swagger-ui label,
        .swagger-ui .markdown p, .swagger-ui .renderedMarkdown p, .swagger-ui .btn,
        .swagger-ui .dialog-ux .modal-ux-header h3, .swagger-ui .dialog-ux .modal-ux-content p,
        .swagger-ui .dialog-ux .modal-ux-content h4, .swagger-ui .auth-container h4,
        .swagger-ui .auth-container .wrapper, .swagger-ui .prop-type, .swagger-ui .model-title,
        .swagger-ui .opblock-description-wrapper p, .swagger-ui .response-control-media-type__accept-message {
            color: var(--text) !important;
        }
        .swagger-ui .parameter__in, .swagger-ui .opblock-tag small { color: var(--muted) !important; }
        .swagger-ui svg:not(:root) { fill: var(--muted); }
        .swagger-ui .scheme-container {
            background: var(--surface) !important; border: 1px solid var(--border) !important;
            border-radius: var(--radius) !important; box-shadow: none !important; margin: 18px 0 !important;
        }
        .swagger-ui .opblock-tag {
            border-bottom: none !important; font-size: 21px !important; font-weight: 600;
            padding: 16px 6px 8px !important;
        }
        .swagger-ui .opblock-tag:hover { background: transparent !important; }
        .swagger-ui .opblock {
            background: var(--surface) !important; border: 1px solid var(--border) !important;
            border-radius: var(--radius) !important; box-shadow: none !important;
            margin-bottom: 12px !important; overflow: hidden;
        }
        .swagger-ui .opblock .opblock-summary { border-bottom: none !important; padding: 12px 16px; }
        .swagger-ui .opblock.is-open .opblock-summary { border-bottom: 1px solid var(--border) !important; }
        .swagger-ui .opblock .opblock-section-header { background: var(--surface-2) !important; box-shadow: none !important; }
        .swagger-ui .opblock-body, .swagger-ui .opblock-description-wrapper { background: transparent !important; }

        /* Method badges */
        .swagger-ui .opblock .opblock-summary-method {
            border-radius: 10px !important; min-width: 76px; padding: 7px 0 !important;
            font-weight: 700; font-size: 12px; text-shadow: none;
        }
        .swagger-ui .opblock.opblock-get    .opblock-summary-method { background: #0e3a4a !important; color: #67e8f9 !important; }
        .swagger-ui .opblock.opblock-post   .opblock-summary-method { background: #3b2a06 !important; color: #fcd34d !important; }
        .swagger-ui .opblock.opblock-patch  .opblock-summary-method { background: #3b1450 !important; color: #f0abfc !important; }
        .swagger-ui .opblock.opblock-put    .opblock-summary-method { background: #2e1f4f !important; color: #c4b5fd !important; }
        .swagger-ui .opblock.opblock-delete .opblock-summary-method { background: #4c1d2a !important; color: #fda4af !important; }
        .swagger-ui .opblock.opblock-get    { border-left: 4px solid #22d3ee !important; }
        .swagger-ui .opblock.opblock-post   { border-left: 4px solid var(--amber) !important; }
        .swagger-ui .opblock.opblock-patch  { border-left: 4px solid var(--magenta) !important; }
        .swagger-ui .opblock.opblock-delete { border-left: 4px solid #fb7185 !important; }

        /* Inputs and dropdowns */
        .swagger-ui input[type=text], .swagger-ui input[type=password], .swagger-ui input[type=email],
        .swagger-ui textarea, .swagger-ui select {
            background: var(--input) !important; color: var(--text) !important;
            border: 1px solid var(--border) !important; border-radius: 14px !important;
            padding: 10px 14px !important; box-shadow: none !important; min-width: 260px;
        }
        .swagger-ui select { cursor: pointer; }
        .swagger-ui input:focus, .swagger-ui select:focus, .swagger-ui textarea:focus {
            outline: none !important; border-color: var(--magenta) !important;
        }
        .swagger-ui .parameter__name.required:after, .swagger-ui .parameter__name.required span { color: #fb7185 !important; }

        /* Buttons */
        .swagger-ui .btn {
            background: var(--surface-2) !important; border: none !important;
            border-radius: 999px !important; box-shadow: none !important; font-weight: 600 !important;
        }
        .swagger-ui .btn.execute, .swagger-ui .btn.authorize, .swagger-ui .auth-btn-wrapper .btn.modal-btn.auth.authorize {
            background: var(--gradient) !important; color: #fff !important;
        }
        .swagger-ui .btn.authorize span { color: #fff !important; }
        .swagger-ui .btn.authorize svg { fill: #fff !important; }
        .swagger-ui .btn.cancel { color: #fda4af !important; }

        /* Code, modal */
        .swagger-ui .highlight-code, .swagger-ui .microlight, .swagger-ui pre {
            background: #140f24 !important; color: #ece8f5 !important; border-radius: 14px !important;
        }
        .swagger-ui table tbody tr td { border-color: var(--border) !important; color: var(--text); }
        .swagger-ui .dialog-ux .backdrop-ux { background: rgba(10, 6, 20, 0.7) !important; }
        .swagger-ui .dialog-ux .modal-ux {
            background: #1e1730 !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important;
        }
        .swagger-ui .dialog-ux .modal-ux-header { border-bottom: 1px solid var(--border) !important; }

        /* ===== Response tables ===== */
        .resp-wrap { overflow-x: auto; margin: 10px 0 14px; border-radius: 14px; border: 1px solid var(--border); }
        .resp-table { width: 100%; border-collapse: collapse; font-size: 13px; }
        .resp-table th, .resp-table td {
            text-align: left; padding: 8px 12px; border-bottom: 1px solid var(--border);
            color: var(--text); white-space: nowrap;
        }
        .resp-table tr:first-child th { background: var(--surface-2); }
        .resp-table.kv th { width: 200px; color: var(--muted); font-weight: 600; background: transparent; }
        .badge { padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }

        /* Password eye */
        .pwd-wrap { position: relative; display: inline-block; }
        .pwd-eye {
            position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
            background: none; border: none; cursor: pointer; font-size: 15px;
        }
        ::-webkit-scrollbar { width: 10px; }
        ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.14); border-radius: 10px; }
    </style>
</head>
<body>
    <div id="banner">
        <div id="brand">
            <span id="brand-logo">🎟️</span>
            <span>EventHub API<small>Event Management System</small></span>
        </div>
        <div id="user-box">
            <div id="user-chip">
                <span id="avatar">?</span>
                <span><div id="user-name">Not logged in</div><div id="user-email">Use Authorize to log in</div></span>
                <span id="role-pill"></span>
            </div>
            <button id="logout-btn" onclick="logout()">Logout</button>
        </div>
    </div>

    <div id="hero">
        <div id="hero-card">
            <h1>Event Management System API</h1>
            <p>Create events, sell tickets, take payments and manage bookings. Fill the forms and pick values from the dropdowns.</p>
            <div class="steps">
                <span class="step">1. Register</span>
                <span class="step">2. Authorize (email + password)</span>
                <span class="step">3. Create event + tickets</span>
                <span class="step">4. Publish</span>
                <span class="step">5. Book</span>
                <span class="step">6. Pay</span>
                <span class="step">7. Cancel / Refund</span>
            </div>
        </div>
    </div>
    <div id="swagger-ui"></div>

    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
        let ui;
        const SCHEME = "OAuth2PasswordBearer";
        const TOKEN_KEY = "ems_token";
        const ROLE_COLORS = { ADMIN: "#db2777", ORGANIZER: "#d97706", CUSTOMER: "#7c3aed" };
        const STATUS_COLORS = {
            PUBLISHED: "#15803d", CONFIRMED: "#15803d", SUCCESS: "#15803d",
            DRAFT: "#475569", PENDING: "#b45309",
            CANCELLED: "#be123c", FAILED: "#be123c", REFUNDED: "#6d28d9", COMPLETED: "#0e7490"
        };

        // ---------- Banner ----------
        function showUser(user) {
            const pill = document.getElementById("role-pill");
            const avatar = document.getElementById("avatar");
            if (!user) {
                avatar.textContent = "?";
                avatar.style.background = "#3b3352";
                document.getElementById("user-name").textContent = "Not logged in";
                document.getElementById("user-email").textContent = "Use Authorize to log in";
                pill.style.display = "none";
                document.getElementById("logout-btn").style.display = "none";
                return;
            }
            avatar.textContent = user.name.trim().charAt(0).toUpperCase();
            avatar.style.background = ROLE_COLORS[user.role];
            document.getElementById("user-name").textContent = user.name;
            document.getElementById("user-email").textContent = user.email;
            pill.textContent = user.role;
            pill.style.background = ROLE_COLORS[user.role];
            pill.style.display = "inline-block";
            document.getElementById("logout-btn").style.display = "inline-block";
        }

        async function loadUser(token) {
            const res = await fetch("/api/users/me", { headers: { Authorization: "Bearer " + token } });
            if (!res.ok) { logout(); return; }
            showUser(await res.json());
        }

        function logout() {
            localStorage.removeItem(TOKEN_KEY);
            if (ui) ui.authActions.logout([SCHEME]);
            showUser(null);
        }

        // ---------- Password eye toggle ----------
        function addPasswordEyes() {
            document.querySelectorAll("input").forEach((input) => {
                const label = (input.placeholder || input.getAttribute("aria-label") || "").toLowerCase();
                if (input.dataset.eye || !(label.includes("password") || input.type === "password")) return;
                input.dataset.eye = "1";
                input.type = "password";
                const wrap = document.createElement("span");
                wrap.className = "pwd-wrap";
                input.parentNode.insertBefore(wrap, input);
                wrap.appendChild(input);
                const eye = document.createElement("button");
                eye.type = "button";
                eye.className = "pwd-eye";
                eye.textContent = "👁️";
                eye.onclick = () => {
                    input.type = input.type === "password" ? "text" : "password";
                    eye.textContent = input.type === "password" ? "👁️" : "🙈";
                };
                wrap.appendChild(eye);
            });
        }

        // ---------- Response body as a table ----------
        function cell(td, key, v) {
            if (v === null || v === undefined || v === "") { td.textContent = "-"; return; }
            if (typeof v === "string" && STATUS_COLORS[v]) {
                td.innerHTML = '<span class="badge" style="background:' + STATUS_COLORS[v] + '">' + v + "</span>";
                return;
            }
            if (Array.isArray(v)) {
                td.textContent = v.length && typeof v[0] === "object"
                    ? v.map((x) => Object.entries(x).map(([a, b]) => a + ": " + b).join(", ")).join(" | ")
                    : v.join(", ");
                return;
            }
            td.textContent = typeof v === "object" ? JSON.stringify(v) : String(v);
        }

        function buildTable(data) {
            const rows = Array.isArray(data) ? data : (data && Array.isArray(data.items) ? data.items : null);
            const table = document.createElement("table");
            table.className = "resp-table";
            if (rows) {
                if (!rows.length) { table.insertRow().insertCell().textContent = "No records found"; return table; }
                const cols = Object.keys(rows[0]);
                const head = table.insertRow();
                cols.forEach((c) => { const th = document.createElement("th"); th.textContent = c; head.appendChild(th); });
                rows.forEach((r) => { const tr = table.insertRow(); cols.forEach((c) => cell(tr.insertCell(), c, r[c])); });
                if (!Array.isArray(data)) {   // paginated result: show page info under the table
                    const tr = table.insertRow();
                    const td = tr.insertCell();
                    td.colSpan = cols.length;
                    td.textContent = "Page " + data.page + " of " + data.pages + "  ·  " + data.total + " result(s)";
                }
            } else {
                table.classList.add("kv");
                Object.entries(data).forEach(([k, v]) => {
                    const tr = table.insertRow();
                    const th = document.createElement("th");
                    th.textContent = k;
                    tr.appendChild(th);
                    cell(tr.insertCell(), k, v);
                });
            }
            return table;
        }

        function renderResponseTables() {
            document.querySelectorAll(".live-responses-table .highlight-code").forEach((box) => {
                const text = box.textContent.trim();
                if (box.dataset.tableFor === text) return;
                let data;
                try { data = JSON.parse(text); } catch (e) { return; }
                if (!data || typeof data !== "object") return;
                const old = box.previousElementSibling;
                if (old && old.classList.contains("resp-wrap")) old.remove();
                const wrap = document.createElement("div");
                wrap.className = "resp-wrap";
                wrap.appendChild(buildTable(data));
                box.parentNode.insertBefore(wrap, box);
                box.dataset.tableFor = text;
            });
        }

        new MutationObserver(() => { addPasswordEyes(); renderResponseTables(); })
            .observe(document.body, { childList: true, subtree: true });

        // ---------- Swagger UI ----------
        window.onload = () => {
            ui = SwaggerUIBundle({
                url: "/openapi.json",
                dom_id: "#swagger-ui",
                defaultModelsExpandDepth: -1,
                persistAuthorization: true,
                displayRequestDuration: true,
                responseInterceptor: (res) => {
                    // After a successful login (Authorize button or the /login endpoint), show who is logged in
                    if (res.url.includes("/api/auth/login") && res.status === 200) {
                        const token = (res.body || JSON.parse(res.text)).access_token;
                        localStorage.setItem(TOKEN_KEY, token);
                        // also unlock the padlocks, so later requests send the token
                        ui.authActions.authorize({
                            [SCHEME]: {
                                name: SCHEME,
                                schema: { type: "oauth2", flow: "password", tokenUrl: "/api/auth/login" },
                                token: { access_token: token, token_type: "bearer" },
                            },
                        });
                        loadUser(token);
                    }
                    return res;
                },
            });
            const saved = localStorage.getItem(TOKEN_KEY);
            if (saved) loadUser(saved); else showUser(null);
        };
    </script>
</body>
</html>
"""
