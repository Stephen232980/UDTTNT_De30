from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

import main


def test_register_account_and_reject_duplicate_email(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "register.db")
    main.initialize_database()
    client = TestClient(main.app)
    payload = {"email": "new-donor@example.com", "password": "SecurePass123", "full_name": "Người hiến mới", "role": "donor"}

    created = client.post("/api/register", json=payload)
    assert created.status_code == 201
    assert created.json()["message"] == "Đăng ký tài khoản thành công"
    assert created.json()["role"] == "volunteer"
    with main.connect() as db:
        donor = db.execute("SELECT * FROM donors WHERE id=?", (db.execute("SELECT donor_id FROM users WHERE id=?", (created.json()["user_id"],)).fetchone()[0],)).fetchone()
        assert donor["email"] == payload["email"]
        assert donor["full_name"] == payload["full_name"]
    duplicate = client.post("/api/register", json=payload)
    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "Email đã tồn tại"

    login = client.post("/api/login", json={"email": payload["email"], "password": payload["password"]})
    assert login.status_code == 200
    assert login.json()["user"]["display_name"] == payload["full_name"]
    assert login.json()["user"]["role"] == "volunteer"


def test_register_rejects_reserved_system_emails(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "reserved.db")
    main.initialize_database()
    client = TestClient(main.app)
    for email in main.SYSTEM_ACCOUNTS:
        response = client.post("/api/register", json={"email": email, "password": "SecurePass123", "full_name": "Tài khoản mới"})
        assert response.status_code == 400
        assert response.json()["detail"] == "Email hệ thống không thể đăng ký"


def test_seeded_system_accounts_can_login_with_expected_roles(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "system-accounts.db")
    main.initialize_database()
    main.initialize_database()
    client = TestClient(main.app)

    for email, (_, expected_role) in main.SYSTEM_ACCOUNTS.items():
        response = client.post("/api/auth/login", json={"email": email, "password": main.DEMO_PASSWORD})
        assert response.status_code == 200
        assert response.json()["user"]["role"] == expected_role
        with main.connect() as db:
            rows = db.execute("SELECT password FROM users WHERE username=?", (email,)).fetchall()
            assert len(rows) == 1
            assert len(rows[0]["password"].split(":", 1)) == 2

    for alias, expected_role in [("admin", "admin"), ("dieuphoi", "coordinator"), ("tinhnguyen", "volunteer"), ("admin@machdo.vn", "admin"), ("tinhnguyen@machdo.vn", "volunteer")]:
        response = client.post("/api/auth/login", json={"email": alias, "password": main.DEMO_PASSWORD})
        assert response.status_code == 200
        assert response.json()["user"]["role"] == expected_role


def test_donor_can_update_own_profile_but_not_login_email(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "profile.db")
    main.initialize_database()
    client = TestClient(main.app)
    login = client.post("/api/auth/login", json={"email": "tinhnguyen@machdo.com", "password": main.DEMO_PASSWORD}).json()
    headers = {"Authorization": f"Bearer {login['token']}"}

    blank_name = client.put("/api/donors/me", headers=headers, json={"full_name": "  "})
    assert blank_name.status_code == 422
    updated = client.put("/api/donors/me", headers=headers, json={
        "full_name": "Nguyễn Tình Nguyện",
        "email": "forged@example.com",
        "phone": "0901234567",
        "blood_group": "O+",
        "birth_date": "1995-04-12",
        "address": "Thành phố Thái Nguyên",
    })
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Nguyễn Tình Nguyện"
    assert updated.json()["email"] == "minhanh@example.vn"
    assert updated.json()["phone"] == "0901234567"
    assert updated.json()["blood_group"] == "O+"
    assert updated.json()["birth_date"] == "1995-04-12"
    assert updated.json()["address"] == "Thành phố Thái Nguyên"
    assert client.get("/api/donors/me", headers=headers).json()["full_name"] == "Nguyễn Tình Nguyện"

    refreshed_login = client.post("/api/auth/login", json={"email": "tinhnguyen@machdo.com", "password": main.DEMO_PASSWORD})
    assert refreshed_login.json()["user"]["display_name"] == "Nguyễn Tình Nguyện"
    assert client.put("/api/donors/me", json=updated.json()).status_code == 401


def test_system_user_can_update_own_profile_without_donor(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "system-profile.db")
    main.initialize_database()
    client = TestClient(main.app)
    login = client.post("/api/auth/login", json={"email": "admin@machdo.com", "password": main.DEMO_PASSWORD}).json()
    headers = {"Authorization": f"Bearer {login['token']}"}

    profile = client.get("/api/users/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["email"] == "admin@machdo.com"
    assert profile.json()["full_name"] == "Quản trị viên"
    updated = client.put("/api/users/me", headers=headers, json={
        "full_name": "Quản trị viên thử nghiệm",
        "phone": "0907654321",
        "blood_group": "A+",
        "birth_date": "1988-11-02",
        "address": "Thái Nguyên",
    })
    assert updated.status_code == 200
    assert updated.json()["email"] == "admin@machdo.com"
    assert updated.json()["full_name"] == "Quản trị viên thử nghiệm"
    assert updated.json()["birth_date"] == "1988-11-02"
    assert client.post("/api/auth/login", json={"email": "admin@machdo.com", "password": main.DEMO_PASSWORD}).json()["user"]["display_name"] == "Quản trị viên thử nghiệm"


def test_coordinator_can_update_profile_and_change_password(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "coordinator-profile.db")
    main.SESSIONS.clear()
    main.initialize_database()
    client = TestClient(main.app)
    login = client.post("/api/auth/login", json={"email": "dieuphoi@machdo.com", "password": main.DEMO_PASSWORD}).json()
    headers = {"Authorization": f"Bearer {login['token']}"}

    initial = client.get("/api/coordinators/me", headers=headers)
    assert initial.status_code == 200
    assert initial.json()["email"] == "dieuphoi@machdo.com"
    assert client.get("/api/coordinators/me").status_code == 401
    volunteer = client.post("/api/auth/login", json={"email": "tinhnguyen@machdo.com", "password": main.DEMO_PASSWORD}).json()
    assert client.get("/api/coordinators/me", headers={"Authorization": f"Bearer {volunteer['token']}"}).status_code == 403

    updated = client.put("/api/coordinators/me", headers=headers, json={
        "full_name": "Điều phối viên ICTU",
        "email": "changed@example.vn",
        "phone": "0912345678",
        "organization": "Bệnh viện Trung ương",
        "job_title": "Điều phối trưởng",
    })
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Điều phối viên ICTU"
    assert updated.json()["email"] == "dieuphoi@machdo.com"
    assert updated.json()["organization"] == "Bệnh viện Trung ương"
    assert updated.json()["job_title"] == "Điều phối trưởng"
    assert client.get("/api/users/me", headers=headers).json()["job_title"] == "Điều phối trưởng"

    change = {"current_password": main.DEMO_PASSWORD, "new_password": "CoordinatorPass456", "confirm_password": "CoordinatorPass456"}
    assert client.post("/api/auth/change-password", headers=headers, json=change).status_code == 200
    assert client.post("/api/auth/login", json={"email": "dieuphoi@machdo.com", "password": main.DEMO_PASSWORD}).status_code == 401
    assert client.post("/api/auth/login", json={"email": "dieuphoi@machdo.com", "password": "CoordinatorPass456"}).status_code == 200


def test_change_password_validates_and_stores_pbkdf2_hash(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "change-password.db")
    main.SESSIONS.clear()
    main.initialize_database()
    client = TestClient(main.app)
    login = client.post("/api/auth/login", json={"email": "tinhnguyen@machdo.com", "password": main.DEMO_PASSWORD}).json()
    other_session = client.post("/api/auth/login", json={"email": "tinhnguyen@machdo.com", "password": main.DEMO_PASSWORD}).json()
    headers = {"Authorization": f"Bearer {login['token']}"}
    other_headers = {"Authorization": f"Bearer {other_session['token']}"}
    payload = {"current_password": main.DEMO_PASSWORD, "new_password": "NewSecurePass456", "confirm_password": "NewSecurePass456"}

    assert client.post("/api/auth/change-password", json=payload).status_code == 401
    wrong = {**payload, "current_password": "WrongPassword"}
    assert client.post("/api/auth/change-password", headers=headers, json=wrong).status_code == 400
    mismatch = {**payload, "confirm_password": "OtherSecurePass456"}
    assert client.post("/api/auth/change-password", headers=headers, json=mismatch).status_code == 422

    changed = client.post("/api/auth/change-password", headers=headers, json=payload)
    assert changed.status_code == 200
    assert changed.json() == {"ok": True}
    assert client.get("/api/donors/me", headers=headers).status_code == 200
    assert client.get("/api/donors/me", headers=other_headers).status_code == 401
    assert client.post("/api/auth/login", json={"email": "tinhnguyen@machdo.com", "password": main.DEMO_PASSWORD}).status_code == 401
    new_login = client.post("/api/auth/login", json={"email": "tinhnguyen@machdo.com", "password": "NewSecurePass456"})
    assert new_login.status_code == 200
    with main.connect() as db:
        encoded = db.execute("SELECT password FROM users WHERE username='tinhnguyen@machdo.com'").fetchone()["password"]
    assert encoded != "NewSecurePass456"
    assert main.verify_password("NewSecurePass456", encoded)


def test_initialize_migrates_legacy_donor_profile_fields(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "legacy-donor.db")
    with main.connect() as db:
        db.execute("CREATE TABLE donors(id INTEGER PRIMARY KEY,full_name TEXT NOT NULL,phone TEXT NOT NULL,email TEXT DEFAULT '',blood_group TEXT DEFAULT 'Chưa cập nhật')")
        db.execute("INSERT INTO donors(id,full_name,phone,email) VALUES (1,'Donor cũ','0900000000','old@example.vn')")

    main.initialize_database()
    with main.connect() as db:
        columns = {row[1] for row in db.execute("PRAGMA table_info(donors)")}
        donor = db.execute("SELECT * FROM donors WHERE id=1").fetchone()
        assert {"birth_date", "address", "created_at"} <= columns
        assert donor["full_name"] == "Donor cũ"
        assert donor["birth_date"] is None
        assert donor["address"] == ""


def test_slot_capacity_is_enforced_concurrently(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "test.db")
    main.SESSIONS.clear()
    main.initialize_database()
    with main.connect() as db:
        cid = db.execute("INSERT INTO campaigns(title,venue,campaign_date,start_time,end_time) VALUES ('Test','Hall','2026-10-01','08:00','09:00')").lastrowid
        slot = db.execute("INSERT INTO slots(campaign_id,start_at,end_at,capacity) VALUES (?,'2026-10-01T08:00','2026-10-01T09:00',1)",(cid,)).lastrowid
        donors = [db.execute("INSERT INTO donors(full_name,phone) VALUES (?,?)",(f"Donor {i}",f"090000000{i}")).lastrowid for i in range(2)]
    token = TestClient(main.app).post("/api/auth/login",json={"email":"admin@machdo.com","password":main.DEMO_PASSWORD}).json()["token"]
    headers = {"Authorization":f"Bearer {token}"}

    def book(donor):
        with TestClient(main.app) as client:
            return client.post("/api/appointments",json={"donor_id":donor,"slot_id":slot},headers=headers).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(book,donors))
    assert sorted(results) == [201,409]
    with main.connect() as db:
        assert db.execute("SELECT COUNT(*) FROM appointments WHERE slot_id=?",(slot,)).fetchone()[0] == 1


def test_ai_fallback_refuses_personal_health_advice(tmp_path, monkeypatch):
    monkeypatch.setattr(main,"DB_PATH",tmp_path/"health.db")
    monkeypatch.setenv("OPENAI_API_KEY","test-key")
    monkeypatch.setattr(main,"ai_call",lambda *_: (_ for _ in ()).throw(AssertionError("personal health question sent to AI")))
    main.initialize_database()
    client=TestClient(main.app)
    token=client.post("/api/auth/login",json={"email":"tinhnguyen@machdo.com","password":main.DEMO_PASSWORD}).json()["token"]
    response=client.post("/api/chat",json={"question":"Tôi đang uống thuốc, có đủ điều kiện hiến máu không?"},headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200
    assert "không thể đánh giá sức khỏe" in response.json()["text"]


def test_chat_requires_authentication(tmp_path, monkeypatch):
    monkeypatch.setattr(main,"DB_PATH",tmp_path/"chat-auth.db")
    main.initialize_database()
    response=TestClient(main.app).post("/api/chat",json={"question":"Sau khi hiến máu cần làm gì?"})
    assert response.status_code == 401


def test_reminder_is_recorded_once_without_external_delivery(tmp_path, monkeypatch):
    monkeypatch.setattr(main,"DB_PATH",tmp_path/"reminders.db")
    monkeypatch.setenv("OPENAI_API_KEY","test-key")
    prompts=[]
    monkeypatch.setattr(main,"ai_call",lambda system,prompt: prompts.append(prompt) or "Hẹn gặp bạn tại ngày hội hiến máu!")
    main.initialize_database()
    client=TestClient(main.app)
    token=client.post("/api/auth/login",json={"email":"dieuphoi@machdo.com","password":main.DEMO_PASSWORD}).json()["token"]
    volunteer_token=client.post("/api/auth/login",json={"email":"tinhnguyen@machdo.com","password":main.DEMO_PASSWORD}).json()["token"]
    headers={"Authorization":f"Bearer {token}"}
    with main.connect() as db:
        donor=db.execute("SELECT id FROM donors LIMIT 1").fetchone()[0]
        campaign=db.execute("SELECT id FROM campaigns LIMIT 1").fetchone()[0]
        slot=db.execute("SELECT id FROM slots WHERE campaign_id=? LIMIT 1",(campaign,)).fetchone()[0]
        db.execute("UPDATE slots SET start_at=datetime('now','+36 hours'),end_at=datetime('now','+37 hours') WHERE id=?",(slot,))
    assert client.post("/api/appointments",json={"donor_id":donor,"slot_id":slot},headers=headers).status_code == 201
    first=client.post(f"/api/notifications/send?campaign_id={campaign}",headers=headers).json()
    second=client.post(f"/api/notifications/send?campaign_id={campaign}",headers=headers).json()
    assert first["sent"] == 1
    assert second["sent"] == 0
    assert first["mode"] == "AI"
    assert len(prompts) == 1
    assert "090" not in prompts[0]
    assert "Nguyễn Minh Anh" not in prompts[0]
    assert "chưa gửi SMS/email" in first["channel"]
    inbox=client.get("/api/notifications",headers={"Authorization":f"Bearer {volunteer_token}"}).json()
    reminders=[n for n in inbox if n.get("type") == "reminder"]
    assert len(reminders) == 1


def test_notifications_generate_upcoming_reminders_once_and_enforce_user_scope(tmp_path, monkeypatch):
    monkeypatch.setattr(main,"DB_PATH",tmp_path/"notifications.db")
    main.SESSIONS.clear()
    main.initialize_database()
    client=TestClient(main.app)
    owner_login=client.post("/api/auth/login",json={"email":"tinhnguyen@machdo.com","password":main.DEMO_PASSWORD}).json()
    owner_headers={"Authorization":f"Bearer {owner_login['token']}"}
    with main.connect() as db:
        donor_id=int(owner_login["user"]["donor_id"])
        campaign_id=db.execute("INSERT INTO campaigns(title,venue,campaign_date,start_time,end_time) VALUES ('Ngày hội sắp tới','Nhà văn hóa trung tâm',date('now','+2 days'),'08:00','12:00')").lastrowid
        for offset in (36,40):
            slot_id=db.execute("INSERT INTO slots(campaign_id,start_at,end_at,capacity) VALUES (?,datetime('now',?),datetime('now',?),10)",(campaign_id,f"+{offset} hours",f"+{offset + 1} hours")).lastrowid
            db.execute("INSERT INTO appointments(donor_id,slot_id,status) VALUES (?,?,'Đã đăng ký')",(donor_id,slot_id))

    first=client.get("/api/notifications",headers=owner_headers)
    assert first.status_code == 200
    assert len(first.json()) == 2
    reminder=first.json()[0]
    assert {"id","user_id","title","message","type","is_read","created_at"} <= reminder.keys()
    assert reminder["title"] == "Lịch hiến máu sắp tới"
    assert reminder["type"] == "reminder"
    assert reminder["is_read"] == 0
    assert "Nhà văn hóa trung tâm" in reminder["message"]
    assert "Khung giờ" in reminder["message"]
    assert len(client.get("/api/notifications",headers=owner_headers).json()) == 2

    other=client.post("/api/register",json={"email":"other-volunteer@example.com","password":"SecurePass123","full_name":"Người khác"}).json()
    other_login=client.post("/api/auth/login",json={"email":"other-volunteer@example.com","password":"SecurePass123"}).json()
    other_headers={"Authorization":f"Bearer {other_login['token']}"}
    assert other["role"] == "volunteer"
    assert client.get("/api/notifications",headers=other_headers).json() == []
    assert client.put(f"/api/notifications/{reminder['id']}/read",headers=other_headers).status_code == 404
    assert client.put(f"/api/notifications/{reminder['id']}/read",headers=owner_headers).status_code == 200
    marked=client.put("/api/notifications/read-all",headers=owner_headers)
    assert marked.json() == {"updated":1}
    assert all(item["is_read"] == 1 for item in client.get("/api/notifications",headers=owner_headers).json())


def test_initialize_migrates_legacy_notification_rows(tmp_path, monkeypatch):
    monkeypatch.setattr(main,"DB_PATH",tmp_path/"legacy-notifications.db")
    with main.connect() as db:
        db.execute("CREATE TABLE notifications(id INTEGER PRIMARY KEY,donor_id INTEGER,campaign_id INTEGER,message TEXT,sent_at TEXT)")
        db.execute("INSERT INTO notifications(id,donor_id,campaign_id,message,sent_at) VALUES (1,1,1,'Lời nhắc cũ','2026-09-20 12:00:00')")

    main.initialize_database()
    main.initialize_database()
    with main.connect() as db:
        notification=db.execute("SELECT * FROM notifications WHERE id=1").fetchone()
        volunteer=db.execute("SELECT id FROM users WHERE username='tinhnguyen@machdo.com'").fetchone()
        assert notification["user_id"] == volunteer["id"]
        assert notification["title"]
        assert notification["message"] == "Lời nhắc cũ"
        assert notification["type"] == "system"
        assert notification["is_read"] == 0
        assert notification["created_at"] == "2026-09-20 12:00:00"


def test_campaign_schedule_changes_notify_booked_volunteers(tmp_path, monkeypatch):
    monkeypatch.setattr(main,"DB_PATH",tmp_path/"schedule-notifications.db")
    main.initialize_database()
    client=TestClient(main.app)
    coordinator=client.post("/api/auth/login",json={"email":"dieuphoi@machdo.com","password":main.DEMO_PASSWORD}).json()["token"]
    volunteer=client.post("/api/auth/login",json={"email":"tinhnguyen@machdo.com","password":main.DEMO_PASSWORD}).json()
    manager_headers={"Authorization":f"Bearer {coordinator}"}
    volunteer_headers={"Authorization":f"Bearer {volunteer['token']}"}
    with main.connect() as db:
        donor_id=int(volunteer["user"]["donor_id"])
        campaign_id=db.execute("INSERT INTO campaigns(title,venue,campaign_date,start_time,end_time) VALUES ('Ngày hội','Điểm hiến cũ','2026-10-12','08:00','09:00')").lastrowid
        slot_id=db.execute("INSERT INTO slots(campaign_id,start_at,end_at,capacity) VALUES (?,'2026-10-12T08:00','2026-10-12T09:00',10)",(campaign_id,)).lastrowid
        db.execute("INSERT INTO appointments(donor_id,slot_id,status) VALUES (?,?,'Đã đăng ký')",(donor_id,slot_id))

    edit={"title":"Ngày hội","venue":"Điểm hiến mới","campaign_date":"2026-10-12","slots":[{"id":slot_id,"start_time":"08:00","end_time":"09:00","capacity":10}]}
    assert client.put(f"/api/campaigns/{campaign_id}",headers=manager_headers,json=edit).status_code == 200
    inbox=client.get("/api/notifications",headers=volunteer_headers).json()
    assert len(inbox) == 1
    assert inbox[0]["type"] == "system"
    assert "Điểm hiến mới" in inbox[0]["message"]

    closed=client.patch(f"/api/campaigns/{campaign_id}/status",headers=manager_headers,json={"status":"Tạm dừng"})
    assert closed.status_code == 200
    inbox=client.get("/api/notifications",headers=volunteer_headers).json()
    assert len(inbox) == 2
    assert any("Tạm dừng" in item["message"] for item in inbox)


def test_volunteer_only_sees_and_books_their_own_donor_record(tmp_path, monkeypatch):
    monkeypatch.setattr(main,"DB_PATH",tmp_path/"volunteer.db")
    main.initialize_database()
    client=TestClient(main.app)
    token=client.post("/api/auth/login",json={"email":"tinhnguyen@machdo.com","password":main.DEMO_PASSWORD}).json()["token"]
    headers={"Authorization":f"Bearer {token}"}
    assert client.get("/api/donors",headers=headers).status_code == 403
    own_donor=client.get("/api/donors/me",headers=headers).json()
    with main.connect() as db:
        another=db.execute("SELECT id FROM donors WHERE id!=? LIMIT 1",(own_donor["id"],)).fetchone()[0]
        slot=db.execute("SELECT id FROM slots LIMIT 1").fetchone()[0]
    denied=client.post("/api/appointments",json={"donor_id":another,"slot_id":slot},headers=headers)
    own=client.post("/api/appointments",json={"donor_id":own_donor["id"],"slot_id":slot},headers=headers)
    assert denied.status_code == 403
    assert own.status_code == 201
    assert [item["donor_id"] for item in client.get("/api/appointments",headers=headers).json()] == [own_donor["id"]]


def test_logout_revokes_session_token(tmp_path, monkeypatch):
    monkeypatch.setattr(main,"DB_PATH",tmp_path/"logout.db")
    main.initialize_database()
    client=TestClient(main.app)
    token=client.post("/api/auth/login",json={"email":"admin@machdo.com","password":main.DEMO_PASSWORD}).json()["token"]
    headers={"Authorization":f"Bearer {token}"}
    assert client.post("/api/auth/logout",headers=headers).status_code == 200
    assert client.get("/api/dashboard",headers=headers).status_code == 401


def test_procedure_chat_uses_approved_document_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr(main,"DB_PATH",tmp_path/"procedures.db")
    monkeypatch.delenv("OPENAI_API_KEY",raising=False)
    main.initialize_database()
    client=TestClient(main.app)
    token=client.post("/api/auth/login",json={"email":"tinhnguyen@machdo.com","password":main.DEMO_PASSWORD}).json()["token"]
    response=client.post("/api/chat",json={"question":"Sau khi hiến máu cần làm gì?"},headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json; charset=utf-8"
    assert "Nghỉ tại điểm hiến" in response.json()["text"]
    compatibility=client.post("/api/ai/answer",json={"question":"Sau khi hiến máu cần làm gì?"},headers={"Authorization":f"Bearer {token}"})
    assert compatibility.status_code == 200
    assert compatibility.json()["text"] == response.json()["text"]


def test_procedure_chat_retrieves_relevant_approved_documents(tmp_path, monkeypatch):
    monkeypatch.setattr(main,"DB_PATH",tmp_path/"rag.db")
    monkeypatch.setenv("OPENAI_API_KEY","test-key")
    prompts=[]
    monkeypatch.setattr(main,"ai_call",lambda system,prompt: prompts.append(system) or "Đã truy xuất tài liệu phù hợp.")
    main.initialize_database()
    client=TestClient(main.app)
    token=client.post("/api/auth/login",json={"email":"tinhnguyen@machdo.com","password":main.DEMO_PASSWORD}).json()["token"]
    headers={"Authorization":f"Bearer {token}"}
    answer=client.post("/api/chat",headers=headers,json={"question":"Sau khi hiến máu cần làm gì?"})
    unknown=client.post("/api/chat",headers=headers,json={"question":"Thủ tục đổi số điện thoại ở đâu?"})
    unsupported_interval=client.post("/api/chat",headers=headers,json={"question":"Khoảng cách giữa 2 lần hiến máu là bao lâu?"})
    assert answer.json()["text"] == "Đã truy xuất tài liệu phù hợp."
    assert "Sau khi hiến máu:" in prompts[0]
    assert "Điều kiện hiến máu:" not in prompts[0]
    assert "chưa tìm thấy" in unknown.json()["text"]
    assert "chưa tìm thấy" in unsupported_interval.json()["text"]
    assert len(prompts) == 1


def test_admin_can_create_donor_and_link_volunteer_account(tmp_path, monkeypatch):
    monkeypatch.setattr(main,"DB_PATH",tmp_path/"account.db")
    main.initialize_database()
    client=TestClient(main.app)
    admin=client.post("/api/auth/login",json={"email":"admin@machdo.com","password":main.DEMO_PASSWORD}).json()["token"]
    response=client.post("/api/donors",headers={"Authorization":f"Bearer {admin}"},json={
        "full_name":"Demo Volunteer","phone":"0900000011","email":"demo@example.vn","blood_group":"A+",
        "login_email":"demo-volunteer@example.com","login_password":"DemoPass123"
    })
    assert response.status_code == 201
    donor=response.json()
    assert donor["account_created"] is True
    assert donor["created_at"]
    login=client.post("/api/auth/login",json={"email":"demo-volunteer@example.com","password":"DemoPass123"})
    assert login.status_code == 200
    profile=client.get("/api/donors/me",headers={"Authorization":f"Bearer {login.json()['token']}"})
    assert profile.json()["id"] == donor["id"]


def test_campaign_custom_slots_edit_status_and_safe_delete(tmp_path, monkeypatch):
    monkeypatch.setattr(main,"DB_PATH",tmp_path/"campaigns.db")
    main.initialize_database()
    client=TestClient(main.app)
    token=client.post("/api/auth/login",json={"email":"dieuphoi@machdo.com","password":main.DEMO_PASSWORD}).json()["token"]
    headers={"Authorization":f"Bearer {token}"}
    payload={"title":"Sẻ chia","venue":"Nhà văn hóa","campaign_date":"2026-10-20","description":"Ngày hội cộng đồng","slots":[
        {"start_time":"08:30","end_time":"09:30","capacity":2},
        {"start_time":"10:00","end_time":"11:00","capacity":3}
    ]}
    created=client.post("/api/campaigns",headers=headers,json=payload)
    assert created.status_code == 201
    campaign=created.json()
    assert [(slot["start_at"][11:],slot["capacity"]) for slot in campaign["slots"]] == [("08:30",2),("10:00",3)]
    overlap={**payload,"slots":[{"start_time":"08:00","end_time":"10:00","capacity":5},{"start_time":"09:00","end_time":"11:00","capacity":5}]}
    assert client.post("/api/campaigns",headers=headers,json=overlap).status_code == 422

    edited={**payload,"title":"Sẻ chia mùa thu","status":"Tạm dừng","slots":[
        {"id":campaign["slots"][0]["id"],"start_time":"08:30","end_time":"09:30","capacity":4},
        {"start_time":"12:00","end_time":"13:00","capacity":6}
    ]}
    updated=client.put(f"/api/campaigns/{campaign['id']}",headers=headers,json=edited)
    assert updated.status_code == 200
    assert updated.json()["title"] == "Sẻ chia mùa thu"
    assert updated.json()["status"] == "Tạm dừng"
    assert [slot["capacity"] for slot in updated.json()["slots"]] == [4,6]

    closed=client.patch(f"/api/campaigns/{campaign['id']}/status",headers=headers,json={"status":"Đã đóng"})
    assert closed.json()["status"] == "Đã đóng"
    assert client.delete(f"/api/campaigns/{campaign['id']}",headers=headers).status_code == 204


def test_campaign_with_bookings_cannot_remove_slot_or_be_deleted(tmp_path, monkeypatch):
    monkeypatch.setattr(main,"DB_PATH",tmp_path/"booked-campaign.db")
    main.initialize_database()
    client=TestClient(main.app)
    admin=client.post("/api/auth/login",json={"email":"admin@machdo.com","password":main.DEMO_PASSWORD}).json()["token"]
    volunteer=client.post("/api/auth/login",json={"email":"tinhnguyen@machdo.com","password":main.DEMO_PASSWORD}).json()["token"]
    admin_headers={"Authorization":f"Bearer {admin}"}
    volunteer_headers={"Authorization":f"Bearer {volunteer}"}
    payload={"title":"Booked","venue":"Hall","campaign_date":"2026-10-21","slots":[{"start_time":"08:00","end_time":"09:00","capacity":2}]}
    campaign=client.post("/api/campaigns",headers=admin_headers,json=payload).json()
    slot=campaign["slots"][0]
    donor=client.get("/api/donors/me",headers=volunteer_headers).json()
    assert client.post("/api/appointments",headers=volunteer_headers,json={"donor_id":donor["id"],"slot_id":slot["id"]}).status_code == 201
    edit={**payload,"slots":[]}
    response=client.put(f"/api/campaigns/{campaign['id']}",headers=admin_headers,json=edit)
    assert response.status_code == 422
    moved={**payload,"campaign_date":"2026-10-22","slots":[{"id":slot["id"],"start_time":"08:00","end_time":"09:00","capacity":2}]}
    assert client.put(f"/api/campaigns/{campaign['id']}",headers=admin_headers,json=moved).status_code == 409
    edit["slots"]=[{"start_time":"09:00","end_time":"10:00","capacity":2}]
    assert client.put(f"/api/campaigns/{campaign['id']}",headers=admin_headers,json=edit).status_code == 409
    assert client.delete(f"/api/campaigns/{campaign['id']}",headers=admin_headers).status_code == 409

def test_ai_monthly_report_returns_campaign_statistics(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "monthly-report.db")
    monkeypatch.setattr(main, "ai_call", lambda system, prompt: "Tháng 9 có hoạt động tích cực.")
    main.initialize_database()
    client = TestClient(main.app)
    token = client.post("/api/auth/login", json={"email": "dieuphoi@machdo.com", "password": main.DEMO_PASSWORD}).json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    with main.connect() as db:
        cid = db.execute("INSERT INTO campaigns(title,venue,campaign_date,start_time,end_time) VALUES ('Tháng chín','Nhà văn hóa','2050-09-12','08:00','10:00')").lastrowid
        slot = db.execute("INSERT INTO slots(campaign_id,start_at,end_at,capacity) VALUES (?, '2050-09-12T08:00','2050-09-12T09:00',10)", (cid,)).lastrowid
        donor = db.execute("SELECT id FROM donors LIMIT 1").fetchone()[0]
        db.execute("INSERT INTO appointments(donor_id,slot_id) VALUES (?,?)", (donor, slot))
    response = client.post("/api/ai/monthly-report", headers=headers, json={"month": 9, "year": 2050})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json; charset=utf-8"
    assert response.json()["summary"] == {"campaign_count": 1, "registrations": 1, "completion_rate": 10.0}
    assert response.json()["report"] == "Tháng 9 có hoạt động tích cực."
    assert client.post("/api/ai/monthly-report", headers=headers, json={"month": 13, "year": 2026}).status_code == 422
    monkeypatch.setattr(main, "ai_call", lambda system, prompt: None)
    fallback = client.post("/api/ai/monthly-report", headers=headers, json={"month": 9, "year": 2050})
    assert fallback.headers["content-type"] == "application/json; charset=utf-8"
    assert fallback.json()["mode"] == "Mẫu dự phòng"
    assert "Trong tháng 9/2050" in fallback.content.decode("utf-8")


def test_custom_reminder_message_is_recorded_for_campaign_volunteers(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "custom-reminder.db")
    main.SESSIONS.clear()
    main.initialize_database()
    client = TestClient(main.app)
    coordinator = client.post("/api/auth/login", json={"email": "dieuphoi@machdo.com", "password": main.DEMO_PASSWORD}).json()["token"]
    volunteer = client.post("/api/auth/login", json={"email": "tinhnguyen@machdo.com", "password": main.DEMO_PASSWORD}).json()
    with main.connect() as db:
        campaign = db.execute("SELECT id,title FROM campaigns LIMIT 1").fetchone()
        slot = db.execute("SELECT id FROM slots WHERE campaign_id=? LIMIT 1", (campaign["id"],)).fetchone()[0]
        donor = volunteer["user"]["donor_id"]
        db.execute("INSERT INTO appointments(donor_id,slot_id) VALUES (?,?)", (donor, slot))
    custom_message = "Xin mời tham gia đúng giờ và mang theo CCCD."
    response = client.post("/api/reminders", headers={"Authorization": f"Bearer {coordinator}"}, json={"campaign_id": campaign["id"], "message": custom_message})
    assert response.status_code == 200
    assert response.json()["sent"] == 1
    inbox = client.get("/api/notifications", headers={"Authorization": f"Bearer {volunteer['token']}"}).json()
    assert any(item["message"] == custom_message for item in inbox)


def test_admin_can_list_update_lock_unlock_and_delete_accounts(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "admin-users.db")
    main.SESSIONS.clear()
    main.initialize_database()
    client = TestClient(main.app)
    admin = client.post("/api/auth/login", json={"email": "admin@machdo.com", "password": main.DEMO_PASSWORD}).json()
    volunteer = client.post("/api/auth/login", json={"email": "tinhnguyen@machdo.com", "password": main.DEMO_PASSWORD}).json()
    admin_headers = {"Authorization": f"Bearer {admin['token']}"}
    volunteer_headers = {"Authorization": f"Bearer {volunteer['token']}"}

    listed = client.get("/api/admin/users", headers=admin_headers)
    assert listed.status_code == 200
    account = next(item for item in listed.json() if item["email"] == "tinhnguyen@machdo.com")
    assert {"id", "email", "full_name", "role", "status", "created_at"} <= account.keys()
    assert account["role"] == "volunteer"
    assert account["status"] == "active"
    assert account["created_at"]

    changed_role = client.put(f"/api/admin/users/{account['id']}/role", headers=admin_headers, json={"role": "coordinator"})
    assert changed_role.status_code == 200
    assert changed_role.json()["role"] == "coordinator"
    assert client.put(f"/api/admin/users/{account['id']}/role", headers=admin_headers, json={"role": "owner"}).status_code == 422

    locked = client.put(f"/api/admin/users/{account['id']}/status", headers=admin_headers, json={"status": "locked"})
    assert locked.status_code == 200
    assert locked.json()["status"] == "locked"
    assert client.get("/api/campaigns", headers=volunteer_headers).status_code == 401
    assert client.post("/api/auth/login", json={"email": "tinhnguyen@machdo.com", "password": main.DEMO_PASSWORD}).status_code == 403
    assert client.put(f"/api/admin/users/{account['id']}/status", headers=admin_headers, json={"status": "active"}).json()["status"] == "active"
    assert client.post("/api/auth/login", json={"email": "tinhnguyen@machdo.com", "password": main.DEMO_PASSWORD}).status_code == 200

    assert client.put(f"/api/admin/users/{admin['user']['id']}/status", headers=admin_headers, json={"status": "locked"}).status_code == 400
    assert client.delete(f"/api/admin/users/{admin['user']['id']}", headers=admin_headers).status_code == 400
    deleted = client.delete(f"/api/admin/users/{account['id']}", headers=admin_headers)
    assert deleted.status_code == 204
    assert all(item["id"] != account["id"] for item in client.get("/api/admin/users", headers=admin_headers).json())


def test_admin_user_management_endpoints_reject_non_admin_roles(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "admin-user-permissions.db")
    main.SESSIONS.clear()
    main.initialize_database()
    client = TestClient(main.app)
    coordinator = client.post("/api/auth/login", json={"email": "dieuphoi@machdo.com", "password": main.DEMO_PASSWORD}).json()
    volunteer = client.post("/api/auth/login", json={"email": "tinhnguyen@machdo.com", "password": main.DEMO_PASSWORD}).json()
    target = volunteer["user"]["id"]
    for login in (coordinator, volunteer):
        headers = {"Authorization": f"Bearer {login['token']}"}
        assert client.get("/api/admin/users", headers=headers).status_code == 403
        assert client.put(f"/api/admin/users/{target}/role", headers=headers, json={"role": "admin"}).status_code == 403
        assert client.put(f"/api/admin/users/{target}/status", headers=headers, json={"status": "locked"}).status_code == 403
        assert client.delete(f"/api/admin/users/{target}", headers=headers).status_code == 403


def test_admin_can_create_all_account_roles_with_hashed_password(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "admin-create-users.db")
    main.SESSIONS.clear()
    main.initialize_database()
    client = TestClient(main.app)
    admin = client.post("/api/auth/login", json={"email": "admin@machdo.com", "password": main.DEMO_PASSWORD}).json()
    headers = {"Authorization": f"Bearer {admin['token']}"}
    for role in ("volunteer", "coordinator", "admin"):
        payload = {"full_name": f"New {role}", "email": f"new-{role}@example.com", "password": "InitialPass123", "role": role}
        response = client.post("/api/admin/users", headers=headers, json=payload)
        assert response.status_code == 201
        account = response.json()
        assert {key: account[key] for key in ("email", "full_name", "role", "status")} == {"email": payload["email"], "full_name": payload["full_name"], "role": role, "status": "active"}
        assert account["created_at"]
        with main.connect() as db:
            row = db.execute("SELECT password FROM users WHERE id=?", (account["id"],)).fetchone()
        assert row["password"] != payload["password"]
        assert main.verify_password(payload["password"], row["password"])
    duplicate = client.post("/api/admin/users", headers=headers, json={"full_name": "Duplicate", "email": "NEW-VOLUNTEER@example.com", "password": "InitialPass123", "role": "volunteer"})
    assert duplicate.status_code == 400
    assert client.post("/api/admin/users", headers=headers, json={"full_name": "Invalid", "email": "bad-email", "password": "InitialPass123", "role": "volunteer"}).status_code == 422


def test_admin_create_user_rejects_non_admin_and_unauthenticated(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "admin-create-permissions.db")
    main.SESSIONS.clear()
    main.initialize_database()
    client = TestClient(main.app)
    payload = {"full_name": "New Account", "email": "new-account@example.com", "password": "InitialPass123", "role": "volunteer"}
    assert client.post("/api/admin/users", json=payload).status_code == 401
    for email in ("dieuphoi@machdo.com", "tinhnguyen@machdo.com"):
        login = client.post("/api/auth/login", json={"email": email, "password": main.DEMO_PASSWORD}).json()
        response = client.post("/api/admin/users", headers={"Authorization": f"Bearer {login['token']}"}, json=payload)
        assert response.status_code == 403


def test_ai_campaign_summary_reports_counts_and_requires_manager_role(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "campaign-summary.db")
    main.SESSIONS.clear()
    monkeypatch.setattr(main, "ai_call", lambda system, prompt: "AI summary from campaign figures.")
    main.initialize_database()
    client = TestClient(main.app)
    coordinator = client.post("/api/auth/login", json={"email": "dieuphoi@machdo.com", "password": main.DEMO_PASSWORD}).json()
    volunteer = client.post("/api/auth/login", json={"email": "tinhnguyen@machdo.com", "password": main.DEMO_PASSWORD}).json()
    headers = {"Authorization": f"Bearer {coordinator['token']}"}
    with main.connect() as db:
        campaign_id = db.execute("INSERT INTO campaigns(title,venue,campaign_date,start_time,end_time) VALUES ('Summary campaign','Hall','2050-09-12','08:00','10:00')").lastrowid
        slot_id = db.execute("INSERT INTO slots(campaign_id,start_at,end_at,capacity) VALUES (?, '2050-09-12T08:00','2050-09-12T09:00',10)", (campaign_id,)).lastrowid
        donor_id = db.execute("SELECT id FROM donors LIMIT 1").fetchone()[0]
        db.execute("INSERT INTO appointments(donor_id,slot_id,status) VALUES (?,?,'Đã đăng ký')", (donor_id, slot_id))

    response = client.post("/api/ai/campaign-summary", headers=headers, json={"campaign_id": campaign_id})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json; charset=utf-8"
    assert response.json()["summary"] == "AI summary from campaign figures."
    assert response.json()["statistics"]["registrations"] == 1
    assert response.json()["statistics"]["target"] == 10
    assert response.json()["statistics"]["completion_rate"] == 10.0
    monkeypatch.setattr(main, "ai_call", lambda system, prompt: None)
    fallback = client.post("/api/ai/summarize-campaign", headers=headers, json={"campaign_id": campaign_id})
    assert fallback.status_code == 200
    assert fallback.headers["content-type"] == "application/json; charset=utf-8"
    assert fallback.json()["mode"] == "Mẫu dự phòng"
    volunteer_headers = {"Authorization": f"Bearer {volunteer['token']}"}
    assert client.post("/api/ai/campaign-summary", headers=volunteer_headers, json={"campaign_id": campaign_id}).status_code == 403
    assert client.post("/api/ai/campaign-summary", headers=headers, json={"campaign_id": campaign_id + 100}).status_code == 404


def test_ai_yearly_report_returns_annual_and_monthly_statistics_as_utf8(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "yearly-report.db")
    main.SESSIONS.clear()
    monkeypatch.setattr(main, "ai_call", lambda system, prompt: "Annual trend report.")
    main.initialize_database()
    client = TestClient(main.app)
    coordinator = client.post("/api/auth/login", json={"email": "dieuphoi@machdo.com", "password": main.DEMO_PASSWORD}).json()
    headers = {"Authorization": f"Bearer {coordinator['token']}"}
    with main.connect() as db:
        campaign_ids = []
        for title, day, capacity in (("Winter drive", "2050-01-12", 10), ("Summer drive", "2050-07-12", 4)):
            campaign_id = db.execute("INSERT INTO campaigns(title,venue,campaign_date,start_time,end_time) VALUES (?,?,?,?,?)", (title, "Hall", day, "08:00", "10:00")).lastrowid
            slot_id = db.execute("INSERT INTO slots(campaign_id,start_at,end_at,capacity) VALUES (?,?,?,?)", (campaign_id, f"{day}T08:00", f"{day}T09:00", capacity)).lastrowid
            campaign_ids.append((campaign_id, slot_id))
        donor_ids = [row[0] for row in db.execute("SELECT id FROM donors ORDER BY id LIMIT 3").fetchall()]
        db.execute("INSERT INTO appointments(donor_id,slot_id,status) VALUES (?,?,'Đã đăng ký')", (donor_ids[0], campaign_ids[0][1]))
        db.execute("INSERT INTO appointments(donor_id,slot_id,status) VALUES (?,?,'Đã đăng ký')", (donor_ids[1], campaign_ids[1][1]))
        db.execute("INSERT INTO appointments(donor_id,slot_id,status) VALUES (?,?,'Đã tham gia')", (donor_ids[2], campaign_ids[1][1]))

    response = client.post("/api/ai/yearly-report", headers=headers, json={"year": 2050})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json; charset=utf-8"
    payload = response.json()
    assert payload["summary"] == {"campaign_count": 2, "registrations": 3, "average_completion_rate": 30.0}
    assert len(payload["monthly"]) == 12
    assert payload["monthly"][0]["completion_rate"] == 10.0
    assert payload["monthly"][6]["completion_rate"] == 50.0
    assert payload["report"] == "Annual trend report."
    assert client.post("/api/ai/yearly-report", headers=headers, json={"year": 1999}).status_code == 422


def test_ai_views_have_separate_routes_and_containers():
    source = (main.STATIC / "app.js").read_text(encoding="utf-8")
    html = (main.STATIC / "index.html").read_text(encoding="utf-8")
    assert '"ai-reports": pages["ai-reports"]' in source
    assert '"ai-reports": aiReportsView' in source
    assert 'id="ai-qa-section"' in source
    assert 'id="ai-reports-section"' in source
    assert 'ai: aiQaView' in source
    assert 'id="monthly-report-panel"' in source
    assert 'id="yearly-report-panel"' in source
    assert 'data-action="yearly-report"' in source
    assert '<meta charset="utf-8">' in html
    assert 'app.js?v=2.3' in html


def test_admin_and_coordinator_campaign_creation_and_details(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "campaign_details.db")
    main.initialize_database()
    client = TestClient(main.app)

    admin_login = client.post("/api/auth/login", json={"email": "admin@machdo.com", "password": main.DEMO_PASSWORD}).json()
    admin_headers = {"Authorization": f"Bearer {admin_login['token']}"}

    coord_login = client.post("/api/auth/login", json={"email": "dieuphoi@machdo.com", "password": main.DEMO_PASSWORD}).json()
    coord_headers = {"Authorization": f"Bearer {coord_login['token']}"}

    # Coordinator creates a campaign
    coord_res = client.post("/api/campaigns", headers=coord_headers, json={
        "title": "Chiến dịch Điều phối viên tạo",
        "venue": "Nhà Văn hóa TP",
        "campaign_date": "2026-11-20",
        "description": "Chiến dịch hiến máu do điều phối viên khởi xướng",
        "slots": [{"start_time": "08:00", "end_time": "09:00", "capacity": 30}],
        "status": "Đang mở"
    })
    assert coord_res.status_code == 201
    coord_cid = coord_res.json()["id"]
    assert "Điều phối viên" in coord_res.json()["created_by"]
    assert "dieuphoi@machdo.com" in coord_res.json()["created_by"]

    # Admin creates a campaign
    admin_res = client.post("/api/campaigns", headers=admin_headers, json={
        "title": "Chiến dịch Quản trị viên tạo",
        "venue": "Trung tâm Y tế quận",
        "campaign_date": "2026-11-25",
        "description": "Chiến dịch hiến máu do admin trực tiếp tạo",
        "slots": [{"start_time": "09:00", "end_time": "10:00", "capacity": 50}],
        "status": "Đang mở"
    })
    assert admin_res.status_code == 201
    admin_cid = admin_res.json()["id"]
    assert "Quản trị viên" in admin_res.json()["created_by"]
    assert "admin@machdo.com" in admin_res.json()["created_by"]

    # Admin views Coordinator's campaign details via GET /api/campaigns/{cid}
    detail_res = client.get(f"/api/campaigns/{coord_cid}", headers=admin_headers)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["title"] == "Chiến dịch Điều phối viên tạo"
    assert "Điều phối viên" in detail["created_by"]
    assert len(detail["slots"]) == 1
    assert "appointments" in detail


def test_admin_creates_user_by_role_and_views_account_details(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "admin_user_mgmt.db")
    main.initialize_database()
    client = TestClient(main.app)

    admin_login = client.post("/api/auth/login", json={"email": "admin@machdo.com", "password": main.DEMO_PASSWORD}).json()
    admin_headers = {"Authorization": f"Bearer {admin_login['token']}"}

    # Admin creates volunteer
    v_res = client.post("/api/admin/users", headers=admin_headers, json={
        "email": "tnv_test@example.com",
        "password": "Password123!",
        "full_name": "Tình Nguyện Viên Mới",
        "role": "volunteer",
        "phone": "0987654321",
        "blood_group": "AB+"
    })
    assert v_res.status_code == 201
    v_id = v_res.json()["id"]
    assert v_res.json()["role"] == "volunteer"
    assert v_res.json()["blood_group"] == "AB+"

    # Admin creates coordinator
    c_res = client.post("/api/admin/users", headers=admin_headers, json={
        "email": "dp_test@example.com",
        "password": "Password123!",
        "full_name": "Điều Phối Viên Mới",
        "role": "coordinator",
        "phone": "0912345678",
        "organization": "Bệnh viện Đa khoa",
        "job_title": "Trưởng nhóm điều phối"
    })
    assert c_res.status_code == 201
    c_id = c_res.json()["id"]
    assert c_res.json()["role"] == "coordinator"
    assert c_res.json()["organization"] == "Bệnh viện Đa khoa"

    # Admin views volunteer details
    v_detail = client.get(f"/api/admin/users/{v_id}", headers=admin_headers)
    assert v_detail.status_code == 200
    v_data = v_detail.json()
    assert v_data["full_name"] == "Tình Nguyện Viên Mới"
    assert v_data["blood_group"] == "AB+"
    assert v_data["donor_id"] is not None
    assert "appointments" in v_data

    # Admin views coordinator details
    c_detail = client.get(f"/api/admin/users/{c_id}", headers=admin_headers)
    assert c_detail.status_code == 200
    c_data = c_detail.json()
    assert c_data["full_name"] == "Điều Phối Viên Mới"
    assert c_data["organization"] == "Bệnh viện Đa khoa"
    assert c_data["job_title"] == "Trưởng nhóm điều phối"

