const app = document.querySelector("#app");

function readSession(key) {
    try { return sessionStorage.getItem(key); } catch (error) { console.warn("Không thể đọc phiên đăng nhập.", error); return null; }
}

function clearSession() {
    try { sessionStorage.clear(); } catch (error) { console.warn("Không thể xóa phiên đăng nhập.", error); }
}

function readPreference(key, fallback) {
    try { return localStorage.getItem(key) || fallback; } catch (error) { console.warn("Không thể đọc tùy chọn giao diện.", error); return fallback; }
}

function savePreference(key, value) {
    try { localStorage.setItem(key, value); } catch (error) { console.warn("Không thể lưu tùy chọn giao diện.", error); }
}

function readUser() {
    try { return JSON.parse(readSession("md-user") || "null"); } catch (error) {
        console.warn("Phiên đăng nhập không hợp lệ.", error);
        clearSession();
        return null;
    }
}
const state = { token: readSession("md-token"), user: readUser(), page: "dashboard", dashboard: null, donors: [], appointments: [], campaigns: [], notifications: [], accounts: [], notificationsOpen: false, avatarMenuOpen: false, theme: readPreference("md-theme", "light") === "dark" ? "dark" : "light" };
document.documentElement.dataset.theme = state.theme;
const pages = { dashboard: "Tổng quan", campaigns: "Chiến dịch", accounts: "Quản lý tài khoản", donors: "Người đăng ký", appointments: "Lượt hẹn", ai: "Hỏi đáp AI", "ai-reports": "Báo cáo thống kê", reminders: "Nhắc lịch" };
const icons = { dashboard: "📊", campaigns: "🚩", accounts: "👥", donors: "♙", appointments: "▦", ai: "💬", "ai-reports": "📊", reminders: "🔔" };
const canManage = () => Boolean(state.user && ["admin", "coordinator"].includes(state.user.role));
const esc = (value) => String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
const prettyDate = (value, options = { day: "numeric", month: "short", year: "numeric" }) => new Intl.DateTimeFormat("vi-VN", options).format(new Date(`${value}T00:00:00`));
const initials = (name) => String(name || "?").split(/\s+/).slice(-2).map((part) => part[0]).join("").toUpperCase();

async function api(path, options = {}) {
    let response;
    try {
        response = await fetch(path, {...options, headers: { "Content-Type": "application/json", ...(state.token ? { Authorization: `Bearer ${state.token}` } : {}), ...options.headers } });
    } catch (error) {
        throw new Error("Không thể kết nối máy chủ. Vui lòng thử lại.", { cause: error });
    }
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || "Không thể hoàn tất yêu cầu");
    return data;
}

function toast(message) {
    const previousToast = document.querySelector(".toast");
    if (previousToast) previousToast.remove();
    if (!document.body) return;
    const node = document.createElement("div");
    node.className = "toast";
    node.textContent = message;
    document.body.append(node);
    setTimeout(() => node.remove(), 3400);
}

function loginView() {
    if (!app) {
        console.error("Không tìm thấy vùng giao diện #app.");
        return;
    }
    app.innerHTML = `<main class="login-shell">
    <aside class="login-art"><div class="brand"><span class="brand-mark">+</span>Mạch Đỏ</div>
      <div class="art-copy"><div class="eyebrow">Điều phối cộng đồng · 2026</div><h1>Một nhịp sẻ chia, vạn điều hy vọng.</h1><p>Nền tảng điều phối chiến dịch hiến máu tình nguyện, từ lịch hẹn đến những lời nhắc kịp lúc.</p></div>
      <div class="art-foot">Mạch Đỏ · Hệ thống quản lý hiến máu tình nguyện</div></aside>
    <section class="login-form-side"><div class="auth-container">
      <div id="login-view" class="auth-view active"><form class="login-form" id="login-form"><div class="brand login-mark"><span class="brand-mark">+</span>Mạch Đỏ</div><div class="eyebrow">Không gian điều phối</div><h2>Chào mừng trở lại</h2><p>Đăng nhập để tiếp tục điều phối những hành trình sẻ chia.</p>
        <div class="field"><label for="login-email">Email hoặc tên tài khoản</label><input id="login-email" name="email" type="text" autocomplete="username" placeholder="Ví dụ: admin@machdo.com hoặc admin" required></div>
        <div class="field"><label for="password">Mật khẩu</label><input id="password" name="password" type="password" autocomplete="current-password" placeholder="Nhập mật khẩu của bạn" required></div>
        <button class="button" style="width:100%;margin-top:9px" type="submit">Đăng nhập <span aria-hidden="true">→</span></button>
        <div class="auth-switch-text" style="text-align: center; margin-top: 16px; margin-bottom: 20px; font-size: 14px; color: #555;">Chưa có tài khoản? <a href="#" id="btn-show-register" class="auth-toggle-link" style="color: #D9383A; font-weight: 600; text-decoration: underline; margin-left: 4px;">Đăng ký ngay</a></div>
      </form></div>
      <div id="register-view" class="auth-view"><form class="login-form" id="register-form"><div class="brand login-mark"><span class="brand-mark">+</span>Mạch Đỏ</div><div class="eyebrow">TẠO TÀI KHOẢN MỚI</div><h2>Tham gia Mạch Đỏ</h2><p>Đăng ký tài khoản để đăng ký hiến máu và theo dõi hành trình.</p>
        <div class="field"><label for="reg-fullname">Họ và tên</label><input id="reg-fullname" name="full_name" autocomplete="name" required minlength="2"></div>
        <div class="field"><label for="reg-email">Email</label><input id="reg-email" name="email" type="email" autocomplete="email" placeholder="nguyenvana@gmail.com" required></div>
        <div class="field"><label for="reg-password">Mật khẩu</label><input id="reg-password" name="password" type="password" autocomplete="new-password" required minlength="8"></div>
        <div class="field"><label for="reg-confirm-password">Nhập lại mật khẩu</label><input id="reg-confirm-password" name="confirm_password" type="password" autocomplete="new-password" required minlength="8"></div>
        <button type="submit" id="btn-submit-register" class="btn-primary button" style="width: 100%;">Tạo tài khoản →</button>
        <div class="auth-switch-text" style="text-align: center; margin-top: 16px; font-size: 14px; color: #555;">Đã có tài khoản? <a href="#" id="btn-show-login" class="auth-toggle-link" style="color: #D9383A; font-weight: 600; text-decoration: underline; margin-left: 4px;">Đăng nhập</a></div>
      </form></div>
    </div></section></main>`;
    const loginForm = document.querySelector("#login-form");
    const registerForm = document.querySelector("#register-form");
    const loginView = document.querySelector("#login-view");
    const registerView = document.querySelector("#register-view");
    const registerLink = document.querySelector("#btn-show-register");
    const loginLink = document.querySelector("#btn-show-login");
    if (!loginForm || !registerForm || !loginView || !registerView || !registerLink || !loginLink) {
        toast("Không thể khởi tạo biểu mẫu đăng nhập.");
        return;
    }
    const showAuthView = (view) => {
        loginView.classList.toggle("active", view === "login");
        registerView.classList.toggle("active", view === "register");
        const firstInput = (view === "register" ? registerForm : loginForm).querySelector("input");
        if (firstInput) firstInput.focus();
    };
    registerLink.addEventListener("click", (event) => {
        event.preventDefault();
        showAuthView("register");
    });
    loginLink.addEventListener("click", (event) => {
        event.preventDefault();
        showAuthView("login");
    });
    loginForm.addEventListener("submit", async(event) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        try {
            const result = await api("/api/login", { method: "POST", body: JSON.stringify({ email: form.get("email"), password: form.get("password") }) });
            state.token = result.token;
            state.user = result.user;
            try {
                sessionStorage.setItem("md-token", state.token);
                sessionStorage.setItem("md-user", JSON.stringify(state.user));
            } catch (storageError) {
                console.warn("Không thể lưu phiên đăng nhập trong trình duyệt.", storageError);
            }
            await loadData();
            render();
        } catch (error) { toast(error.message); }
    });
    registerForm.addEventListener("submit", async(event) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        const password = String(form.get("password") || "");
        const confirmPassword = String(form.get("confirm_password") || "");
        const email = String(form.get("email") || "").trim();
        if (!form.get("full_name") || !email || !password || !confirmPassword) {
            toast("Vui lòng điền đầy đủ thông tin.");
            return;
        }
        if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
            toast("Vui lòng nhập email hợp lệ.");
            return;
        }
        if (password !== confirmPassword) {
            toast("Mật khẩu xác nhận không khớp.");
            return;
        }
        try {
            await api("/api/register", { method: "POST", body: JSON.stringify({ email, password, full_name: form.get("full_name") }) });
            registerForm.reset();
            showAuthView("login");
            toast("Đăng ký thành công!");
        } catch (error) { toast(error.message); }
    });
}

async function loadData() {
    if (!state.token) return;
    try {
        if (canManage()) {
            [state.dashboard, state.donors, state.appointments, state.campaigns, state.notifications] = await Promise.all([
                api("/api/dashboard"), api("/api/donors"), api("/api/appointments"), api("/api/campaigns"), api("/api/notifications")
            ]);
            state.accounts = state.user.role === "admin" ? await api("/api/admin/users") : [];
        } else {
            const [ownDonor, appointments, campaigns, notifications] = await Promise.all([
                api("/api/donors/me"), api("/api/appointments"), api("/api/campaigns"), api("/api/notifications")
            ]);
            state.dashboard = null;
            state.donors = [ownDonor];
            state.appointments = appointments;
            state.campaigns = campaigns;
            state.notifications = notifications;
        }
    } catch (error) {
        if (error.message === "Vui lòng đăng nhập") {
            state.token = null;
            state.user = null;
            clearSession();
        } else toast(error.message);
    }
}

function navigation() {
    const menu = state.user?.role === "admin"
        ? { dashboard: pages.dashboard, campaigns: pages.campaigns, accounts: pages.accounts, ai: pages.ai, "ai-reports": pages["ai-reports"], reminders: pages.reminders }
        : canManage() ? { dashboard: pages.dashboard, campaigns: pages.campaigns, donors: pages.donors, appointments: pages.appointments, ai: pages.ai, "ai-reports": pages["ai-reports"], reminders: pages.reminders }
            : { campaigns: pages.campaigns, appointments: pages.appointments, ai: pages.ai };
    return Object.entries(menu).map(([key, label]) => `<button class="nav-item ${state.page === key ? "active" : ""}" data-page="${key}"><span class="nav-icon">${icons[key]}</span>${label}</button>`).join("");
}

function shell(content) {
    const dateLabel = new Intl.DateTimeFormat("vi-VN", { weekday: "long", day: "numeric", month: "long" }).format(new Date());
    const unread = state.notifications.filter((item) => !Number(item.is_read)).length;
    const badge = unread ? `<span class="notification-badge">${unread > 99 ? "99+" : unread}</span>` : "";
    const items = state.notifications.map((item) => {
        const unreadClass = Number(item.is_read) ? "" : " unread";
        const icon = item.type === "reminder" ? "⏰" : "📢";
        return `<button type="button" class="notification-item${unreadClass}" data-action="read-notification" data-notification-id="${item.id}" aria-label="${esc(item.title)}${Number(item.is_read) ? "" : ", chưa đọc"}"><span class="notification-symbol" aria-hidden="true">${icon}</span><span class="notification-copy"><span class="notification-titleline"><strong>${esc(item.title)}</strong><time>${notificationTimestamp(item.created_at)}</time></span><span class="notification-message">${esc(item.message)}</span></span></button>`;
    }).join("");
    const notificationPanel = state.notificationsOpen ? `<section id="notification-panel" class="notification-panel" aria-label="Thông báo"><div class="notification-panel-head"><h2>Thông báo</h2><button type="button" data-action="mark-all-read" ${unread ? "" : "disabled"}>Đánh dấu tất cả là đã đọc</button></div><div class="notification-list">${items || `<p class="notification-empty">Bạn chưa có thông báo nào.</p>`}</div></section>` : "";
    const avatarMenu = state.avatarMenuOpen ? `<div class="avatar-dropdown" role="menu" aria-label="Tài khoản"><div class="avatar-menu-identity"><strong>${esc(state.user && state.user.display_name)}</strong><span>${esc(state.user && state.user.email)}</span></div><button type="button" class="avatar-menu-item" role="menuitem" data-action="profile"><span aria-hidden="true">👤</span> Hồ sơ cá nhân</button><button type="button" class="avatar-menu-item" role="menuitem" data-action="settings"><span aria-hidden="true">⚙️</span> Cài đặt</button><div class="avatar-menu-divider"></div><button type="button" class="avatar-menu-item avatar-menu-logout" role="menuitem" data-action="logout"><span aria-hidden="true">↗</span> Đăng xuất</button></div>` : "";
  return `<div class="app-shell"><aside class="sidebar"><div class="brand"><span class="brand-mark">+</span>Mạch Đỏ</div><div class="nav-label">Không gian làm việc</div><nav class="nav-list">${navigation()}</nav>
    <div class="side-bottom"><div class="user-mini"><div class="avatar">${initials(state.user && state.user.display_name)}</div><div><div class="user-name">${esc(state.user && state.user.display_name)}</div><div class="user-role">${esc(roleName(state.user && state.user.role))}</div></div></div><button class="logout" data-action="logout">↗ &nbsp;Đăng xuất</button></div></aside>
  <main class="main-area"><header class="topbar"><div class="breadcrumb">MẠCH ĐỎ &nbsp;/&nbsp; <strong>${pages[state.page]}</strong></div><div class="top-actions"><div class="date-chip">◷ &nbsp;${dateLabel}</div><div class="notification-wrap"><button type="button" class="notification-bell" data-action="toggle-notifications" aria-label="Thông báo${unread ? `, ${unread} chưa đọc` : ""}" aria-expanded="${state.notificationsOpen}" aria-controls="notification-panel" title="Thông báo"><span aria-hidden="true">🔔</span>${badge}</button>${notificationPanel}</div><div class="avatar-menu-wrap"><button type="button" class="avatar top-avatar" data-action="toggle-avatar-menu" aria-label="Tài khoản cá nhân" aria-expanded="${state.avatarMenuOpen}" aria-haspopup="menu" title="Tài khoản">${initials(state.user && state.user.display_name)}</button>${avatarMenu}</div></div></header><section class="content">${content}</section></main>
    <nav class="mobile-nav">${navigation()}</nav></div><dialog id="modal"></dialog>`;
}

function notificationTimestamp(value) {
  const timestamp = new Date(`${String(value || "").replace(" ", "T")}Z`);
  return Number.isNaN(timestamp.getTime()) ? "" : new Intl.DateTimeFormat("vi-VN", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }).format(timestamp);
}

function roleName(role) { return ({ admin: "Quản trị viên", coordinator: "Điều phối viên", volunteer: "Tình nguyện viên" })[role] || "Thành viên"; }

function heading(kicker, title, subtitle, action = "") { return `<div class="page-heading"><div><div class="eyebrow">${kicker}</div><h1>${title}</h1><p>${subtitle}</p></div>${action}</div>`; }

function metric(label, value, icon, foot) { return `<article class="metric"><div class="metric-top"><span>${label}</span><span class="metric-icon">${icon}</span></div><div class="metric-value">${value}</div><div class="metric-foot">${foot}</div></article>`; }

function dashboardView() {
    const data = state.dashboard || {};
    const dateToday = new Intl.DateTimeFormat("vi-VN", { month: "short" });
    const campaignRows = (data.campaigns || []).slice(0, 4).map((event) => `<div class="event-row" data-action="view-campaign" data-campaign="${event.id}" style="cursor:pointer" title="Nhấn để xem chi tiết chiến dịch"><div class="date-block"><strong>${new Date(`${event.campaign_date}T00:00:00`).getDate()}</strong><small>${dateToday.format(new Date(`${event.campaign_date}T00:00:00`))}</small></div><div><div class="event-title">${esc(event.title)}</div><div class="event-sub">${esc(event.venue)} · ${event.start_time}–${event.end_time}</div></div><div class="seat-count">${event.slots.reduce((sum, slot) => sum + slot.booked, 0)} lượt hẹn</div></div>`).join("") || `<div class="empty">Chưa có chiến dịch nào.</div>`;
  const maxGroup = Math.max(1, ...(data.blood_groups || []).map((group) => group.value));
  const groupRows = (data.blood_groups || []).map((group) => `<div class="blood-line"><span class="blood-type">${esc(group.name)}</span><div class="bar-track"><div class="bar-fill" style="width:${Math.max(5, group.value / maxGroup * 100)}%"></div></div><span class="blood-num">${group.value}</span></div>`).join("");
  const recentRows = (data.recent || []).map((item) => `<tr><td><div class="person-cell"><span class="person-dot">${initials(item.full_name)}</span>${esc(item.full_name)}</div></td><td>${esc(item.campaign_title)}</td><td>${esc(item.blood_group)}</td><td>${statusPill(item.status)}</td></tr>`).join("");
  return `${heading("BẢNG ĐIỀU KHIỂN", `Xin chào, ${esc(state.user && state.user.display_name)}`, "Cùng xem nhịp đập của các chiến dịch hôm nay.")}
    <div class="metric-grid">${metric("Người đăng ký", data.total_donors ?? 0, "♙", "Hồ sơ trong hệ thống")}${metric("Lượt giữ chỗ", data.registrations ?? 0, "▦", `${data.attended ?? 0} lượt đã tham gia`)}${metric("Chiến dịch sắp tới", data.upcoming_campaigns ?? 0, "⌑", "Đang mở đăng ký")}${metric("Tỷ lệ tham gia", data.registrations ? `${Math.round(data.attended / data.registrations * 100)}%` : "0%", "↗", "Trên tổng lượt giữ chỗ")}</div>
    <div class="dash-grid"><section class="section"><div class="section-head"><h2>Chiến dịch sắp diễn ra</h2><div style="display:flex;gap:8px;align-items:center;">${canManage() ? `<button class="button small" data-action="new-campaign">＋ Tạo chiến dịch</button>` : ""}<button class="button secondary small" data-page="campaigns">Xem tất cả →</button></div></div><div class="event-list">${campaignRows}</div></section>
    <section class="section"><div class="section-head"><h2>Phân bố nhóm máu</h2><span>Dữ liệu demo</span></div><div class="blood-list">${groupRows || `<div class="empty">Chưa có dữ liệu nhóm máu.</div>`}</div></section></div>
    <section class="section" style="margin-top:15px"><div class="section-head"><h2>Đăng ký gần đây</h2><button class="button secondary small" data-page="appointments">Mở danh sách →</button></div><div class="table-wrap"><table><thead><tr><th>NGƯỜI ĐĂNG KÝ</th><th>CHIẾN DỊCH</th><th>NHÓM MÁU</th><th>TRẠNG THÁI</th></tr></thead><tbody>${recentRows || `<tr><td colspan="4" class="empty">Chưa có lượt đăng ký nào.</td></tr>`}</tbody></table></div></section>`;
}

function statusPill(value) {
  const tone = value === "Đã tham gia" ? "" : value === "Vắng mặt" || value === "Đã hủy" ? "red" : "gold";
  const label = value === "Đã tham gia" ? "Đã tham gia hiến máu" : value;
  return `<span class="pill ${tone}">${esc(label)}</span>`;
}

function campaignsView() {
  const cards = state.campaigns.map((event) => `<article class="campaign-item"><div class="campaign-topline"><div class="eyebrow">${prettyDate(event.campaign_date)}</div>${canManage() ? `<select class="campaign-status" data-campaign-status="${event.id}" aria-label="Trạng thái ${esc(event.title)}">${["Đang mở", "Tạm dừng", "Đã đóng"].map((status) => `<option ${event.status === status || (event.status === "Đã kết thúc" && status === "Đã đóng") ? "selected" : ""}>${status}</option>`).join("")}</select>` : `<span class="pill">${esc(event.status === "Đã kết thúc" ? "Đã đóng" : event.status)}</span>`}</div><h3>${esc(event.title)}</h3><div class="campaign-creator-pill" title="Người tạo chiến dịch"><span class="creator-icon">👤</span> Tạo bởi: <strong>${esc(event.created_by || "Điều phối viên (dieuphoi@machdo.com)")}</strong></div><div class="campaign-meta"><span>⌖ ${esc(event.venue)}</span><span>◷ ${event.start_time}–${event.end_time}</span></div><div class="slot-list">${event.slots.map((slot) => {
    const ratio = Math.min(100, slot.booked / slot.capacity * 100);
    return `<div class="slot-row"><div class="slot-left"><span>${slot.start_at.slice(11)}–${slot.end_at.slice(11)}</span><span class="slot-meter"><span style="width:${ratio}%"></span></span><span>${slot.booked}/${slot.capacity}</span></div><button class="button small" data-action="book" data-slot="${slot.id}" ${slot.booked >= slot.capacity || event.status !== "Đang mở" ? "disabled" : ""}>Đăng ký</button></div>`;
  }).join("")}</div><div class="campaign-actions"><button class="button secondary small" data-action="view-campaign" data-campaign="${event.id}">👁️ Chi tiết</button>${canManage() ? `<button class="button secondary small" data-action="edit-campaign" data-campaign="${event.id}">Sửa</button><button class="button danger-quiet small" data-action="delete-campaign" data-campaign="${event.id}">Xóa</button>` : ""}</div></article>`).join("");
  return `${heading("ĐIỀU PHỐI", "Chiến dịch", "Quản lý điểm hiến, thời gian và sức chứa từng khung giờ.", canManage() ? `<button class="button" data-action="new-campaign">＋ Tạo chiến dịch</button>` : "")}
    <div class="campaign-grid">${cards || `<div class="section empty">Chưa có chiến dịch.</div>`}</div>`;
}

function donorsView(query = "") {
  const filtered = state.donors.filter((person) => `${person.full_name} ${person.phone} ${person.blood_group}`.toLowerCase().includes(query.toLowerCase()));
  const rows = filtered.map((person) => `<tr><td><div class="person-cell"><span class="person-dot">${initials(person.full_name)}</span>${esc(person.full_name)}</div></td><td>${esc(person.phone)}</td><td>${esc(person.email || "—")}</td><td>${esc(person.blood_group)}</td><td>${prettyDate(person.created_at ? person.created_at.slice(0, 10) : new Date().toISOString().slice(0, 10))}</td></tr>`).join("");
  return `${heading("CỘNG ĐỒNG", "Người đăng ký", `${state.donors.length} hồ sơ · Nhóm máu lưu ở mức dữ liệu demo.`, canManage() ? `<button class="button" data-action="new-donor">＋ Thêm hồ sơ</button>` : "")}
    <div class="toolbar"><div class="filter-row"><input class="search" id="donor-search" placeholder="Tìm tên, số điện thoại, nhóm máu…" value="${esc(query)}"></div><span class="pill">${filtered.length} kết quả</span></div>
    <section class="section"><div class="table-wrap"><table><thead><tr><th>HỌ TÊN</th><th>ĐIỆN THOẠI</th><th>EMAIL</th><th>NHÓM MÁU</th><th>NGÀY TẠO</th></tr></thead><tbody>${rows || `<tr><td colspan="5" class="empty">Không tìm thấy hồ sơ phù hợp.</td></tr>`}</tbody></table></div></section>`;
}

function accountTimestamp(value) {
  const timestamp = new Date(`${String(value || "").replace(" ", "T")}Z`);
  return Number.isNaN(timestamp.getTime()) ? "—" : new Intl.DateTimeFormat("vi-VN", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" }).format(timestamp);
}

function adminUsersView() {
  const currentId = String(state.user.id);
  const rows = state.accounts.map((account) => {
    const isSelf = String(account.id) === currentId;
    const roleName = { volunteer: "Tình nguyện viên", coordinator: "Điều phối viên", admin: "Quản trị viên" }[account.role] || account.role;
    const statusName = account.status === "locked" ? "Đã khóa" : "Hoạt động";
    return `<tr><td><div class="account-identity"><strong>${esc(account.full_name)}</strong><span>${esc(account.email)}</span></div></td><td><span class="role-badge role-${esc(account.role)}">${esc(roleName)}</span></td><td>${accountTimestamp(account.created_at)}</td><td><span class="account-status status-${esc(account.status)}"><i></i>${statusName}</span></td><td><div class="account-actions"><button class="button secondary small" data-action="account-detail" data-user-id="${account.id}" title="Xem chi tiết tài khoản">👁️ Chi tiết</button><select data-user-role="${account.id}" aria-label="Vai trò của ${esc(account.full_name)}" ${isSelf ? "disabled" : ""}>${["volunteer", "coordinator", "admin"].map((role) => `<option value="${role}" ${account.role === role ? "selected" : ""}>${role}</option>`).join("")}</select><button class="button secondary small" data-action="account-status" data-user-id="${account.id}" data-status="${account.status === "locked" ? "active" : "locked"}" ${isSelf ? "disabled title=\"Không thể khóa tài khoản của bạn\"" : ""}>${account.status === "locked" ? "Mở khóa" : "Khóa"}</button><button class="button danger-quiet small" data-action="account-delete" data-user-id="${account.id}" data-user-name="${esc(account.full_name)}" ${isSelf ? "disabled title=\"Không thể xóa tài khoản của bạn\"" : ""}>Xóa</button></div></td></tr>`;
  }).join("");
  return `${heading("QUẢN TRỊ HỆ THỐNG", "Quản lý tài khoản", "Phân quyền và quản lý trạng thái tài khoản trong hệ thống.")}
    <section class="section"><div class="section-head account-section-head"><h2>Danh sách tài khoản</h2><div class="account-section-tools"><span>${state.accounts.length} tài khoản</span><button class="button" data-action="new-account">＋ Thêm tài khoản mới</button></div></div><div class="table-wrap"><table class="account-table"><thead><tr><th>HỌ TÊN &amp; EMAIL</th><th>VAI TRÒ</th><th>NGÀY GIỜ ĐĂNG KÝ</th><th>TRẠNG THÁI</th><th>THAO TÁC</th></tr></thead><tbody>${rows || `<tr><td colspan="5" class="empty">Chưa có tài khoản nào.</td></tr>`}</tbody></table></div></section>`;
}

function appointmentsView(query = "") {
  const filtered = state.appointments.filter((item) => `${item.full_name} ${item.campaign_title} ${item.status}`.toLowerCase().includes(query.toLowerCase()));
  const rows = filtered.map((item) => `<tr><td><div class="person-cell"><span class="person-dot">${initials(item.full_name)}</span>${esc(item.full_name)}</div></td><td>${esc(item.campaign_title)}</td><td>${prettyDate(item.start_at.slice(0, 10))} · ${item.start_at.slice(11)}</td><td>${esc(item.blood_group)}</td><td>${canManage() ? `<select class="status-select" data-appointment="${item.id}" aria-label="Trạng thái ${esc(item.full_name)}">${["Đã đăng ký", "Đã tham gia", "Vắng mặt", "Đã hủy"].map((status) => `<option value="${status}" ${item.status === status ? "selected" : ""}>${status === "Đã tham gia" ? "Đã tham gia hiến máu" : status}</option>`).join("")}</select>` : statusPill(item.status)}</td></tr>`).join("");
  return `${heading("LỊCH THAM GIA", "Lượt hẹn", "Theo dõi đăng ký, điểm hiến và trạng thái tham gia.")}
    <div class="toolbar"><div class="filter-row"><input class="search" id="appointment-search" placeholder="Tìm người hoặc chiến dịch…" value="${esc(query)}"></div><span class="pill">${filtered.length} lượt</span></div>
    <section class="section"><div class="table-wrap"><table><thead><tr><th>NGƯỜI ĐĂNG KÝ</th><th>CHIẾN DỊCH</th><th>KHUNG GIỜ</th><th>NHÓM MÁU</th><th>TRẠNG THÁI</th></tr></thead><tbody>${rows || `<tr><td colspan="5" class="empty">Chưa có lượt hẹn.</td></tr>`}</tbody></table></div></section>`;
}

function campaignOptions() { return state.campaigns.map((event) => `<option value="${event.id}">${esc(event.title)} · ${prettyDate(event.campaign_date)}</option>`).join(""); }
function aiQaView() {
  return `<section id="ai-qa-section">${heading("TRỢ LÝ QUY TRÌNH", "Hỏi đáp quy trình", "Tra cứu hướng dẫn hiến máu dựa trên tài liệu đã được duyệt.")}
    <div class="safety-note"><span>⚕</span><span><strong>Lưu ý sức khỏe:</strong> Trợ lý chỉ cung cấp hướng dẫn quy trình, không đánh giá sức khỏe hoặc điều kiện hiến máu cá nhân.</span></div>
    <section class="ai-assistant">
      <div class="assistant-intro"><span class="assistant-mark" aria-hidden="true">✳</span><div><h2>Hỏi về hành trình hiến máu</h2><p>Chọn một gợi ý hoặc nhập câu hỏi của bạn.</p></div></div>
      <div class="quick-suggestions" role="group" aria-label="Câu hỏi gợi ý">
        <button type="button" class="question-suggestion" data-suggestion="Trước khi hiến máu cần chuẩn bị gì?">Trước khi hiến máu cần chuẩn bị gì?</button>
        <button type="button" class="question-suggestion" data-suggestion="Sau khi hiến máu nên làm gì?">Sau khi hiến máu nên làm gì?</button>
        <button type="button" class="question-suggestion" data-suggestion="Khoảng cách giữa 2 lần hiến máu là bao lâu?">Khoảng cách giữa 2 lần hiến máu là bao lâu?</button>
      </div>
      <form id="procedure-form" class="procedure-form">
        <label for="procedure-question">Câu hỏi của bạn</label>
        <div class="question-composer"><textarea id="procedure-question" name="question" rows="4" maxlength="1000" placeholder="Ví dụ: Sau khi hiến máu cần lưu ý điều gì?" required></textarea><button type="submit" class="button green procedure-submit"><span aria-hidden="true">↗</span> Gửi câu hỏi</button></div>
      </form>
      <section class="answer-card" aria-label="Câu trả lời" aria-live="polite" aria-busy="false"><div class="answer-card-head"><span class="answer-mark" aria-hidden="true">✳</span><div><h3>Thông tin quy trình</h3><p id="answer-source">Câu trả lời sẽ hiển thị tại đây.</p></div></div><div id="answer-result" class="answer-copy"><p class="answer-placeholder">Câu trả lời chỉ dựa trên nguồn thông tin đã được duyệt.</p></div></section>
    </section></section>`;
}

function aiReportsView() {
  const campaignSummaries = state.campaigns.map((campaign) => `<article class="campaign-summary-card"><div><h3>${esc(campaign.title)}</h3><p>${prettyDate(campaign.campaign_date)} · ${esc(campaign.venue)}</p></div><div class="campaign-summary-metrics"><span>${campaign.slots.reduce((total, slot) => total + Number(slot.booked || 0), 0)} lượt đăng ký</span><span>${campaign.slots.reduce((total, slot) => total + Number(slot.capacity || 0), 0)} chỉ tiêu</span></div><button class="button secondary small" data-action="campaign-summary" data-campaign-id="${campaign.id}">Tạo tóm tắt AI</button><div class="campaign-summary-result" id="campaign-summary-${campaign.id}" aria-live="polite">Chưa tạo tóm tắt.</div></article>`).join("");
  return `<section id="ai-reports-section">${heading("PHÂN TÍCH CHIẾN DỊCH", "Báo cáo thống kê", "Tóm tắt lượt đăng ký theo chiến dịch và tổng hợp kết quả theo tháng/năm.")}
    <section class="section monthly-report-card"><div class="section-head"><div><h2>Tóm tắt chiến dịch</h2><span>Số liệu đăng ký và chỉ tiêu của từng chiến dịch.</span></div></div><div class="campaign-summary-list">${campaignSummaries || `<p class="empty">Chưa có chiến dịch.</p>`}</div></section>
    <section class="section monthly-report-card annual-report-section"><div class="section-head"><div><h2>Báo cáo tổng hợp (AI)</h2><span>Chọn kỳ báo cáo để xem thống kê và nhận xét xu hướng.</span></div></div>
      <div class="report-type-tabs" role="tablist" aria-label="Loại báo cáo"><button type="button" class="report-type-tab active" role="tab" aria-selected="true" aria-controls="monthly-report-panel" data-report-type="month">📅 Báo cáo theo Tháng</button><button type="button" class="report-type-tab" role="tab" aria-selected="false" aria-controls="yearly-report-panel" data-report-type="year">📆 Báo cáo theo Năm</button></div>
      <section id="monthly-report-panel" class="report-period-panel" role="tabpanel"><div class="report-controls"><label>Tháng<select id="report-month">${Array.from({length:12},(_,i)=>`<option value="${i+1}" ${i+1===new Date().getMonth()+1?'selected':''}>Tháng ${i+1}</option>`).join("")}</select></label><label>Năm<select id="report-month-year">${Array.from({length:7},(_,i)=>new Date().getFullYear()-3+i).map((year)=>`<option value="${year}" ${year===new Date().getFullYear()?'selected':''}>${year}</option>`).join("")}</select></label><button class="button green" data-action="monthly-report">Tạo báo cáo Tháng</button></div><div id="monthly-report-result" class="report-result" aria-live="polite"><p class="answer-placeholder">Chọn tháng và năm để tạo báo cáo.</p></div></section>
      <section id="yearly-report-panel" class="report-period-panel" role="tabpanel" hidden><div class="report-controls"><label>Năm<select id="report-year">${Array.from({length:7},(_,i)=>new Date().getFullYear()-3+i).map((year)=>`<option value="${year}" ${year===new Date().getFullYear()?'selected':''}>${year}</option>`).join("")}</select></label><button class="button green" data-action="yearly-report">Tạo báo cáo Năm</button></div><div id="yearly-report-result" class="report-result" aria-live="polite"><p class="answer-placeholder">Chọn năm để tạo báo cáo tổng kết.</p></div></section>
    </section></section>`;
}

function remindersView() {
  const history = state.notifications.map((item) => `<tr><td>${esc(item.title)}</td><td>${esc(item.message)}</td><td>${item.type === "reminder" ? "Nhắc lịch" : "Hệ thống"}</td><td>${notificationTimestamp(item.created_at)}</td></tr>`).join("");
  return `${heading("CHĂM SÓC CỘNG ĐỒNG", "Nhắc lịch", "Ghi nhận nhắc lịch demo cho người đã đăng ký.")}
    <section class="section" style="margin-bottom:14px"><div class="section-head"><div><h2>Gửi nhắc lịch chiến dịch</h2><span>Hệ thống chưa kết nối SMS hoặc email.</span></div></div><div class="reminder-form"><label for="reminder-campaign">Chiến dịch</label><select id="reminder-campaign" class="search">${campaignOptions()}</select><label for="reminder-message">Nội dung nhắc lịch</label><textarea id="reminder-message" rows="4" maxlength="2000">Trân trọng mời Quý tình nguyện viên tham gia hiến máu theo lịch hẹn tại chiến dịch [Tên chiến dịch]. Vui lòng mang theo CCCD và chuẩn bị sức khỏe thật tốt!</textarea><button class="button" data-action="remind">Ghi nhận nhắc lịch</button></div></section>
    <section class="section"><div class="section-head"><h2>Lịch sử thông báo của bạn</h2><span>${state.notifications.length} thông báo</span></div><div class="table-wrap"><table><thead><tr><th>TIÊU ĐỀ</th><th>NỘI DUNG</th><th>LOẠI</th><th>THỜI GIAN</th></tr></thead><tbody>${history || `<tr><td colspan="4" class="empty">Chưa có thông báo được ghi nhận.</td></tr>`}</tbody></table></div></section>`;
}

function render() {
  if (!app) {
    console.error("Không tìm thấy vùng giao diện #app.");
    return;
  }
  try {
    if (!state.token || !state.user) return loginView();
    if (!canManage() && !["campaigns", "appointments", "ai"].includes(state.page)) state.page = "campaigns";
    if (state.user.role === "admin" && ["donors", "appointments"].includes(state.page)) state.page = "campaigns";
    if (state.user.role !== "admin" && state.page === "accounts") state.page = "campaigns";
    const views = { dashboard: dashboardView, campaigns: campaignsView, accounts: adminUsersView, donors: donorsView, appointments: appointmentsView, ai: aiQaView, "ai-reports": aiReportsView, reminders: remindersView };
    app.innerHTML = shell((views[state.page] || dashboardView)());
    app.querySelectorAll("[data-page]").forEach((button) => button.addEventListener("click", () => { state.page = button.dataset.page; render(); }));
    bindActionControls(app);
    app.querySelectorAll("[data-report-type]").forEach((button) => button.addEventListener("click", () => {
      const showMonth = button.dataset.reportType === "month";
      app.querySelector("#monthly-report-panel")?.toggleAttribute("hidden", !showMonth);
      app.querySelector("#yearly-report-panel")?.toggleAttribute("hidden", showMonth);
      app.querySelectorAll("[data-report-type]").forEach((tab) => {
        const active = tab === button;
        tab.classList.toggle("active", active);
        tab.setAttribute("aria-selected", String(active));
      });
    }));
    app.querySelectorAll("[data-suggestion]").forEach((button) => button.addEventListener("click", () => {
      const question = app.querySelector("#procedure-question");
      if (question) { question.value = button.dataset.suggestion; question.focus(); }
    }));
    const procedureForm = app.querySelector("#procedure-form");
    procedureForm?.addEventListener("submit", (event) => {
      event.preventDefault();
      const question = app.querySelector("#procedure-question");
      const button = procedureForm.querySelector("button[type='submit']");
      if (question && button) askProcedure(question.value, button).catch((error) => toast(error.message));
    });
    const donorSearch = document.querySelector("#donor-search");
    if (donorSearch) donorSearch.addEventListener("input", (event) => { const pos = event.target.selectionStart; renderDonorSearch(event.target.value, pos); });
    const appointmentSearch = document.querySelector("#appointment-search");
    if (appointmentSearch) appointmentSearch.addEventListener("input", (event) => { const pos = event.target.selectionStart; renderAppointmentSearch(event.target.value, pos); });
    bindStatusControls();
    app.querySelectorAll("[data-user-role]").forEach((select) => select.addEventListener("change", async () => {
      try {
        await api(`/api/admin/users/${select.dataset.userRole}/role`, { method: "PUT", body: JSON.stringify({ role: select.value }) });
        await loadData(); render(); toast("Đã cập nhật vai trò tài khoản.");
      } catch (error) { toast(error.message); await loadData(); render(); }
    }));
    app.querySelectorAll("[data-campaign-status]").forEach((select) => select.addEventListener("change", async () => {
      try {
        await api(`/api/campaigns/${select.dataset.campaignStatus}/status`, { method: "PATCH", body: JSON.stringify({ status: select.value }) });
        await loadData(); render(); toast("Đã cập nhật trạng thái chiến dịch.");
      } catch (error) { toast(error.message); }
    }));
  } catch (error) {
    console.error("Không thể dựng giao diện.", error);
    app.innerHTML = `<main class="content"><h1>Không thể tải giao diện</h1><p>Vui lòng tải lại trang. Nếu lỗi tiếp tục, hãy kiểm tra kết nối máy chủ.</p></main>`;
  }
}

function bindActionControls(root) {
  if (!root) return;
  root.querySelectorAll("[data-action]").forEach((button) => button.addEventListener("click", () => {
    handleAction(button.dataset.action, button).catch((error) => toast(error.message || "Không thể hoàn tất thao tác."));
  }));
}

function bindStatusControls() {
  if (!app) return;
  app.querySelectorAll("[data-appointment]").forEach((select) => select.addEventListener("change", async () => {
    try { await api(`/api/appointments/${select.dataset.appointment}`, { method: "PATCH", body: JSON.stringify({ status: select.value }) }); await loadData(); toast("Đã cập nhật trạng thái tham gia."); }
    catch (error) { toast(error.message); }
  }));
}

function renderDonorSearch(query, pos) {
  const content = document.querySelector(".content");
  if (!content) return;
  content.innerHTML = donorsView(query);
  bindActionControls(content);
  const next = document.querySelector("#donor-search");
  if (!next) return;
  next.focus();
  next.setSelectionRange(pos, pos);
}
function renderAppointmentSearch(query, pos) {
  const content = document.querySelector(".content");
  if (!content) return;
  content.innerHTML = appointmentsView(query);
  const next = document.querySelector("#appointment-search");
  if (!next) return;
  next.focus();
  next.setSelectionRange(pos, pos);
  bindStatusControls();
}

function showModal(title, body, wide = false) {
  const dialog = document.querySelector("#modal");
  if (!dialog) {
    toast("Không tìm thấy vùng hiển thị biểu mẫu.");
    return false;
  }
  dialog.classList.toggle("wide", Boolean(wide));
  dialog.innerHTML = `<div class="dialog-head"><h2>${title}</h2><button class="icon-button" data-close aria-label="Đóng">×</button></div>${body}`;
  dialog.querySelectorAll("[data-close]").forEach((button) => button.addEventListener("click", () => dialog.close()));
  dialog.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); }, { once: true });
  dialog.showModal();
  return true;
}

function profileForm(profile, coordinator = false) {
  if (coordinator) {
    return `<form id="profile-form"><div class="form-grid"><div class="field"><label for="profile-name">HỌ VÀ TÊN</label><input id="profile-name" name="full_name" value="${esc(profile.full_name)}" required minlength="2" maxlength="100"></div><div class="field"><label for="profile-email">EMAIL ĐĂNG NHẬP</label><input id="profile-email" type="email" value="${esc(profile.email)}" readonly aria-readonly="true"></div><div class="field"><label for="profile-phone">SỐ ĐIỆN THOẠI</label><input id="profile-phone" name="phone" type="tel" value="${esc(profile.phone)}" maxlength="20"></div><div class="field"><label for="profile-organization">ĐƠN VỊ / CƠ SỞ CÔNG TÁC</label><input id="profile-organization" name="organization" value="${esc(profile.organization)}" maxlength="200" placeholder="Bệnh viện / Hội Chữ thập đỏ"></div><div class="field span-two"><label for="profile-job-title">CHỨC VỤ</label><input id="profile-job-title" name="job_title" value="${esc(profile.job_title)}" maxlength="100"></div></div><div class="dialog-actions"><button type="button" class="button secondary" data-close>Hủy</button><button type="submit" class="button">Lưu thay đổi</button></div></form>`;
  }
  const groups = ["Chưa cập nhật", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];
  return `<form id="profile-form"><div class="form-grid"><div class="field"><label for="profile-name">HỌ VÀ TÊN</label><input id="profile-name" name="full_name" value="${esc(profile.full_name)}" required minlength="2" maxlength="100"></div><div class="field"><label for="profile-email">EMAIL ĐĂNG NHẬP</label><input id="profile-email" type="email" value="${esc(profile.email)}" readonly aria-readonly="true"></div><div class="field"><label for="profile-phone">SỐ ĐIỆN THOẠI</label><input id="profile-phone" name="phone" type="tel" value="${esc(profile.phone)}" maxlength="20"></div><div class="field"><label for="profile-blood-group">NHÓM MÁU</label><select id="profile-blood-group" name="blood_group">${groups.map((group) => `<option value="${group}" ${profile.blood_group === group ? "selected" : ""}>${group}</option>`).join("")}</select></div><div class="field"><label for="profile-birth-date">NGÀY SINH</label><input id="profile-birth-date" name="birth_date" type="date" value="${esc(profile.birth_date || "")}"></div><div class="field span-two"><label for="profile-address">ĐỊA CHỈ</label><input id="profile-address" name="address" value="${esc(profile.address)}" maxlength="300"></div></div><div class="dialog-actions"><button type="button" class="button secondary" data-close>Hủy</button><button type="submit" class="button">Lưu thay đổi</button></div></form>`;
}

async function openProfileModal() {
  try {
    const coordinator = state.user.role === "coordinator";
    const endpoint = coordinator ? "/api/coordinators/me" : "/api/users/me";
    const profile = await api(endpoint);
    const title = coordinator ? "Chỉnh sửa hồ sơ Điều phối viên" : "Chỉnh sửa hồ sơ cá nhân";
    if (!showModal(title, profileForm({ ...profile, email: state.user.email }, coordinator))) return;
    const form = document.querySelector("#profile-form");
    form?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const data = Object.fromEntries(new FormData(form));
      if (!data.birth_date) delete data.birth_date;
      try {
        const updated = await api(endpoint, { method: "PUT", body: JSON.stringify(data) });
        state.user.display_name = updated.full_name;
        try { sessionStorage.setItem("md-user", JSON.stringify(state.user)); } catch (error) { console.warn("Không thể cập nhật phiên trong trình duyệt.", error); }
        document.querySelector("#modal")?.close();
        render();
        toast(coordinator ? "Đã cập nhật hồ sơ Điều phối viên." : "Đã cập nhật hồ sơ cá nhân.");
      } catch (error) { toast(error.message); }
    });
  } catch (error) { toast(error.message); }
}

function settingsForm() {
  return `<div class="settings-sections" role="group" aria-label="Cài đặt tài khoản">
    <section class="settings-section" aria-labelledby="settings-password-heading">
      <div class="settings-section-title"><span aria-hidden="true">🔑</span><div><h3 id="settings-password-heading">Đổi mật khẩu</h3><p>Mật khẩu mới cần có ít nhất 8 ký tự.</p></div></div>
      <form id="change-password-form">
        <div class="field"><label for="current-password">MẬT KHẨU HIỆN TẠI</label><input id="current-password" name="current_password" type="password" autocomplete="current-password" required maxlength="100"></div>
        <div class="field"><label for="new-password">MẬT KHẨU MỚI</label><input id="new-password" name="new_password" type="password" autocomplete="new-password" required minlength="8" maxlength="100"></div>
        <div class="field"><label for="confirm-password">XÁC NHẬN MẬT KHẨU MỚI</label><input id="confirm-password" name="confirm_password" type="password" autocomplete="new-password" required minlength="8" maxlength="100"></div>
        <div class="dialog-actions"><button type="submit" class="button">Cập nhật mật khẩu</button></div>
      </form>
    </section>
    <section class="settings-section settings-row" aria-labelledby="settings-theme-heading"><div class="settings-section-title"><span aria-hidden="true">🌙</span><div><h3 id="settings-theme-heading">Giao diện</h3><p>${state.theme === "dark" ? "Tối" : "Sáng"}</p></div></div><label class="theme-toggle"><input id="theme-setting" type="checkbox" role="switch" aria-label="Giao diện tối" ${state.theme === "dark" ? "checked" : ""}><span class="theme-toggle-track"><span></span></span></label></section>
  </div>`;
}

function openSettingsModal() {
  if (!showModal("Cài đặt tài khoản", settingsForm())) return;
  const form = document.querySelector("#change-password-form");
  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(form));
    if (data.new_password !== data.confirm_password) return toast("Mật khẩu mới và xác nhận không khớp.");
    const submit = form.querySelector("button[type='submit']");
    if (submit) submit.disabled = true;
    try {
      await api("/api/auth/change-password", { method: "POST", body: JSON.stringify(data) });
      form.reset();
      document.querySelector("#modal")?.close();
      toast("Đã cập nhật mật khẩu. Các phiên đăng nhập khác đã được đăng xuất.");
    } catch (error) { toast(error.message); }
    finally { if (submit) submit.disabled = false; }
  });
  document.querySelector("#theme-setting")?.addEventListener("change", (event) => {
    state.theme = event.target.checked ? "dark" : "light";
    savePreference("md-theme", state.theme);
    document.documentElement.dataset.theme = state.theme;
    const themeLabel = event.target.closest(".settings-row")?.querySelector(".settings-section-title p");
    if (themeLabel) themeLabel.textContent = state.theme === "dark" ? "Tối" : "Sáng";
  });
}

function donorForm() {
  return `<form id="donor-form"><div class="form-grid"><div class="field span-two"><label>HỌ VÀ TÊN</label><input name="full_name" required minlength="2"></div><div class="field"><label>SỐ ĐIỆN THOẠI</label><input name="phone" required minlength="8" inputmode="tel"></div><div class="field"><label>EMAIL</label><input name="email" type="email"></div><div class="field span-two"><label>NHÓM MÁU · DỮ LIỆU DEMO</label><select name="blood_group"><option>Chưa cập nhật</option><option>A+</option><option>A-</option><option>B+</option><option>B-</option><option>AB+</option><option>AB-</option><option>O+</option><option>O-</option></select></div><div class="field span-two"><label>EMAIL ĐĂNG NHẬP · KHÔNG BẮT BUỘC</label><input name="login_email" type="email" placeholder="email@vidu.com"></div><div class="field span-two"><label>MẬT KHẨU TẠM · KHÔNG BẮT BUỘC</label><input name="login_password" type="password" minlength="8" placeholder="Ít nhất 8 ký tự"></div></div><div class="dialog-actions"><button type="button" class="button secondary" data-close>Hủy</button><button class="button">Lưu hồ sơ</button></div></form>`;
}

function slotEditorRow(slot = {}) {
  const start = slot.start_time || (slot.start_at ? slot.start_at.slice(11) : "08:00");
  const end = slot.end_time || (slot.end_at ? slot.end_at.slice(11) : "09:00");
  const capacity = slot.capacity || 24;
  return `<div class="slot-editor-row" data-slot-row data-slot-id="${slot.id || ""}"><label>GIỜ BẮT ĐẦU<input class="slot-start" type="time" value="${esc(start)}" required></label><label>GIỜ KẾT THÚC<input class="slot-end" type="time" value="${esc(end)}" required></label><label>SỨC CHỨA<input class="slot-capacity" type="number" min="1" max="500" value="${capacity}" required></label><button class="icon-button slot-remove" type="button" aria-label="Xóa khung giờ" title="Xóa khung giờ">×</button></div>`;
}

function campaignForm(event = null) {
  const tomorrow = new Date(Date.now() + 86400000).toISOString().slice(0, 10);
  const slots = event && event.slots.length ? event.slots.map(slotEditorRow).join("") : slotEditorRow();
  return `<form id="campaign-form" data-campaign-id="${event ? event.id : ""}"><div class="form-grid"><div class="field span-two"><label>TÊN CHIẾN DỊCH</label><input name="title" value="${esc(event ? event.title : "")}" required minlength="3"></div><div class="field span-two"><label>ĐIỂM HIẾN</label><input name="venue" value="${esc(event ? event.venue : "")}" required></div><div class="field"><label>NGÀY TỔ CHỨC</label><input type="date" name="campaign_date" value="${event ? event.campaign_date : tomorrow}" required></div><div class="field"><label>TRẠNG THÁI</label><select name="status">${["Đang mở", "Tạm dừng", "Đã đóng"].map((status) => `<option ${event && (event.status === status || (event.status === "Đã kết thúc" && status === "Đã đóng")) ? "selected" : ""}>${status}</option>`).join("")}</select></div><div class="field span-two"><label>MÔ TẢ</label><textarea name="description">${esc(event ? event.description : "")}</textarea></div></div><div class="slot-editor-head"><strong>Khung giờ & sức chứa</strong><button type="button" class="button secondary small" id="add-slot">＋ Thêm khung giờ</button></div><div id="slot-editor">${slots}</div><div class="dialog-actions"><button type="button" class="button secondary" data-close>Hủy</button><button class="button">${event ? "Lưu thay đổi" : "Tạo chiến dịch"}</button></div></form>`;
}

function openCampaignEditor(event = null) {
  const title = event ? "Sửa chiến dịch" : "Tạo chiến dịch mới";
  if (!showModal(title, campaignForm(event))) return;
  const form = document.querySelector("#campaign-form");
  const slotEditor = document.querySelector("#slot-editor");
  const addSlot = document.querySelector("#add-slot");
  if (!form || !slotEditor || !addSlot) return toast("Không thể khởi tạo biểu mẫu chiến dịch.");
  addSlot.addEventListener("click", () => slotEditor.insertAdjacentHTML("beforeend", slotEditorRow()));
  slotEditor.addEventListener("click", (clickEvent) => {
    const remove = clickEvent.target.closest(".slot-remove");
    if (remove && slotEditor.querySelectorAll("[data-slot-row]").length > 1) remove.closest("[data-slot-row]").remove();
    else if (remove) toast("Chiến dịch cần có ít nhất một khung giờ.");
  });
  form.addEventListener("submit", async (submitEvent) => {
    submitEvent.preventDefault();
    const data = Object.fromEntries(new FormData(form));
    data.slots = Array.from(slotEditor.querySelectorAll("[data-slot-row]"), (row) => ({
      id: row.dataset.slotId ? Number(row.dataset.slotId) : null,
      start_time: row.querySelector(".slot-start").value,
      end_time: row.querySelector(".slot-end").value,
      capacity: Number(row.querySelector(".slot-capacity").value)
    }));
    try {
      const campaignId = form.dataset.campaignId;
      await api(campaignId ? `/api/campaigns/${campaignId}` : "/api/campaigns", { method: campaignId ? "PUT" : "POST", body: JSON.stringify(data) });
      await loadData(); render(); toast(campaignId ? "Đã cập nhật chiến dịch." : "Đã tạo chiến dịch.");
    } catch (error) { toast(error.message); }
  });
}

async function openCampaignDetails(campaignId) {
  try {
    const campaign = await api(`/api/campaigns/${campaignId}`);
    const totalCapacity = (campaign.slots || []).reduce((sum, s) => sum + Number(s.capacity || 0), 0);
    const totalBooked = (campaign.slots || []).reduce((sum, s) => sum + Number(s.booked || 0), 0);
    const attendedCount = (campaign.appointments || []).filter((a) => a.status === "Đã tham gia").length;
    const fillPercent = totalCapacity ? Math.min(100, Math.round(totalBooked / totalCapacity * 100)) : 0;
    
    const slotsHtml = (campaign.slots || []).map((slot, idx) => {
      const ratio = slot.capacity ? Math.min(100, Math.round((slot.booked / slot.capacity) * 100)) : 0;
      return `<div class="detail-slot-pill">
        <div class="slot-time-title"><strong>Khung ${idx + 1}:</strong> ${slot.start_at.slice(11)} – ${slot.end_at.slice(11)}</div>
        <div class="slot-meter-row">
          <div class="slot-meter"><span style="width:${ratio}%"></span></div>
          <span class="slot-meter-text">${slot.booked}/${slot.capacity}</span>
        </div>
      </div>`;
    }).join("");

    const participants = campaign.appointments || [];
    const participantRows = participants.map((item, idx) => `
      <tr>
        <td>${idx + 1}</td>
        <td>
          <div class="person-cell">
            <span class="person-dot">${initials(item.full_name)}</span>
            <div>
              <strong>${esc(item.full_name)}</strong>
              <div style="font-size:12px;color:var(--muted)">${esc(item.phone || "—")} · ${esc(item.email || "—")}</div>
            </div>
          </div>
        </td>
        <td><span class="pill" style="font-weight:700">${esc(item.blood_group || "Chưa rõ")}</span></td>
        <td>${item.start_at.slice(11)} – ${item.end_at.slice(11)}</td>
        <td>${statusPill(item.status)}</td>
      </tr>
    `).join("");

    const modalBody = `
      <div class="campaign-detail-dialog">
        <div class="campaign-detail-header">
          <div class="campaign-detail-badges">
            <span class="creator-badge">👤 Tạo bởi: <strong>${esc(campaign.created_by || "Điều phối viên (dieuphoi@machdo.com)")}</strong></span>
            ${statusPill(campaign.status)}
          </div>
          <h2 class="campaign-detail-title">${esc(campaign.title)}</h2>
          <p class="campaign-detail-desc">${esc(campaign.description || "Chưa có mô tả cho chiến dịch này.")}</p>
        </div>

        <div class="detail-info-grid">
          <div class="detail-info-card">
            <div class="info-label">📍 ĐỊA ĐIỂM TỔ CHỨC</div>
            <div class="info-val">${esc(campaign.venue)}</div>
          </div>
          <div class="detail-info-card">
            <div class="info-label">📅 NGÀY DIỄN RA</div>
            <div class="info-val">${prettyDate(campaign.campaign_date)}</div>
          </div>
          <div class="detail-info-card">
            <div class="info-label">⏰ THỜI GIAN</div>
            <div class="info-val">${campaign.start_time} – ${campaign.end_time}</div>
          </div>
          <div class="detail-info-card">
            <div class="info-label">📊 TIẾN ĐỘ ĐĂNG KÝ</div>
            <div class="info-val">${totalBooked}/${totalCapacity} (${fillPercent}%) · ${attendedCount} đã tham gia</div>
          </div>
        </div>

        <div class="detail-slots-section">
          <h3>Các khung giờ tiếp nhận (${(campaign.slots || []).length} khung)</h3>
          <div class="detail-slots-grid">${slotsHtml}</div>
        </div>

        <div class="detail-participants-section">
          <div class="section-head" style="margin-bottom:10px">
            <h3>Danh sách tình nguyện viên đã đăng ký (${participants.length})</h3>
          </div>
          <div class="table-wrap" style="max-height: 260px; overflow-y: auto;">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>TÌNH NGUYỆN VIÊN</th>
                  <th>NHÓM MÁU</th>
                  <th>KHUNG GIỜ</th>
                  <th>TRẠNG THÁI</th>
                </tr>
              </thead>
              <tbody>
                ${participantRows || `<tr><td colspan="5" class="empty">Chưa có người đăng ký vào chiến dịch này.</td></tr>`}
              </tbody>
            </table>
          </div>
        </div>

        <div class="dialog-actions" style="margin-top:20px;">
          ${canManage() ? `<button type="button" class="button secondary" data-action="detail-edit-campaign">✏️ Sửa chiến dịch</button>` : ""}
          <button type="button" class="button" data-close>Đóng</button>
        </div>
      </div>
    `;

    if (!showModal("Chi tiết chiến dịch", modalBody, true)) return;
    const dialog = document.querySelector("#modal");
    dialog?.querySelector("[data-action='detail-edit-campaign']")?.addEventListener("click", () => {
      dialog.close();
      openCampaignEditor(campaign);
    });
  } catch (error) {
    toast(error.message);
  }
}

async function openAccountDetails(userId) {
  try {
    const user = await api(`/api/admin/users/${userId}`);
    const isSelf = String(user.id) === String(state.user.id);
    const roleBadgeClass = `role-${esc(user.role)}`;
    const roleLabel = { volunteer: "Tình nguyện viên", coordinator: "Điều phối viên", admin: "Quản trị viên" }[user.role] || user.role;
    const statusLabel = user.status === "locked" ? "Đã khóa" : "Hoạt động";
    const appointments = user.appointments || [];
    
    const appointmentRows = appointments.map((app, idx) => `
      <tr>
        <td>${idx + 1}</td>
        <td>
          <strong>${esc(app.campaign_title)}</strong>
          <div style="font-size:12px;color:var(--muted)">📍 ${esc(app.venue)}</div>
        </td>
        <td>${prettyDate(app.campaign_date)}</td>
        <td>${app.start_at.slice(11)} – ${app.end_at.slice(11)}</td>
        <td>${statusPill(app.status)}</td>
      </tr>
    `).join("");

    const roleSpecificInfo = user.role === "volunteer" ? `
      <div class="detail-info-card">
        <div class="info-label">🩸 NHÓM MÁU</div>
        <div class="info-val"><span class="pill" style="font-weight:700">${esc(user.blood_group || "Chưa cập nhật")}</span></div>
      </div>
      <div class="detail-info-card">
        <div class="info-label">🎂 NGÀY SINH</div>
        <div class="info-val">${user.birth_date ? prettyDate(user.birth_date) : "Chưa cập nhật"}</div>
      </div>
      <div class="detail-info-card span-two">
        <div class="info-label">🏠 ĐỊA CHỈ</div>
        <div class="info-val">${esc(user.address || "Chưa cập nhật")}</div>
      </div>
    ` : `
      <div class="detail-info-card">
        <div class="info-label">🏢 ĐƠN VỊ CÔNG TÁC</div>
        <div class="info-val">${esc(user.organization || "Chưa cập nhật")}</div>
      </div>
      <div class="detail-info-card">
        <div class="info-label">💼 CHỨC VỤ</div>
        <div class="info-val">${esc(user.job_title || "Chưa cập nhật")}</div>
      </div>
      <div class="detail-info-card span-two">
        <div class="info-label">🏠 ĐỊA CHỈ</div>
        <div class="info-val">${esc(user.address || "Chưa cập nhật")}</div>
      </div>
    `;

    const volunteerHistorySection = user.role === "volunteer" ? `
      <div class="detail-participants-section" style="margin-top:16px;">
        <div class="section-head" style="margin-bottom:10px">
          <h3>Lịch sử đăng ký hiến máu (${appointments.length} lượt hẹn)</h3>
        </div>
        <div class="table-wrap" style="max-height: 220px; overflow-y: auto;">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>CHIẾN DỊCH</th>
                <th>NGÀY</th>
                <th>KHUNG GIỜ</th>
                <th>TRẠNG THÁI</th>
              </tr>
            </thead>
            <tbody>
              ${appointmentRows || `<tr><td colspan="5" class="empty">Chưa có lượt hẹn hiến máu nào.</td></tr>`}
            </tbody>
          </table>
        </div>
      </div>
    ` : "";

    const modalBody = `
      <div class="user-detail-dialog">
        <div class="user-detail-header">
          <div class="person-cell" style="gap:14px;">
            <span class="person-dot" style="width:50px;height:50px;font-size:18px;">${initials(user.full_name)}</span>
            <div>
              <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                <h2 style="margin:0;font-size:20px;">${esc(user.full_name)}</h2>
                <span class="role-badge ${roleBadgeClass}">${esc(roleLabel)}</span>
                <span class="account-status status-${esc(user.status)}"><i></i>${statusLabel}</span>
              </div>
              <div style="color:var(--muted);font-size:13px;margin-top:4px;">${esc(user.email)} · ID #${user.id}</div>
            </div>
          </div>
        </div>

        <div class="detail-info-grid" style="margin-top:16px;">
          <div class="detail-info-card">
            <div class="info-label">📞 SỐ ĐIỆN THOẠI</div>
            <div class="info-val">${esc(user.phone || "Chưa cập nhật")}</div>
          </div>
          <div class="detail-info-card">
            <div class="info-label">🕒 NGÀY TẠO TÀI KHOẢN</div>
            <div class="info-val">${accountTimestamp(user.created_at)}</div>
          </div>
          ${roleSpecificInfo}
        </div>

        ${volunteerHistorySection}

        <div class="dialog-actions" style="margin-top:20px;">
          ${!isSelf ? `
            <button class="button secondary" type="button" data-action="detail-toggle-status" data-status="${user.status === "locked" ? "active" : "locked"}">
              ${user.status === "locked" ? "Mở khóa tài khoản" : "Khóa tài khoản"}
            </button>
          ` : ""}
          <button type="button" class="button" data-close>Đóng</button>
        </div>
      </div>
    `;

    if (!showModal("Chi tiết tài khoản", modalBody, true)) return;
    const dialog = document.querySelector("#modal");
    dialog?.querySelector("[data-action='detail-toggle-status']")?.addEventListener("click", async (e) => {
      const targetStatus = e.currentTarget.dataset.status;
      try {
        await api(`/api/admin/users/${user.id}/status`, { method: "PUT", body: JSON.stringify({ status: targetStatus }) });
        dialog.close();
        await loadData();
        render();
        toast(targetStatus === "locked" ? "Tài khoản đã được khóa." : "Tài khoản đã được mở khóa.");
      } catch (err) {
        toast(err.message);
      }
    });
  } catch (error) {
    toast(error.message);
  }
}

async function handleAction(action, button) {
  if (action === "logout") { try { await api("/api/auth/logout", { method: "POST" }); } catch {} state.token = null; state.user = null; state.avatarMenuOpen = false; state.notificationsOpen = false; clearSession(); render(); return; }
  if (action === "toggle-avatar-menu") { state.avatarMenuOpen = !state.avatarMenuOpen; state.notificationsOpen = false; render(); return; }
  if (action === "profile") { state.avatarMenuOpen = false; render(); await openProfileModal(); return; }
  if (action === "settings") { state.avatarMenuOpen = false; render(); openSettingsModal(); return; }
  if (action === "toggle-notifications") {
    state.notificationsOpen = !state.notificationsOpen;
    render();
    if (state.notificationsOpen) { state.notifications = await api("/api/notifications"); render(); }
    return;
  }
  if (action === "read-notification") {
    await api(`/api/notifications/${button.dataset.notificationId}/read`, { method: "PUT" });
    state.notifications = await api("/api/notifications");
    render();
    return;
  }
  if (action === "mark-all-read") {
    await api("/api/notifications/read-all", { method: "PUT" });
    state.notifications = await api("/api/notifications");
    render();
    return;
  }
  if (action === "view-campaign") {
    await openCampaignDetails(Number(button.dataset.campaign));
    return;
  }
  if (action === "account-detail") {
    await openAccountDetails(Number(button.dataset.userId));
    return;
  }
  if (action === "new-donor") {
    if (!showModal("Thêm hồ sơ người đăng ký", donorForm())) return;
    const form = document.querySelector("#donor-form");
    if (!form) return toast("Không thể khởi tạo biểu mẫu hồ sơ.");
    form.addEventListener("submit", async (event) => { event.preventDefault(); const data = Object.fromEntries(new FormData(event.currentTarget)); if (!data.login_email) delete data.login_email; if (!data.login_password) delete data.login_password; try { const result = await api("/api/donors", { method: "POST", body: JSON.stringify(data) }); await loadData(); render(); toast(result.account_created ? "Đã tạo hồ sơ và tài khoản tình nguyện viên." : "Đã thêm hồ sơ người đăng ký."); } catch (error) { toast(error.message); } });
  }
  if (action === "new-account") {
    const formBody = `<form id="admin-create-user-form" class="account-create-form">
      <div class="field">
        <label for="account-role">Phân quyền vai trò</label>
        <select id="account-role" name="role" required>
          <option value="volunteer">🟢 Tình nguyện viên</option>
          <option value="coordinator">🔵 Điều phối viên</option>
          <option value="admin">🟣 Quản trị viên</option>
        </select>
      </div>
      <div class="form-grid">
        <div class="field">
          <label for="account-full-name">Họ và tên</label>
          <input id="account-full-name" name="full_name" type="text" required minlength="2" maxlength="100" autocomplete="name" placeholder="Ví dụ: Nguyễn Văn A">
        </div>
        <div class="field">
          <label for="account-email">Email đăng nhập</label>
          <input id="account-email" name="email" type="email" required maxlength="254" autocomplete="email" placeholder="user@machdo.com">
        </div>
        <div class="field">
          <label for="account-password">Mật khẩu khởi tạo</label>
          <input id="account-password" name="password" type="password" required minlength="8" maxlength="100" autocomplete="new-password" placeholder="Tối thiểu 8 ký tự">
        </div>
        <div class="field">
          <label for="account-phone">Số điện thoại</label>
          <input id="account-phone" name="phone" type="tel" maxlength="20" placeholder="0901234567">
        </div>
        <div class="field span-two" id="account-blood-field">
          <label for="account-blood-group">Nhóm máu</label>
          <select id="account-blood-group" name="blood_group">
            <option value="Chưa cập nhật">Chưa cập nhật</option>
            <option value="A+">A+</option>
            <option value="A-">A-</option>
            <option value="B+">B+</option>
            <option value="B-">B-</option>
            <option value="AB+">AB+</option>
            <option value="AB-">AB-</option>
            <option value="O+">O+</option>
            <option value="O-">O-</option>
          </select>
        </div>
        <div class="field" id="account-org-field" style="display:none;">
          <label for="account-organization">Đơn vị / Cơ sở công tác</label>
          <input id="account-organization" name="organization" maxlength="200" placeholder="Bệnh viện / Hội Chữ thập đỏ">
        </div>
        <div class="field" id="account-job-field" style="display:none;">
          <label for="account-job-title">Chức vụ</label>
          <input id="account-job-title" name="job_title" maxlength="100" placeholder="Điều phối viên / Trưởng ban">
        </div>
      </div>
      <div class="dialog-actions">
        <button type="button" class="button secondary" data-close>Hủy</button>
        <button type="submit" class="button">Tạo tài khoản</button>
      </div>
    </form>`;
    if (!showModal("Thêm tài khoản mới", formBody)) return;
    const form = document.querySelector("#admin-create-user-form");
    const roleSelect = form?.querySelector("#account-role");
    const bloodField = form?.querySelector("#account-blood-field");
    const orgField = form?.querySelector("#account-org-field");
    const jobField = form?.querySelector("#account-job-field");
    const syncRoleFields = () => {
      const role = roleSelect?.value;
      if (role === "volunteer") {
        if (bloodField) bloodField.style.display = "block";
        if (orgField) orgField.style.display = "none";
        if (jobField) jobField.style.display = "none";
      } else {
        if (bloodField) bloodField.style.display = "none";
        if (orgField) orgField.style.display = "block";
        if (jobField) jobField.style.display = "block";
      }
    };
    roleSelect?.addEventListener("change", syncRoleFields);
    syncRoleFields();

    form?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const submit = form.querySelector("button[type='submit']");
      if (submit) submit.disabled = true;
      try {
        const payload = Object.fromEntries(new FormData(form));
        await api("/api/admin/users", { method: "POST", body: JSON.stringify(payload) });
        document.querySelector("#modal")?.close();
        await loadData(); render(); toast(`Đã tạo tài khoản ${roleName(payload.role)} mới thành công.`);
      } catch (error) { toast(error.message); if (submit) submit.disabled = false; }
    });
    return;
  }
  if (action === "new-campaign") openCampaignEditor();
  if (action === "edit-campaign") openCampaignEditor(state.campaigns.find((event) => event.id === Number(button.dataset.campaign)));
  if (action === "delete-campaign") {
    const campaign = state.campaigns.find((event) => event.id === Number(button.dataset.campaign));
    if (!campaign || !window.confirm(`Xóa chiến dịch “${campaign.title}”? Thao tác này không thể hoàn tác.`)) return;
    try { await api(`/api/campaigns/${campaign.id}`, { method: "DELETE" }); await loadData(); render(); toast("Đã xóa chiến dịch."); }
    catch (error) { toast(error.message); }
  }
  if (action === "monthly-report") {
    const month = Number(document.querySelector("#report-month")?.value);
    const year = Number(document.querySelector("#report-month-year")?.value);
    const result = document.querySelector("#monthly-report-result");
    if (!result) return;
    result.textContent = "Đang tổng hợp số liệu và tạo báo cáo…";
    try {
      const report = await api("/api/ai/monthly-report", { method: "POST", body: JSON.stringify({ month, year }) });
      result.innerHTML = `<div class="report-metrics"><article><span>Chiến dịch trong tháng</span><strong>${report.summary.campaign_count}</strong></article><article><span>Lượt tình nguyện viên đăng ký</span><strong>${report.summary.registrations}</strong></article><article><span>Hoàn thành chỉ tiêu</span><strong>${report.summary.completion_rate}%</strong></article></div><p class="report-copy">${esc(report.report)}</p><small>Nguồn: ${esc(report.mode)}</small>`;
    } catch (error) { result.textContent = error.message; }
  }
  if (action === "yearly-report") {
    const year = Number(document.querySelector("#report-year")?.value);
    const result = document.querySelector("#yearly-report-result");
    if (!result) return;
    result.textContent = "Đang tổng hợp số liệu cả năm…";
    try {
      const report = await api("/api/ai/yearly-report", { method: "POST", body: JSON.stringify({ year }) });
      const monthRows = report.monthly.map((item) => `<tr><td>Tháng ${item.month}</td><td>${item.campaign_count}</td><td>${item.registrations}</td><td>${item.completion_rate}%</td></tr>`).join("");
      result.innerHTML = `<div class="report-metrics"><article><span>Chiến dịch trong năm</span><strong>${report.summary.campaign_count}</strong></article><article><span>Tổng lượt đăng ký</span><strong>${report.summary.registrations}</strong></article><article><span>Tỷ lệ hoàn thành trung bình</span><strong>${report.summary.average_completion_rate}%</strong></article></div><p class="report-copy">${esc(report.report)}</p><div class="table-wrap"><table><thead><tr><th>Kỳ</th><th>Chiến dịch</th><th>Lượt đăng ký</th><th>Hoàn thành chỉ tiêu</th></tr></thead><tbody>${monthRows}</tbody></table></div><small>Nguồn: ${esc(report.mode)}</small>`;
    } catch (error) { result.textContent = error.message; }
  }
  if (action === "campaign-summary") {
    const campaignId = Number(button.dataset.campaignId);
    const result = document.querySelector(`#campaign-summary-${campaignId}`);
    if (!result) return;
    result.textContent = "Đang tổng hợp số liệu chiến dịch…";
    try {
      const response = await api("/api/ai/campaign-summary", { method: "POST", body: JSON.stringify({ campaign_id: campaignId }) });
      result.textContent = `${response.summary} Nguồn: ${response.mode}.`;
    } catch (error) { result.textContent = error.message; }
  }
  if (action === "account-status") {
    const userId = Number(button.dataset.userId);
    try {
      await api(`/api/admin/users/${userId}/status`, { method: "PUT", body: JSON.stringify({ status: button.dataset.status }) });
      await loadData(); render(); toast(button.dataset.status === "locked" ? "Tài khoản đã được khóa." : "Tài khoản đã được mở khóa.");
    } catch (error) { toast(error.message); }
  }
  if (action === "account-delete") {
    const userId = Number(button.dataset.userId);
    const userName = button.dataset.userName || "tài khoản này";
    if (!window.confirm(`Xóa ${userName}? Thao tác này không thể hoàn tác.`)) return;
    try {
      await api(`/api/admin/users/${userId}`, { method: "DELETE" });
      await loadData(); render(); toast("Đã xóa tài khoản.");
    } catch (error) { toast(error.message); }
  }
  if (action === "book") openBooking(Number(button.dataset.slot));
  if (action === "remind") {
    const field = document.querySelector("#reminder-campaign");
    if (!field) return toast("Vui lòng chọn chiến dịch.");
    const campaignId = Number(field.value);
    const message = document.querySelector("#reminder-message")?.value || "";
    try { const result = await api("/api/reminders", { method: "POST", body: JSON.stringify({ campaign_id: campaignId, message }) }); await loadData(); render(); toast(`${result.sent} nhắc lịch đã được ghi nhận. ${result.channel}`); }
    catch (error) { toast(error.message); }
  }
}

async function openBooking(slotId) {
  const slot = state.campaigns.flatMap((event) => event.slots.map((item) => ({ ...item, event }))).find((item) => item.id === slotId);
  if (!slot) return;
  if (!showModal("Đăng ký khung giờ", `<form id="booking-form"><p style="font-size:12px;line-height:1.7;color:#687970">${esc(slot.event.title)}<br>${esc(slot.event.venue)} · ${prettyDate(slot.event.campaign_date)} · ${slot.start_at.slice(11)}–${slot.end_at.slice(11)}</p><div class="field"><label>NGƯỜI ĐĂNG KÝ</label><select name="donor_id" required>${state.donors.map((person) => `<option value="${person.id}">${esc(person.full_name)} · ${esc(person.phone)}</option>`).join("")}</select></div><div class="dialog-actions"><button type="button" class="button secondary" data-close>Hủy</button><button class="button">Xác nhận giữ chỗ</button></div></form>`)) return;
  const form = document.querySelector("#booking-form");
  if (!form) return toast("Không thể khởi tạo biểu mẫu đăng ký.");
  form.addEventListener("submit", async (event) => { event.preventDefault(); const donorId = Number(new FormData(event.currentTarget).get("donor_id")); try { await api("/api/appointments", { method: "POST", body: JSON.stringify({ donor_id: donorId, slot_id: slotId }) }); const dialog = document.querySelector("#modal"); if (dialog) dialog.close(); await loadData(); render(); toast("Đăng ký khung giờ thành công."); } catch (error) { toast(error.message); } });
}

async function askProcedure(question, button) {
  const result = document.querySelector("#answer-result");
  const source = document.querySelector("#answer-source");
  const answerCard = document.querySelector(".answer-card");
  if (!result || !source || !answerCard) return;
  const normalizedQuestion = question.trim();
  if (!normalizedQuestion) return document.querySelector("#procedure-question")?.focus();
  button.disabled = true;
  answerCard.setAttribute("aria-busy", "true");
  source.textContent = "Đang tra cứu tài liệu…";
  result.replaceChildren();
  const loading = document.createElement("p");
  loading.className = "answer-placeholder";
  loading.textContent = "Đang tìm hướng dẫn phù hợp.";
  result.append(loading);
  try {
    const response = await api("/api/chat", { method: "POST", body: JSON.stringify({ question: normalizedQuestion }) });
    source.textContent = `Nguồn trả lời · ${response.mode}`;
    result.replaceChildren();
    const paragraphs = String(response.text || "").split(/\n\s*\n/).map((paragraph) => paragraph.trim()).filter(Boolean);
    for (const text of paragraphs) {
      const paragraph = document.createElement("p");
      paragraph.textContent = text;
      result.append(paragraph);
    }
  } catch (error) {
    source.textContent = "Không thể tra cứu lúc này";
    result.replaceChildren();
    const paragraph = document.createElement("p");
    paragraph.className = "answer-error";
    paragraph.textContent = error.message;
    result.append(paragraph);
  } finally {
    answerCard.setAttribute("aria-busy", "false");
    button.disabled = false;
  }
}

async function start() {
  try {
    app?.addEventListener("click", (event) => {
      const outsideNotifications = state.notificationsOpen && !event.target.closest(".notification-wrap");
      const outsideAvatar = state.avatarMenuOpen && !event.target.closest(".avatar-menu-wrap");
      if (outsideNotifications || outsideAvatar) {
        state.notificationsOpen = outsideNotifications ? false : state.notificationsOpen;
        state.avatarMenuOpen = outsideAvatar ? false : state.avatarMenuOpen;
        render();
      }
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && (state.notificationsOpen || state.avatarMenuOpen)) { state.notificationsOpen = false; state.avatarMenuOpen = false; render(); }
    });
    if (state.token && state.user) await loadData();
    render();
    if (!state.token || !state.user) {
      document.querySelector("#login-view")?.classList.add("active");
      document.querySelector("#register-view")?.classList.remove("active");
    }
  } catch (error) {
    console.error("Không thể khởi tạo ứng dụng.", error);
    if (app) app.innerHTML = `<main class="content"><h1>Không thể khởi tạo ứng dụng</h1><p>Vui lòng tải lại trang. Nếu lỗi tiếp tục, hãy kiểm tra kết nối máy chủ.</p></main>`;
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", start, { once: true });
} else {
  start();
}
