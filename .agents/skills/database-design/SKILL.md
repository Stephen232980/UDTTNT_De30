---
name: database-design
description: "Use when designing, reviewing, migrating, or documenting the nine SQLite tables in Mạch Đỏ (users, donors, donation_locations, campaigns, campaign_slots, appointments, notifications, chat_logs, procedures) and ensuring full referential integrity and AI grounding alignment."
---

# Database Design (Kiến trúc & Cơ sở Dữ liệu Mạch Đỏ)

Skill này cung cấp các nguyên tắc cốt lõi, quy chuẩn kỹ thuật và quy trình kiểm soát dữ liệu cho **09 bảng SQLite** của hệ thống Mạch Đỏ, đồng bộ với tài liệu thiết kế cơ sở dữ liệu chuẩn tại [Báo cáo 06 (Screenflow & DB)](file:///C:/Folder/UDTTNT-main/06_GenAI_SoftwareDevelopment_screenflow_db.docx) và skill tổng hợp [`screenflow-db`](file:///C:/Folder/UDTTNT-main/UDTTNT-main/.agents/skills/screenflow-db/SKILL.md).

## Workflow
1. Inspect `initialize_database()`, the actual SQLite file (`data/blood_donation.db`), `database/schema.sql`, foreign-key metadata, unique indexes, and migration code.
2. Treat the live schema as the source of truth. Separate current DDL from recommended improvements; do not silently add constraints or indexes to a supposedly faithful schema artifact.
3. Document all **9 entities and relationships**:
   - `users`: Core authentication, roles (`admin`, `coordinator`, `donor`), account status.
   - `donors`: Medical biological profile, blood type, weight, last donation date, linked 1-1 with `users`.
   - `donation_locations`: Facilities and mobile donation centers.
   - `campaigns`: Donation events created by users/coordinators, located at donation locations.
   - `campaign_slots`: Time slots and capacity control for each campaign.
   - `appointments`: Volunteer booking instances linking donors to specific campaign slots.
   - `notifications`: Multi-channel notifications delivered to users (automated reminder service).
   - `chat_logs`: Audit trail of questions and responses between users and AI assistant.
   - `procedures`: Approved official clinical workflows serving as the strict grounding knowledge base for the AI Chatbot (UC006).
4. Preserve parameterized SQL, `PRAGMA foreign_keys=ON`, transaction boundaries (`BEGIN IMMEDIATE` / `COMMIT`), and compatibility with existing data.
5. For each migration document ordering, rollback/backup strategy, data backfill, and verification queries.

## Constraints and Indexes
- Record primary keys, current `UNIQUE` constraints, foreign keys, nullability, defaults, and `ON DELETE` behavior exactly.
- Note SQLite's automatically generated unique indexes separately from explicit indexes.
- Recommend an index only against a demonstrated query workload; measure before adding it. Add checks for enumerated statuses, positive capacity, and required relationships as proposals unless they exist in runtime DDL.
- Validate with a clean temporary database and with the existing database; never overwrite user data as part of documentation generation.
