# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import urllib.error
import urllib.request
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path
from typing import Annotated, Iterator, Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
DB_PATH = Path(os.getenv("BLOOD_DONATION_DB", ROOT / "data" / "blood_donation.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
app = FastAPI(title="Mạch Đỏ | Quản lý hiến máu")
app.mount("/static", StaticFiles(directory=STATIC), name="static")
SESSIONS: dict[str, dict[str, str]] = {}
DEMO_PASSWORD = "HienMau2026!"
SYSTEM_ACCOUNTS = {
    "admin@gmail.com": ("Quản trị viên", "admin"),
    "dieuphoi@gmail.com": ("Điều phối viên", "coordinator"),
}


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    db = sqlite3.connect(DB_PATH, timeout=10, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA journal_mode=WAL")
    try:
        yield db
    finally:
        db.close()


def hash_password(value: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", value.encode(), salt, 180_000)
    return f"{salt.hex()}:{digest.hex()}"


def verify_password(value: str, encoded: str) -> bool:
    try:
        salt, digest = encoded.split(":", 1)
        actual = hashlib.pbkdf2_hmac("sha256", value.encode(), bytes.fromhex(salt), 180_000).hex()
    except ValueError:
        return False
    return hmac.compare_digest(actual, digest)


def initialize_database() -> None:
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT UNIQUE,display_name TEXT,role TEXT,password TEXT,donor_id INTEGER REFERENCES donors(id),phone TEXT NOT NULL DEFAULT '',blood_group TEXT NOT NULL DEFAULT 'Chưa cập nhật',birth_date TEXT,address TEXT NOT NULL DEFAULT '',organization TEXT NOT NULL DEFAULT '',job_title TEXT NOT NULL DEFAULT '',email TEXT NOT NULL DEFAULT '',full_name TEXT NOT NULL DEFAULT '',status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','locked')),created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS donors(id INTEGER PRIMARY KEY,full_name TEXT NOT NULL,phone TEXT NOT NULL,email TEXT DEFAULT '',blood_group TEXT DEFAULT 'Chưa cập nhật',created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,birth_date TEXT,address TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS campaigns(id INTEGER PRIMARY KEY,title TEXT NOT NULL,venue TEXT NOT NULL,campaign_date TEXT NOT NULL,start_time TEXT NOT NULL,end_time TEXT NOT NULL,description TEXT DEFAULT '',status TEXT DEFAULT 'Đang mở');
        CREATE TABLE IF NOT EXISTS slots(id INTEGER PRIMARY KEY,campaign_id INTEGER REFERENCES campaigns(id),start_at TEXT,end_at TEXT,capacity INTEGER,UNIQUE(campaign_id,start_at));
        CREATE TABLE IF NOT EXISTS appointments(id INTEGER PRIMARY KEY,donor_id INTEGER REFERENCES donors(id),slot_id INTEGER REFERENCES slots(id),status TEXT DEFAULT 'Đã đăng ký',created_at TEXT DEFAULT CURRENT_TIMESTAMP,UNIQUE(donor_id,slot_id));
        CREATE TABLE IF NOT EXISTS notifications(id INTEGER PRIMARY KEY,user_id INTEGER REFERENCES users(id),title TEXT NOT NULL DEFAULT '',message TEXT NOT NULL DEFAULT '',type TEXT NOT NULL DEFAULT 'system',is_read INTEGER NOT NULL DEFAULT 0,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,appointment_id INTEGER REFERENCES appointments(id),donor_id INTEGER REFERENCES donors(id),campaign_id INTEGER REFERENCES campaigns(id),sent_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS procedures(id INTEGER PRIMARY KEY,title TEXT,content TEXT);
        """)
        notification_columns = {row[1] for row in db.execute("PRAGMA table_info(notifications)")}
        notification_migrations = {
            "user_id": "INTEGER REFERENCES users(id)",
            "title": "TEXT NOT NULL DEFAULT ''",
            "type": "TEXT NOT NULL DEFAULT 'system'",
            "is_read": "INTEGER NOT NULL DEFAULT 0",
            "created_at": "TEXT NOT NULL DEFAULT ''",
            "appointment_id": "INTEGER REFERENCES appointments(id)",
        }
        for column, definition in notification_migrations.items():
            if column not in notification_columns:
                db.execute(f"ALTER TABLE notifications ADD COLUMN {column} {definition}")
        db.execute("UPDATE notifications SET created_at=COALESCE(NULLIF(created_at,''),sent_at,CURRENT_TIMESTAMP)")
        db.execute("UPDATE notifications SET title=COALESCE(NULLIF(title,''),(SELECT title FROM campaigns WHERE campaigns.id=notifications.campaign_id),'Thông báo hiến máu')")
        db.execute("UPDATE notifications SET user_id=(SELECT id FROM users WHERE users.donor_id=notifications.donor_id LIMIT 1) WHERE user_id IS NULL AND donor_id IS NOT NULL")
        db.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user_created ON notifications(user_id,created_at DESC)")
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_notifications_reminder_appointment ON notifications(user_id,appointment_id) WHERE type='reminder' AND appointment_id IS NOT NULL")
        user_columns={row[1] for row in db.execute("PRAGMA table_info(users)")}
        if "donor_id" not in user_columns:
            db.execute("ALTER TABLE users ADD COLUMN donor_id INTEGER REFERENCES donors(id)")
        user_migrations={
            "email":"TEXT NOT NULL DEFAULT ''",
            "full_name":"TEXT NOT NULL DEFAULT ''",
            "status":"TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','locked'))",
            "created_at":"TEXT NOT NULL DEFAULT ''",
        }
        for column,definition in user_migrations.items():
            if column not in user_columns:
                db.execute(f"ALTER TABLE users ADD COLUMN {column} {definition}")
        db.execute("UPDATE users SET email=COALESCE(NULLIF(email,''),username,''),full_name=COALESCE(NULLIF(full_name,''),display_name,''),created_at=COALESCE(NULLIF(created_at,''),CURRENT_TIMESTAMP),status=CASE WHEN status IN ('active','locked') THEN status ELSE 'active' END")
        user_profile_migrations = {
            "phone": "TEXT NOT NULL DEFAULT ''",
            "blood_group": "TEXT NOT NULL DEFAULT 'Chưa cập nhật'",
            "birth_date": "TEXT",
            "address": "TEXT NOT NULL DEFAULT ''",
            "organization": "TEXT NOT NULL DEFAULT ''",
            "job_title": "TEXT NOT NULL DEFAULT ''",
        }
        for column, definition in user_profile_migrations.items():
            if column not in user_columns:
                db.execute(f"ALTER TABLE users ADD COLUMN {column} {definition}")
        donor_columns={row[1] for row in db.execute("PRAGMA table_info(donors)")}
        if "created_at" not in donor_columns:
            db.execute("ALTER TABLE donors ADD COLUMN created_at TEXT NOT NULL DEFAULT ''")
            db.execute("UPDATE donors SET created_at=CURRENT_TIMESTAMP WHERE created_at=''")
        if "birth_date" not in donor_columns:
            db.execute("ALTER TABLE donors ADD COLUMN birth_date TEXT")
        if "address" not in donor_columns:
            db.execute("ALTER TABLE donors ADD COLUMN address TEXT NOT NULL DEFAULT ''")
        for legacy, email in [("admin", "admin@machdo.vn"), ("dieuphoi", "dieuphoi@machdo.vn"), ("tinhnguyen", "tinhnguyen@machdo.vn")]:
            if db.execute("SELECT 1 FROM users WHERE username=?", (email,)).fetchone() is None:
                db.execute("UPDATE users SET username=? WHERE username=?", (email, legacy))
        demo_users = [(email, label, role) for email, (label, role) in SYSTEM_ACCOUNTS.items()]
        demo_users.append(("tinhnguyen@machdo.vn", "Tình nguyện viên", "volunteer"))
        for email, label, role in demo_users:
            db.execute("INSERT OR IGNORE INTO users(username,display_name,role,password,email,full_name) VALUES (?,?,?,?,?,?)", (email, label, role, hash_password(DEMO_PASSWORD),email,label))
        if not db.execute("SELECT 1 FROM campaigns LIMIT 1").fetchone():
            samples = [("Giọt hồng tháng 9", "Nhà Văn hóa Thanh niên", date.today()+timedelta(days=3), "08:00", "12:00", "Ngày hội hiến máu tình nguyện cộng đồng."), ("Chủ nhật Đỏ", "Trung tâm Hội nghị ICTU", date.today()+timedelta(days=9), "07:00", "11:00", "Cùng sẻ chia giọt máu, trao thêm hy vọng.")]
            for title, venue, day, start, end, description in samples:
                cid = db.execute("INSERT INTO campaigns(title,venue,campaign_date,start_time,end_time,description) VALUES (?,?,?,?,?,?)", (title,venue,day.isoformat(),start,end,description)).lastrowid
                for hour in range(int(start[:2]), int(end[:2])):
                    db.execute("INSERT INTO slots(campaign_id,start_at,end_at,capacity) VALUES (?,?,?,24)", (cid,f"{day.isoformat()}T{hour:02}:00",f"{day.isoformat()}T{hour+1:02}:00"))
        if not db.execute("SELECT 1 FROM donors LIMIT 1").fetchone():
            db.executemany("INSERT INTO donors(full_name,phone,email,blood_group) VALUES (?,?,?,?)", [("Nguyễn Minh Anh","0901234567","minhanh@example.vn","O+"),("Trần Gia Bảo","0912345678","giabao@example.vn","A+"),("Lê Thu Hà","0987654321","thuha@example.vn","B+"),("Phạm Quốc Huy","0976543210","quochuy@example.vn","AB+"),("Võ Khánh Linh","0934567890","khanhlinh@example.vn","O-")])
        db.execute("UPDATE users SET donor_id=(SELECT id FROM donors ORDER BY id LIMIT 1) WHERE username='tinhnguyen@machdo.vn' AND donor_id IS NULL")
        if not db.execute("SELECT 1 FROM procedures LIMIT 1").fetchone():
            db.executemany("INSERT INTO procedures(title,content) VALUES (?,?)", [("Trước khi hiến máu","Đăng ký thông tin, xuất trình giấy tờ tùy thân, được nhân viên y tế tư vấn và kiểm tra sức khỏe. Nên ăn nhẹ, uống đủ nước và nghỉ ngơi đầy đủ."),("Quy trình hiến máu","Quy trình gồm đăng ký, khám sàng lọc, hiến máu dưới sự giám sát của nhân viên y tế và nghỉ tại chỗ sau hiến; thường mất khoảng 45 đến 60 phút."),("Sau khi hiến máu","Nghỉ tại điểm hiến ít nhất 10 đến 15 phút, uống nước và dùng đồ ăn nhẹ. Tránh hoạt động gắng sức trong ngày; nếu thấy không khỏe, báo ngay nhân viên y tế."),("Điều kiện hiến máu","Việc đủ điều kiện hiến máu do nhân viên y tế đánh giá trực tiếp tại điểm hiến. Trợ lý không thể đánh giá sức khỏe cá nhân.")])


initialize_database()


class Login(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str


class RegisterInput(BaseModel):
    email: str = Field(min_length=5, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(min_length=2, max_length=100)
    role: Literal["donor", "volunteer"] = "donor"


class DonorInput(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=8, max_length=20)
    email: str = ""
    blood_group: str = "Chưa cập nhật"
    login_email: str | None = Field(default=None, min_length=5, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    login_password: str | None = Field(default=None, min_length=8, max_length=100)


class DonorProfileUpdate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone: str = Field(default="", max_length=20)
    blood_group: Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Chưa cập nhật"] = "Chưa cập nhật"
    birth_date: date | None = None
    address: str = Field(default="", max_length=300)
    organization: str = Field(default="", max_length=200)
    job_title: str = Field(default="", max_length=100)


class CoordinatorProfileUpdate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone: str = Field(default="", max_length=20)
    organization: str = Field(default="", max_length=200)
    job_title: str = Field(default="", max_length=100)


class ChangePasswordInput(BaseModel):
    current_password: str = Field(min_length=1, max_length=100)
    new_password: str = Field(min_length=8, max_length=100)
    confirm_password: str = Field(min_length=8, max_length=100)


class SlotInput(BaseModel):
    id: int | None = None
    start_time: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    end_time: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    capacity: int = Field(ge=1, le=500)


class CampaignInput(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    venue: str
    campaign_date: date
    description: str = ""
    slots: list[SlotInput] = Field(default_factory=list)
    start_time: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):00$")
    end_time: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):00$")
    capacity: int = Field(default=24, ge=1, le=500)
    status: Literal["Đang mở", "Đã đóng", "Tạm dừng"] = "Đang mở"


class CampaignStatusInput(BaseModel):
    status: Literal["Đang mở", "Đã đóng", "Tạm dừng"]


class AppointmentInput(BaseModel):
    donor_id: int
    slot_id: int


class StatusInput(BaseModel):
    status: Literal["Đã đăng ký", "Đã tham gia", "Vắng mặt", "Đã hủy"]


class AdminUserRoleInput(BaseModel):
    role: Literal["volunteer", "coordinator", "admin"]


class AdminUserCreateInput(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=100)
    role: Literal["volunteer", "coordinator", "admin"]


class AdminUserStatusInput(BaseModel):
    status: Literal["active", "locked"]


class ChatInput(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


class MonthlyReportInput(BaseModel):
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)


class YearlyReportInput(BaseModel):
    year: int = Field(ge=2000, le=2100)


class ReminderInput(BaseModel):
    campaign_id: int = Field(gt=0)
    message: str | None = Field(default=None, min_length=1, max_length=2000)


class CampaignSummaryInput(BaseModel):
    campaign_id: int = Field(gt=0)


def ai_json(payload: dict[str, object]) -> JSONResponse:
    return JSONResponse(content=payload, media_type="application/json; charset=utf-8")


def signed_in(authorization: Annotated[str | None, Header()] = None) -> dict[str, str]:
    user = SESSIONS.get(authorization.removeprefix("Bearer ") if authorization else "")
    if not user:
        raise HTTPException(401, "Vui lòng đăng nhập")
    return user


def roles(*allowed: str):
    def check(user: dict[str, str] = Depends(signed_in)) -> dict[str, str]:
        if user["role"] not in allowed:
            raise HTTPException(403, "Bạn không có quyền thực hiện thao tác này")
        return user
    return check


def campaign_info(db: sqlite3.Connection, cid: int) -> dict[str, object] | None:
    row = db.execute("SELECT * FROM campaigns WHERE id=?", (cid,)).fetchone()
    if row is None:
        return None
    result = dict(row)
    result["slots"] = [dict(item) for item in db.execute("""SELECT s.id,s.start_at,s.end_at,s.capacity,SUM(CASE WHEN a.status!='Đã hủy' THEN 1 ELSE 0 END) booked FROM slots s LEFT JOIN appointments a ON a.slot_id=s.id WHERE s.campaign_id=? GROUP BY s.id ORDER BY s.start_at""", (cid,))]
    return result


def slot_values(data: CampaignInput) -> list[dict[str, object]]:
    if data.slots:
        slots = [slot.model_dump() for slot in data.slots]
    elif data.start_time and data.end_time and data.end_time > data.start_time:
        slots = [
            {"id": None, "start_time": f"{hour:02}:00", "end_time": f"{hour + 1:02}:00", "capacity": data.capacity}
            for hour in range(int(data.start_time[:2]), int(data.end_time[:2]))
        ]
    else:
        raise HTTPException(422, "Thêm ít nhất một khung giờ hợp lệ")
    if not slots:
        raise HTTPException(422, "Thêm ít nhất một khung giờ")
    slots.sort(key=lambda slot: str(slot["start_time"]))
    for index, slot in enumerate(slots):
        if slot["end_time"] <= slot["start_time"]:
            raise HTTPException(422, "Giờ kết thúc phải sau giờ bắt đầu cho mỗi khung")
        if index and slots[index - 1]["end_time"] > slot["start_time"]:
            raise HTTPException(422, "Các khung giờ không được chồng lấn")
    return slots


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html", media_type="text/html; charset=utf-8")


@app.post("/api/register", status_code=201)
def register(data: RegisterInput) -> dict[str, str | int]:
    email = data.email.strip().lower()
    full_name = data.full_name.strip()
    if not email or not full_name:
        raise HTTPException(422, "Email và họ tên không được để trống")
    if email in SYSTEM_ACCOUNTS:
        raise HTTPException(400, "Email hệ thống không thể đăng ký")
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM users WHERE username=?", (email,)).fetchone():
            db.rollback()
            raise HTTPException(400, "Email đã tồn tại")
        donor_id = db.execute(
            "INSERT INTO donors(full_name,phone,email) VALUES (?,?,?)", (full_name, "", email)
        ).lastrowid
        role = "volunteer"
        user_id = db.execute(
            "INSERT INTO users(username,display_name,role,password,donor_id,email,full_name) VALUES (?,?,?,?,?,?,?)",
            (email, full_name, role, hash_password(data.password), donor_id,email,full_name),
        ).lastrowid
        db.commit()
    return {"message": "Đăng ký tài khoản thành công", "user_id": user_id, "role": role}


@app.post("/api/login")
@app.post("/api/auth/login")
def login(data: Login) -> dict[str, object]:
    with connect() as db:
        row = db.execute("SELECT * FROM users WHERE username=?", (data.email.strip().lower(),)).fetchone()
    valid = bool(row and verify_password(data.password, row["password"]))
    if not valid:
        raise HTTPException(401, "Email hoặc mật khẩu không chính xác")
    if row["status"] == "locked":
        raise HTTPException(403, "Tài khoản đã bị khóa")
    token = secrets.token_urlsafe(32)
    user = {"id": str(row["id"]), "email": row["username"], "display_name": row["display_name"], "role": row["role"], "donor_id": str(row["donor_id"] or ""), "status": row["status"]}
    SESSIONS[token] = user
    return {"token": token, "user": user}


@app.post("/api/auth/logout")
def logout(_: dict[str, str] = Depends(signed_in), authorization: Annotated[str | None, Header()] = None) -> dict[str, bool]:
    if authorization:
        SESSIONS.pop(authorization.removeprefix("Bearer "), None)
    return {"ok": True}


@app.post("/api/auth/change-password")
def change_password(data: ChangePasswordInput, user: dict[str, str] = Depends(signed_in), authorization: Annotated[str | None, Header()] = None) -> dict[str, bool]:
    if data.new_password != data.confirm_password:
        raise HTTPException(422, "Mật khẩu mới và xác nhận không khớp")
    if data.new_password == data.current_password:
        raise HTTPException(400, "Mật khẩu mới phải khác mật khẩu hiện tại")
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT password FROM users WHERE id=?", (int(user["id"]),)).fetchone()
        if row is None or not verify_password(data.current_password, row["password"]):
            db.rollback()
            raise HTTPException(400, "Mật khẩu hiện tại không chính xác")
        db.execute("UPDATE users SET password=? WHERE id=?", (hash_password(data.new_password), int(user["id"])))
        db.commit()
    current_token = authorization.removeprefix("Bearer ") if authorization else ""
    for token, session_user in list(SESSIONS.items()):
        if session_user["id"] == user["id"] and token != current_token:
            SESSIONS.pop(token, None)
    return {"ok": True}


@app.get("/api/dashboard")
def dashboard(user: dict[str, str] = Depends(roles("admin", "coordinator"))) -> dict[str, object]:
    with connect() as db:
        stats = {"total_donors":db.execute("SELECT COUNT(*) FROM donors").fetchone()[0],"registrations":db.execute("SELECT COUNT(*) FROM appointments WHERE status!='Đã hủy'").fetchone()[0],"attended":db.execute("SELECT COUNT(*) FROM appointments WHERE status='Đã tham gia'").fetchone()[0],"upcoming_campaigns":db.execute("SELECT COUNT(*) FROM campaigns WHERE campaign_date>=? AND status='Đang mở'",(date.today().isoformat(),)).fetchone()[0]}
        groups = [dict(r) for r in db.execute("SELECT blood_group name,COUNT(*) value FROM donors GROUP BY blood_group ORDER BY value DESC")]
        recent_query="SELECT a.id,d.full_name,d.blood_group,a.status,s.start_at,c.title campaign_title FROM appointments a JOIN donors d ON d.id=a.donor_id JOIN slots s ON s.id=a.slot_id JOIN campaigns c ON c.id=s.campaign_id"
        if user["role"]=="volunteer":
            recent_query+=" WHERE a.donor_id=? ORDER BY a.created_at DESC LIMIT 6"
            recent=[dict(r) for r in db.execute(recent_query,(int(user["donor_id"]),))] if user["donor_id"] else []
        else:
            recent=[dict(r) for r in db.execute(recent_query+" ORDER BY a.created_at DESC LIMIT 6")]
        events = [campaign_info(db,r[0]) for r in db.execute("SELECT id FROM campaigns ORDER BY campaign_date")]
    return {**stats,"blood_groups":groups,"recent":recent,"campaigns":events}


@app.get("/api/donors")
def donors(_: dict[str, str] = Depends(roles("admin", "coordinator"))) -> list[dict[str, object]]:
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT * FROM donors ORDER BY id DESC")]


@app.get("/api/donors/me")
def my_donor(user: dict[str, str] = Depends(signed_in)) -> dict[str, object]:
    if not user["donor_id"]:
        raise HTTPException(404, "Tài khoản chưa liên kết hồ sơ người đăng ký")
    with connect() as db:
        row = db.execute("SELECT * FROM donors WHERE id=?", (int(user["donor_id"]),)).fetchone()
        if row is None:
            raise HTTPException(404, "Không tìm thấy hồ sơ người đăng ký")
        return dict(row)


@app.get("/api/users/me")
def my_account_profile(user: dict[str, str] = Depends(signed_in)) -> dict[str, object]:
    if user["donor_id"]:
        profile = my_donor(user)
        return {**profile, "email": user["email"]}
    with connect() as db:
        row = db.execute("SELECT username,display_name,phone,blood_group,birth_date,address,organization,job_title FROM users WHERE id=?", (int(user["id"]),)).fetchone()
        if row is None:
            raise HTTPException(404, "Không tìm thấy hồ sơ tài khoản")
        return {"full_name": row["display_name"], "email": row["username"], "phone": row["phone"], "blood_group": row["blood_group"], "birth_date": row["birth_date"], "address": row["address"], "organization": row["organization"], "job_title": row["job_title"]}


@app.put("/api/donors/me")
def update_my_donor(data: DonorProfileUpdate, user: dict[str, str] = Depends(signed_in)) -> dict[str, object]:
    if not user["donor_id"]:
        raise HTTPException(404, "Tài khoản chưa liên kết hồ sơ người đăng ký")
    full_name = data.full_name.strip()
    if len(full_name) < 2:
        raise HTTPException(422, "Họ tên cần có ít nhất 2 ký tự")
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        donor_id = int(user["donor_id"])
        if db.execute("SELECT 1 FROM donors WHERE id=?", (donor_id,)).fetchone() is None:
            db.rollback()
            raise HTTPException(404, "Không tìm thấy hồ sơ người đăng ký")
        db.execute("UPDATE donors SET full_name=?,phone=?,blood_group=?,birth_date=?,address=? WHERE id=?", (full_name, data.phone.strip(), data.blood_group, data.birth_date.isoformat() if data.birth_date else None, data.address.strip(), donor_id))
        db.execute("UPDATE users SET display_name=?,full_name=? WHERE id=?", (full_name,full_name,int(user["id"])))
        db.commit()
        return dict(db.execute("SELECT * FROM donors WHERE id=?", (donor_id,)).fetchone())


@app.put("/api/users/me")
def update_my_account_profile(data: DonorProfileUpdate, user: dict[str, str] = Depends(signed_in)) -> dict[str, object]:
    if user["donor_id"]:
        profile = update_my_donor(data, user)
        return {**profile, "email": user["email"]}
    full_name = data.full_name.strip()
    if len(full_name) < 2:
        raise HTTPException(422, "Họ tên cần có ít nhất 2 ký tự")
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        db.execute("UPDATE users SET display_name=?,full_name=?,phone=?,blood_group=?,birth_date=?,address=?,organization=?,job_title=? WHERE id=?", (full_name,full_name,data.phone.strip(), data.blood_group, data.birth_date.isoformat() if data.birth_date else None, data.address.strip(), data.organization.strip(), data.job_title.strip(), int(user["id"])))
        db.commit()
        row = db.execute("SELECT username,display_name,phone,blood_group,birth_date,address,organization,job_title FROM users WHERE id=?", (int(user["id"]),)).fetchone()
        if row is None:
            raise HTTPException(404, "Không tìm thấy hồ sơ tài khoản")
        return {"full_name": row["display_name"], "email": row["username"], "phone": row["phone"], "blood_group": row["blood_group"], "birth_date": row["birth_date"], "address": row["address"], "organization": row["organization"], "job_title": row["job_title"]}


@app.get("/api/coordinators/me")
def coordinator_profile(user: dict[str, str] = Depends(roles("coordinator"))) -> dict[str, object]:
    return my_account_profile(user)


@app.put("/api/coordinators/me")
def update_coordinator_profile(data: CoordinatorProfileUpdate, user: dict[str, str] = Depends(roles("coordinator"))) -> dict[str, object]:
    full_name = data.full_name.strip()
    if len(full_name) < 2:
        raise HTTPException(422, "Họ tên cần có ít nhất 2 ký tự")
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        db.execute("UPDATE users SET display_name=?,full_name=?,phone=?,organization=?,job_title=? WHERE id=? AND role='coordinator'", (full_name,full_name,data.phone.strip(), data.organization.strip(), data.job_title.strip(), int(user["id"])))
        row = db.execute("SELECT username,display_name,phone,organization,job_title FROM users WHERE id=? AND role='coordinator'", (int(user["id"]),)).fetchone()
        if row is None:
            db.rollback()
            raise HTTPException(404, "Không tìm thấy hồ sơ điều phối viên")
        db.commit()
        return {"full_name": row["display_name"], "email": row["username"], "phone": row["phone"], "organization": row["organization"], "job_title": row["job_title"]}


@app.get("/api/admin/users")
def admin_list_users(_:dict[str,str]=Depends(roles("admin")))->list[dict[str,object]]:
    with connect() as db:
        rows=db.execute("SELECT id,email,full_name,role,status,created_at FROM users ORDER BY datetime(created_at) DESC,id DESC").fetchall()
        return [dict(row) for row in rows]


@app.post("/api/admin/users", status_code=201)
def admin_create_user(data: AdminUserCreateInput, _:dict[str,str]=Depends(roles("admin")))->dict[str,object]:
    email=data.email.strip().lower()
    full_name=data.full_name.strip()
    if len(full_name)<2:
        raise HTTPException(422,"Full name must contain at least 2 characters")
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM users WHERE lower(email)=? OR lower(username)=?",(email,email)).fetchone():
            db.rollback()
            raise HTTPException(400,"Email already exists")
        now=db.execute("SELECT CURRENT_TIMESTAMP").fetchone()[0]
        user_id=db.execute("INSERT INTO users(username,display_name,role,password,email,full_name,status,created_at) VALUES (?,?,?,?,?,?,'active',?)",(email,full_name,data.role,hash_password(data.password),email,full_name,now)).lastrowid
        db.commit()
        row=db.execute("SELECT id,email,full_name,role,status,created_at FROM users WHERE id=?",(user_id,)).fetchone()
        return dict(row)


@app.put("/api/admin/users/{user_id}/role")
def admin_update_user_role(user_id:int,data:AdminUserRoleInput,_:dict[str,str]=Depends(roles("admin")))->dict[str,object]:
    with connect() as db:
        changed=db.execute("UPDATE users SET role=? WHERE id=?",(data.role,user_id))
        if not changed.rowcount:
            raise HTTPException(404,"Account not found")
        for session in SESSIONS.values():
            if session["id"]==str(user_id): session["role"]=data.role
        row=db.execute("SELECT id,email,full_name,role,status,created_at FROM users WHERE id=?",(user_id,)).fetchone()
        return dict(row)


@app.put("/api/admin/users/{user_id}/status")
def admin_update_user_status(user_id:int,data:AdminUserStatusInput,admin:dict[str,str]=Depends(roles("admin")))->dict[str,object]:
    if user_id==int(admin["id"]) and data.status=="locked":
        raise HTTPException(400,"You cannot lock your own account")
    with connect() as db:
        changed=db.execute("UPDATE users SET status=? WHERE id=?",(data.status,user_id))
        if not changed.rowcount:
            raise HTTPException(404,"Account not found")
        row=db.execute("SELECT id,email,full_name,role,status,created_at FROM users WHERE id=?",(user_id,)).fetchone()
    if data.status=="locked":
        for token,session in list(SESSIONS.items()):
            if session["id"]==str(user_id): SESSIONS.pop(token,None)
    return dict(row)


@app.delete("/api/admin/users/{user_id}",status_code=204)
def admin_delete_user(user_id:int,admin:dict[str,str]=Depends(roles("admin")))->None:
    if user_id==int(admin["id"]):
        raise HTTPException(400,"You cannot delete your own account")
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        target=db.execute("SELECT role FROM users WHERE id=?",(user_id,)).fetchone()
        if not target:
            db.rollback()
            raise HTTPException(404,"Account not found")
        if target["role"]=="admin" and db.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0]<=1:
            db.rollback()
            raise HTTPException(409,"Cannot delete the last admin account")
        db.execute("DELETE FROM notifications WHERE user_id=?",(user_id,))
        db.execute("DELETE FROM users WHERE id=?",(user_id,))
        db.commit()
    for token,session in list(SESSIONS.items()):
        if session["id"]==str(user_id): SESSIONS.pop(token,None)

@app.post("/api/donors", status_code=201)
def add_donor(data: DonorInput, _: dict[str, str] = Depends(roles("admin","coordinator"))) -> dict[str, object]:
    if data.blood_group not in {"A+","A-","B+","B-","AB+","AB-","O+","O-","Chưa cập nhật"}: raise HTTPException(422,"Nhóm máu không hợp lệ")
    if bool(data.login_email) != bool(data.login_password):
        raise HTTPException(422, "Nhập cả email và mật khẩu để tạo tài khoản")
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            cursor=db.execute("INSERT INTO donors(full_name,phone,email,blood_group) VALUES (?,?,?,?)",(data.full_name.strip(),data.phone.strip(),data.email.strip(),data.blood_group))
            donor_id=cursor.lastrowid
            if data.login_email and data.login_password:
                account_email=data.login_email.strip().lower()
                account_name=data.full_name.strip()
                db.execute("INSERT INTO users(username,display_name,role,password,donor_id,email,full_name) VALUES (?,?, 'volunteer', ?, ?, ?, ?)",(account_email,account_name,hash_password(data.login_password),donor_id,account_email,account_name))
            result=dict(db.execute("SELECT * FROM donors WHERE id=?",(donor_id,)).fetchone())
            db.commit()
            return {**result, "account_created": bool(data.login_email)}
        except sqlite3.IntegrityError as error:
            db.rollback()
            raise HTTPException(409, "Email đã tồn tại hoặc dữ liệu không hợp lệ") from error


@app.get("/api/campaigns")
def campaigns(_: dict[str, str] = Depends(signed_in)) -> list[dict[str, object]]:
    with connect() as db: return [campaign_info(db,r[0]) for r in db.execute("SELECT id FROM campaigns ORDER BY campaign_date")]


@app.post("/api/campaigns", status_code=201)
def add_campaign(data: CampaignInput, _: dict[str, str] = Depends(roles("admin","coordinator"))) -> dict[str, object]:
    slots=slot_values(data)
    start_time=str(slots[0]["start_time"])
    end_time=str(slots[-1]["end_time"])
    with connect() as db:
        cid=db.execute("INSERT INTO campaigns(title,venue,campaign_date,start_time,end_time,description,status) VALUES (?,?,?,?,?,?,?)",(data.title.strip(),data.venue.strip(),data.campaign_date.isoformat(),start_time,end_time,data.description.strip(),data.status)).lastrowid
        for slot in slots:
            db.execute("INSERT INTO slots(campaign_id,start_at,end_at,capacity) VALUES (?,?,?,?)",(cid,f"{data.campaign_date}T{slot['start_time']}",f"{data.campaign_date}T{slot['end_time']}",slot["capacity"]))
        return campaign_info(db,cid)


def notify_campaign_users(db:sqlite3.Connection,campaign_id:int,title:str,message:str)->None:
    db.execute("""INSERT INTO notifications(user_id,donor_id,campaign_id,title,message,type,is_read)
        SELECT DISTINCT u.id,a.donor_id,?,?,?,'system',0
        FROM appointments a JOIN slots s ON s.id=a.slot_id JOIN users u ON u.donor_id=a.donor_id
        WHERE s.campaign_id=? AND a.status='Đã đăng ký'""",(campaign_id,title,message,campaign_id))


@app.patch("/api/campaigns/{cid}/status")
def campaign_status(cid:int,data:CampaignStatusInput,_:dict[str,str]=Depends(roles("admin","coordinator")))->dict[str,object]:
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        event=db.execute("SELECT title,campaign_date,venue,status FROM campaigns WHERE id=?",(cid,)).fetchone()
        if event is None: raise HTTPException(404,"Không tìm thấy chiến dịch")
        db.execute("UPDATE campaigns SET status=? WHERE id=?",(data.status,cid))
        if event["status"]!=data.status:
            message=f"Trạng thái chiến dịch '{event['title']}' đã thay đổi thành {data.status}. Ngày {event['campaign_date']} tại {event['venue']}."
            notify_campaign_users(db,cid,"Cập nhật chiến dịch",message)
        result=campaign_info(db,cid)
        db.commit()
        return result


@app.put("/api/campaigns/{cid}")
def edit_campaign(cid:int,data:CampaignInput,_:dict[str,str]=Depends(roles("admin","coordinator")))->dict[str,object]:
    slots=slot_values(data)
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        event=db.execute("SELECT id,title,venue,campaign_date,status FROM campaigns WHERE id=?",(cid,)).fetchone()
        if event is None:
            db.rollback()
            raise HTTPException(404,"Không tìm thấy chiến dịch")
        existing={row["id"]:row for row in db.execute("SELECT * FROM slots WHERE campaign_id=?",(cid,))}
        slots_changed=len(slots)!=len(existing) or any(slot["id"] is None or slot["id"] not in existing or slot["start_time"]!=existing[slot["id"]]["start_at"][11:] or slot["end_time"]!=existing[slot["id"]]["end_at"][11:] for slot in slots)
        for slot_id in existing:
            db.execute("UPDATE slots SET start_at=?,end_at=? WHERE id=?",(f"__editing_{cid}_{slot_id}_start__",f"__editing_{cid}_{slot_id}_end__",slot_id))
        kept_ids=set()
        for slot in slots:
            slot_id=slot["id"]
            if slot_id is not None and slot_id not in existing:
                db.rollback()
                raise HTTPException(422,"Khung giờ không thuộc chiến dịch này")
            if slot_id is not None:
                booked=db.execute("SELECT COUNT(*) FROM appointments WHERE slot_id=? AND status!='Đã hủy'",(slot_id,)).fetchone()[0]
                previous=existing[slot_id]
                if booked and (data.campaign_date.isoformat()!=previous["start_at"][:10] or slot["start_time"]!=previous["start_at"][11:] or slot["end_time"]!=previous["end_at"][11:]):
                    db.rollback()
                    raise HTTPException(409,"Không thể đổi ngày hoặc giờ của khung đã có lượt hẹn")
                if booked>slot["capacity"]:
                    db.rollback()
                    raise HTTPException(409,"Sức chứa mới thấp hơn số lượt đã đặt")
                kept_ids.add(slot_id)
                db.execute("UPDATE slots SET start_at=?,end_at=?,capacity=? WHERE id=?",(f"{data.campaign_date}T{slot['start_time']}",f"{data.campaign_date}T{slot['end_time']}",slot["capacity"],slot_id))
            else:
                db.execute("INSERT INTO slots(campaign_id,start_at,end_at,capacity) VALUES (?,?,?,?)",(cid,f"{data.campaign_date}T{slot['start_time']}",f"{data.campaign_date}T{slot['end_time']}",slot["capacity"]))
        for slot_id in set(existing)-kept_ids:
            booked=db.execute("SELECT COUNT(*) FROM appointments WHERE slot_id=?",(slot_id,)).fetchone()[0]
            if booked:
                db.rollback()
                raise HTTPException(409,"Không thể xóa khung giờ đang có lượt hẹn")
            db.execute("DELETE FROM slots WHERE id=?",(slot_id,))
        start_time=str(slots[0]["start_time"])
        end_time=str(slots[-1]["end_time"])
        db.execute("UPDATE campaigns SET title=?,venue=?,campaign_date=?,start_time=?,end_time=?,description=?,status=? WHERE id=?",(data.title.strip(),data.venue.strip(),data.campaign_date.isoformat(),start_time,end_time,data.description.strip(),data.status,cid))
        changes=[]
        if event["title"]!=data.title.strip(): changes.append("tên chiến dịch đã thay đổi.")
        if event["venue"]!=data.venue.strip(): changes.append("địa điểm hiến máu đã thay đổi.")
        if event["campaign_date"]!=data.campaign_date.isoformat(): changes.append("ngày tổ chức đã thay đổi.")
        if event["status"]!=data.status: changes.append(f"trạng thái hiện tại là {data.status}.")
        if slots_changed: changes.append("các khung giờ đăng ký đã được cập nhật.")
        if changes:
            message=f"Chiến dịch '{data.title.strip()}' có cập nhật: {' '.join(changes)} Ngày {data.campaign_date.isoformat()}, địa điểm {data.venue.strip()}, khung giờ {start_time}–{end_time}."
            notify_campaign_users(db,cid,"Cập nhật lịch hiến máu",message)
        db.commit()
        return campaign_info(db,cid)


@app.delete("/api/campaigns/{cid}",status_code=204)
def delete_campaign(cid:int,_:dict[str,str]=Depends(roles("admin","coordinator")))->None:
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM campaigns WHERE id=?",(cid,)).fetchone() is None:
            db.rollback()
            raise HTTPException(404,"Không tìm thấy chiến dịch")
        linked=db.execute("SELECT 1 FROM slots s JOIN appointments a ON a.slot_id=s.id WHERE s.campaign_id=? UNION ALL SELECT 1 FROM notifications WHERE campaign_id=? LIMIT 1",(cid,cid)).fetchone()
        if linked:
            db.rollback()
            raise HTTPException(409,"Không thể xóa chiến dịch đã có lượt hẹn hoặc thông báo")
        db.execute("DELETE FROM slots WHERE campaign_id=?",(cid,))
        db.execute("DELETE FROM campaigns WHERE id=?",(cid,))
        db.commit()


@app.get("/api/appointments")
def appointments(user:dict[str,str]=Depends(signed_in))->list[dict[str,object]]:
    query="SELECT a.id,a.donor_id,d.full_name,d.phone,d.blood_group,a.slot_id,a.status,s.start_at,c.title campaign_title,c.venue FROM appointments a JOIN donors d ON d.id=a.donor_id JOIN slots s ON s.id=a.slot_id JOIN campaigns c ON c.id=s.campaign_id"
    with connect() as db:
        if user["role"]=="volunteer":
            if not user["donor_id"]: return []
            return [dict(r) for r in db.execute(query+" WHERE a.donor_id=? ORDER BY s.start_at DESC",(int(user["donor_id"]),))]
        return [dict(r) for r in db.execute(query+" ORDER BY s.start_at DESC")]


@app.post("/api/appointments",status_code=201)
def reserve(data:AppointmentInput,user:dict[str,str]=Depends(signed_in))->dict[str,object]:
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        slot=db.execute("SELECT s.*,c.status campaign_status FROM slots s JOIN campaigns c ON c.id=s.campaign_id WHERE s.id=?",(data.slot_id,)).fetchone()
        donor=db.execute("SELECT id FROM donors WHERE id=?",(data.donor_id,)).fetchone()
        if not slot or not donor: db.rollback(); raise HTTPException(404,"Không tìm thấy người đăng ký hoặc khung giờ")
        if user["role"]=="volunteer" and user["donor_id"]!=str(data.donor_id): db.rollback(); raise HTTPException(403,"Tình nguyện viên chỉ có thể đăng ký lịch cho hồ sơ của mình")
        if slot["campaign_status"]!="Đang mở": db.rollback(); raise HTTPException(409,"Chiến dịch đã đóng đăng ký")
        conflict=db.execute("SELECT 1 FROM appointments a JOIN slots s ON s.id=a.slot_id WHERE a.donor_id=? AND a.status!='Đã hủy' AND s.start_at<? AND s.end_at>? LIMIT 1",(data.donor_id,slot["end_at"],slot["start_at"])).fetchone()
        if conflict: db.rollback(); raise HTTPException(409,"Người đăng ký đã có lịch trùng khung giờ")
        booked=db.execute("SELECT COUNT(*) FROM appointments WHERE slot_id=? AND status!='Đã hủy'",(data.slot_id,)).fetchone()[0]
        if booked>=slot["capacity"]: db.rollback(); raise HTTPException(409,"Khung giờ đã đủ số lượng")
        aid=db.execute("INSERT INTO appointments(donor_id,slot_id) VALUES (?,?)",(data.donor_id,data.slot_id)).lastrowid
        result=dict(db.execute("SELECT a.id,a.donor_id,d.full_name,a.slot_id,a.status,s.start_at,s.end_at,c.id campaign_id,c.title campaign_title,c.campaign_date,c.venue FROM appointments a JOIN donors d ON d.id=a.donor_id JOIN slots s ON s.id=a.slot_id JOIN campaigns c ON c.id=s.campaign_id WHERE a.id=?",(aid,)).fetchone())
        volunteer_accounts=db.execute("SELECT id FROM users WHERE donor_id=?",(data.donor_id,)).fetchall()
        confirmation=f"Chúc mừng {result['full_name']}! Bạn đã đăng ký thành công lịch hiến máu chiến dịch '{result['campaign_title']}' vào lúc {result['start_at'][11:]}–{result['end_at'][11:]} ngày {result['campaign_date']} tại {result['venue']}. Hãy chú ý nghỉ ngơi và chuẩn bị sức khỏe thật tốt nhé!"
        db.executemany("INSERT INTO notifications(user_id,donor_id,campaign_id,appointment_id,title,message,type,is_read) VALUES (?,?,?,?,?,?, 'system',0)",[(account["id"],data.donor_id,result["campaign_id"],aid,"Xác nhận đăng ký hiến máu thành công",confirmation) for account in volunteer_accounts])
        coordinators=db.execute("SELECT id FROM users WHERE role='coordinator'").fetchall()
        coordinator_message=f"{result['full_name']} vừa đăng ký hiến máu chiến dịch '{result['campaign_title']}' vào lúc {result['start_at'][11:]}–{result['end_at'][11:]} ngày {result['campaign_date']} tại {result['venue']}."
        db.executemany("INSERT INTO notifications(user_id,donor_id,campaign_id,appointment_id,title,message,type,is_read) VALUES (?,?,?,?,?,?, 'system',0)",[(coordinator["id"],data.donor_id,result["campaign_id"],aid,"Có lượt đăng ký hiến máu mới",coordinator_message) for coordinator in coordinators])
        db.commit(); return result


@app.patch("/api/appointments/{aid}")
def update_appointment(aid:int,data:StatusInput,_:dict[str,str]=Depends(roles("admin","coordinator")))->dict[str,object]:
    with connect() as db:
        changed=db.execute("UPDATE appointments SET status=? WHERE id=?",(data.status,aid))
        if not changed.rowcount: raise HTTPException(404,"Không tìm thấy lượt đăng ký")
        return dict(db.execute("SELECT * FROM appointments WHERE id=?",(aid,)).fetchone())


def ai_call(system:str,prompt:str)->str|None:
    key=os.getenv("OPENAI_API_KEY")
    if not key: return None
    req=urllib.request.Request(os.getenv("OPENAI_BASE_URL","https://api.openai.com/v1/chat/completions"),data=json.dumps({"model":os.getenv("OPENAI_MODEL","gpt-4o-mini"),"messages":[{"role":"system","content":system},{"role":"user","content":prompt}],"temperature":0.4},ensure_ascii=False).encode("utf-8"),headers={"Authorization":f"Bearer {key}","Content-Type":"application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req,timeout=20) as res: return json.loads(res.read())["choices"][0]["message"]["content"].strip()
    except (urllib.error.URLError,TimeoutError,KeyError,IndexError,json.JSONDecodeError): return None


@app.post("/api/chat")
@app.post("/api/ai/answer", include_in_schema=False)
def chat(data:ChatInput,_:dict[str,str]=Depends(signed_in))->JSONResponse:
    question=data.question.strip()
    if not question: raise HTTPException(422,"Vui lòng nhập câu hỏi")
    medical=("đủ điều kiện","bệnh","thuốc","sức khỏe","sức khoẻ","cân nặng","huyết áp","mang thai","cá nhân","đang đau","dị ứng","chẩn đoán")
    if any(word in question.lower() for word in medical):
        return ai_json({"text":"Mình không thể đánh giá sức khỏe hoặc điều kiện hiến máu cá nhân. Nhân viên y tế sẽ tư vấn và kiểm tra trực tiếp tại điểm hiến.","mode":"Chuyển nhân viên y tế"})
    with connect() as db: docs=[dict(r) for r in db.execute("SELECT title,content FROM procedures")]
    words=set(re.findall(r"[^\W_]+",question.lower()))-{"hiến","máu","khi"}
    ranked=sorted(docs,key=lambda doc:len(words & set(re.findall(r"[^\W_]+",doc["title"].lower()))),reverse=True)
    retrieved=[doc for doc in ranked if words & set(re.findall(r"[^\W_]+",doc["title"].lower()))][:2]
    if not retrieved:
        return ai_json({"text":"Mình chưa tìm thấy thông tin này trong tài liệu được duyệt. Vui lòng liên hệ điều phối viên hoặc nhân viên y tế tại điểm hiến.","mode":"Không tìm thấy tài liệu phù hợp"})
    source="\n".join(f"{d['title']}: {d['content']}" for d in retrieved)
    text=ai_call("Chỉ trả lời dựa trên các tài liệu được duyệt và truy xuất bên dưới. Không tư vấn, chẩn đoán hay đánh giá sức khỏe cá nhân. Nếu thiếu thông tin, hướng người hỏi đến nhân viên y tế.\n"+source,question)
    used_ai=bool(text)
    if not text:
        text=retrieved[0]["content"]
    return ai_json({"text":text,"mode":"AI" if used_ai else "Tài liệu quy trình"})


@app.post("/api/ai/monthly-report")
def monthly_campaign_report(data:MonthlyReportInput,_:dict[str,str]=Depends(roles("admin","coordinator")))->JSONResponse:
    registered_status="\u0110\u00e3 \u0111\u0103ng k\u00fd"
    attended_status="\u0110\u00e3 tham gia"
    with connect() as db:
        campaigns=db.execute("""SELECT c.id,c.title,c.campaign_date,
            (SELECT COUNT(*) FROM appointments a JOIN slots sx ON sx.id=a.slot_id WHERE sx.campaign_id=c.id AND a.status IN (?,?)) registrations,
            (SELECT COALESCE(SUM(sx.capacity),0) FROM slots sx WHERE sx.campaign_id=c.id) target
            FROM campaigns c WHERE strftime('%m',c.campaign_date)=? AND strftime('%Y',c.campaign_date)=?
            ORDER BY c.campaign_date,c.id""",(registered_status,attended_status,f"{data.month:02d}",str(data.year))).fetchall()
        peak=db.execute("""SELECT substr(s.start_at,12,5) start_time,COUNT(a.id) registrations
            FROM campaigns c JOIN slots s ON s.campaign_id=c.id JOIN appointments a ON a.slot_id=s.id
            WHERE strftime('%m',c.campaign_date)=? AND strftime('%Y',c.campaign_date)=?
            AND a.status IN (?,?) GROUP BY s.start_at ORDER BY registrations DESC,s.start_at LIMIT 1""",(f"{data.month:02d}",str(data.year),registered_status,attended_status)).fetchone()
    count=len(campaigns)
    registrations=sum(int(row["registrations"]) for row in campaigns)
    target=sum(int(row["target"]) for row in campaigns)
    rate=round(registrations*100/target,1) if target else 0.0
    summary={"campaign_count":count,"registrations":registrations,"completion_rate":rate}
    facts={"month":data.month,"year":data.year,"summary":summary,"campaigns":[dict(row) for row in campaigns],"peak_start_time":peak["start_time"] if peak else None}
    prompt="Write a concise Vietnamese campaign performance report based only on these figures: "+json.dumps(facts,ensure_ascii=False)
    report=ai_call("Summarize blood donation campaign statistics without inventing facts.",prompt)
    used_ai=bool(report)
    report=report or f"Trong tháng {data.month}/{data.year} có {count} chiến dịch, {registrations} lượt đăng ký và tỷ lệ hoàn thành chỉ tiêu {rate:.1f}%."
    if peak and not used_ai: report+=f" Khung giờ có nhiều đăng ký nhất bắt đầu lúc {peak['start_time']}."
    return ai_json({"month":data.month,"year":data.year,"summary":summary,"report":report,"mode":"AI" if used_ai else "Mẫu dự phòng"})


@app.post("/api/ai/yearly-report")
def yearly_campaign_report(data:YearlyReportInput,_:dict[str,str]=Depends(roles("admin","coordinator")))->JSONResponse:
    registered_status="\u0110\u00e3 \u0111\u0103ng k\u00fd"
    attended_status="\u0110\u00e3 tham gia"
    with connect() as db:
        campaigns=db.execute("""SELECT c.id,c.title,c.campaign_date,
            (SELECT COUNT(*) FROM appointments a JOIN slots s ON s.id=a.slot_id WHERE s.campaign_id=c.id AND a.status IN (?,?)) registrations,
            (SELECT COALESCE(SUM(s.capacity),0) FROM slots s WHERE s.campaign_id=c.id) target
            FROM campaigns c WHERE strftime('%Y',c.campaign_date)=?
            ORDER BY c.campaign_date,c.id""",(registered_status,attended_status,str(data.year))).fetchall()
    monthly=[{"month":month,"campaign_count":0,"registrations":0,"completion_rate":0.0,"target":0} for month in range(1,13)]
    total_campaigns=0
    total_registrations=0
    campaign_rates=[]
    for campaign in campaigns:
        month=int(campaign["campaign_date"][5:7])
        registrations=int(campaign["registrations"])
        target=int(campaign["target"])
        rate=round(registrations*100/target,1) if target else 0.0
        total_campaigns+=1
        total_registrations+=registrations
        campaign_rates.append(rate)
        monthly[month-1]["campaign_count"]+=1
        monthly[month-1]["registrations"]+=registrations
        monthly[month-1]["target"]+=target
    for item in monthly:
        item["completion_rate"]=round(item["registrations"]*100/item["target"],1) if item["target"] else 0.0
    average_rate=round(sum(campaign_rates)/len(campaign_rates),1) if campaign_rates else 0.0
    summary={"campaign_count":total_campaigns,"registrations":total_registrations,"average_completion_rate":average_rate}
    facts={"year":data.year,"summary":summary,"monthly":monthly}
    report=ai_call("Analyze this annual blood donation campaign data in Vietnamese. Describe trends only when supported by the monthly figures; do not invent facts or give medical advice.",json.dumps(facts,ensure_ascii=False))
    used_ai=bool(report)
    report=report or f"Năm {data.year} có {total_campaigns} chiến dịch và {total_registrations} lượt đăng ký. Tỷ lệ hoàn thành trung bình theo chiến dịch là {average_rate:.1f}%."
    return ai_json({"year":data.year,"summary":summary,"monthly":monthly,"report":report,"mode":"AI" if used_ai else "Mẫu dự phòng"})


@app.post("/api/ai/campaign-summary")
@app.post("/api/ai/summarize-campaign", include_in_schema=False)
def campaign_summary(data:CampaignSummaryInput,_:dict[str,str]=Depends(roles("admin","coordinator")))->JSONResponse:
    registered_status="\u0110\u00e3 \u0111\u0103ng k\u00fd"
    attended_status="\u0110\u00e3 tham gia"
    with connect() as db:
        campaign=db.execute("""SELECT c.id,c.title,c.venue,c.campaign_date,c.status,
            (SELECT COALESCE(SUM(s.capacity),0) FROM slots s WHERE s.campaign_id=c.id) target,
            (SELECT COUNT(*) FROM appointments a JOIN slots s ON s.id=a.slot_id WHERE s.campaign_id=c.id AND a.status IN (?,?)) registrations,
            (SELECT COUNT(*) FROM appointments a JOIN slots s ON s.id=a.slot_id WHERE s.campaign_id=c.id AND a.status=?) attended
            FROM campaigns c WHERE c.id=?""",(registered_status,attended_status,attended_status,data.campaign_id)).fetchone()
    if campaign is None:
        raise HTTPException(404,"Không tìm thấy chiến dịch")
    facts={key:campaign[key] for key in ("title","venue","campaign_date","status","target","registrations","attended")}
    facts["completion_rate"]=round(int(campaign["registrations"])*100/int(campaign["target"]),1) if campaign["target"] else 0.0
    summary=ai_call("Summarize blood donation campaign registration statistics in concise Vietnamese. Use only provided facts; do not invent details or give medical advice.",json.dumps(facts,ensure_ascii=False))
    used_ai=bool(summary)
    summary=summary or (f"Chiến dịch {campaign['title']} có {facts['registrations']} lượt đăng ký trên {facts['target']} chỉ tiêu "
        f"({facts['completion_rate']}%); đã ghi nhận {facts['attended']} lượt tham gia. Trạng thái: {campaign['status']}.")
    return ai_json({"campaign_id":campaign["id"],"summary":summary,"statistics":facts,"mode":"AI" if used_ai else "Mẫu dự phòng"})


@app.post("/api/notifications/send")
def send_reminders(campaign_id:int,message:str|None=None,_:dict[str,str]=Depends(roles("admin","coordinator")))->dict[str,object]:
    with connect() as db:
        event=db.execute("SELECT title,campaign_date,venue FROM campaigns WHERE id=?",(campaign_id,)).fetchone()
        if not event: raise HTTPException(404,"Không tìm thấy chiến dịch")
        rows=db.execute("SELECT DISTINCT u.id user_id,a.donor_id FROM appointments a JOIN slots s ON s.id=a.slot_id JOIN users u ON u.donor_id=a.donor_id WHERE s.campaign_id=? AND a.status='Đã đăng ký' AND NOT EXISTS(SELECT 1 FROM notifications n WHERE n.donor_id=a.donor_id AND n.campaign_id=s.campaign_id AND n.type='system' AND n.title=?)",(campaign_id,event["title"])).fetchall()
        custom_message=message.strip() if message and message.strip() else None
        generated_message=ai_call("Viết lời nhắc lịch hiến máu thân thiện, ngắn gọn và chính xác; không đưa lời khuyên y khoa.",f"Chiến dịch {event['title']}, ngày {event['campaign_date']}, địa điểm {event['venue']}.") if rows and not custom_message else None
        used_ai=bool(generated_message)
        message=custom_message or generated_message or f"Nhắc lịch hiến máu: {event['title']} ngày {event['campaign_date']}. Hẹn gặp bạn tại {event['venue']}!"
        db.executemany("INSERT INTO notifications(user_id,donor_id,campaign_id,title,message,type,is_read) VALUES (?,?,?,?,?,'system',0)",[(r["user_id"],r["donor_id"],campaign_id,event["title"],message) for r in rows])
    return {"sent":len(rows),"channel":"Demo: ghi nhận thông báo, chưa gửi SMS/email","mode":"AI" if used_ai else "Mẫu dự phòng"}


@app.post("/api/reminders")
def create_reminders(data:ReminderInput,user:dict[str,str]=Depends(roles("admin","coordinator")))->dict[str,object]:
    return send_reminders(data.campaign_id,data.message,user)

@app.get("/api/notifications")
def notifications(user:dict[str,str]=Depends(signed_in))->list[dict[str,object]]:
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        if user["donor_id"]:
            upcoming=db.execute("""SELECT a.id appointment_id,a.donor_id,s.campaign_id,c.title campaign_title,c.venue,s.start_at,s.end_at
                FROM appointments a JOIN slots s ON s.id=a.slot_id JOIN campaigns c ON c.id=s.campaign_id
                WHERE a.donor_id=? AND a.status='Đã đăng ký'
                  AND datetime(s.start_at) BETWEEN datetime('now','+24 hours') AND datetime('now','+48 hours')
                  AND NOT EXISTS(SELECT 1 FROM notifications n WHERE n.user_id=? AND n.appointment_id=a.id AND n.type='reminder')""",(int(user["donor_id"]),int(user["id"]))).fetchall()
            for appointment in upcoming:
                message=f"Bạn có lịch hiến máu {appointment['campaign_title']} vào {appointment['start_at']}. Khung giờ {appointment['start_at'][11:]}–{appointment['end_at'][11:]}. Địa điểm: {appointment['venue']}."
                db.execute("INSERT OR IGNORE INTO notifications(user_id,donor_id,campaign_id,appointment_id,title,message,type,is_read) VALUES (?,?,?,?,?,?,'reminder',0)",(int(user["id"]),appointment["donor_id"],appointment["campaign_id"],appointment["appointment_id"],"Lịch hiến máu sắp tới",message))
        rows=db.execute("SELECT id,user_id,title,message,type,is_read,created_at FROM notifications WHERE user_id=? ORDER BY datetime(created_at) DESC,id DESC",(int(user["id"]),)).fetchall()
        db.commit()
        return [dict(row) for row in rows]


@app.put("/api/notifications/read-all")
def read_all_notifications(user:dict[str,str]=Depends(signed_in))->dict[str,int]:
    with connect() as db:
        updated=db.execute("UPDATE notifications SET is_read=1 WHERE user_id=? AND is_read=0",(int(user["id"]),))
        return {"updated":updated.rowcount}


@app.put("/api/notifications/{notification_id}/read")
def read_notification(notification_id:int,user:dict[str,str]=Depends(signed_in))->dict[str,bool]:
    with connect() as db:
        updated=db.execute("UPDATE notifications SET is_read=1 WHERE id=? AND user_id=?",(notification_id,int(user["id"])))
        if not updated.rowcount:
            raise HTTPException(404,"Không tìm thấy thông báo")
        return {"ok":True}


@app.get("/api/procedures")
def procedures(_:dict[str,str]=Depends(signed_in))->list[dict[str,object]]:
    with connect() as db: return [dict(r) for r in db.execute("SELECT title,content FROM procedures ORDER BY id")]
