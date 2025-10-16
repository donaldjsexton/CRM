# 🧾 CRM — Django / FastAPI Prototype

A backend-first **CRM** built with **Django** and extending into **FastAPI** for automation and API-driven workflows.
Designed for event and wedding professionals who need structure, not dashboards.

---

## 🧠 Why It Exists
Most CRMs are front-end heavy and logic-light.
This one reverses that: **data integrity first, interface later.**
Every model, view, and signal revolves around traceability — knowing who changed what, when, and why.

---

## ⚙️ Current Features
- Client / Vendor record management
- Lead and quote tracking
- Automated task assignments
- Notes + comment threads with history logging
- Django Admin for internal control

---

## 🧩 Stack
| Layer | Tech |
|-------|------|
| Backend | Django + FastAPI |
| Database | PostgreSQL |
| Realtime | Redis + Daphne (planned) |
| Auth | JWT |
| Storage | Local → Cloudflare R2 (next) |
| Infra | Docker + Nginx |

---

## 🧱 Structure
```
/crm
├── api/
├── models/
├── templates/
├── static/
└── utils/
```

---

## 🛣️ Next Steps
- Merge FastAPI async endpoints with Django Admin
- Add vendor ↔ client chat via Redis pub/sub
- Extend role-based permissions for team hierarchy

---

## 💡 Philosophy
Fewer clicks, more clarity.
If data flows cleanly, the interface can be simple — that’s the thesis behind this build.

---

**Donald Sexton**
[GitHub](https://github.com/donaldjsexton) • [LinkedIn](https://linkedin.com/in/donaldjsexton) • [X](https://x.com/donaldjsexton_)
