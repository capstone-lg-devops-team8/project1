# webOS Subscription Management Dashboard

A web dashboard for managing webOS appliance subscriptions. It lists subscribers, shows each subscriber's appliances, and displays per-device usage with a weekly bar chart.

Team 8 project for the Capstone LG DevOps course. The backend is **FastAPI**, the frontend is plain **HTML/CSS/JavaScript** with **Chart.js**, and the data is in-memory dummy data (no database).

## Getting started

Requires Python 3.10 or newer.

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server (from the project root)
uvicorn app.main:app --reload
```

Then open:

| URL | What it is |
|-----|-----------|
| http://localhost:8000 | Dashboard |
| http://localhost:8000/docs | Interactive API docs (Swagger UI): try every endpoint from the browser |
| http://localhost:8000/health | Health check, returns `{"status": "ok"}` |

## API

All endpoints are under `/api` and return JSON.

| Method | Path | Returns | Errors |
|--------|------|---------|--------|
| GET | `/api/subscribers` | All subscribers | — |
| GET | `/api/subscribers/{userId}/devices` | Devices owned by that subscriber (`[]` if they have none) | `404` if the subscriber does not exist |
| GET | `/api/devices/{deviceId}/usage` | Usage detail for one device, including `weeklyUsageTrend` (Mon–Sun) | `404` if the device does not exist |

Quick check from a terminal (on Windows PowerShell, type `curl.exe`, not `curl`):

```bash
curl http://localhost:8000/api/subscribers              # 5 subscribers
curl http://localhost:8000/api/subscribers/U001/devices # D001, D002
curl http://localhost:8000/api/subscribers/U005/devices # []
curl http://localhost:8000/api/subscribers/U999/devices # 404
curl http://localhost:8000/api/devices/D001/usage       # usage JSON
curl http://localhost:8000/api/devices/D999/usage       # 404
```

The sample data lives in [app/data/dummy_data.py](app/data/dummy_data.py): 5 subscribers (`U001`–`U005`) and 8 devices (`D001`–`D008`). `U005` intentionally has no devices.

## Project structure

```
project1/
├── app/
│   ├── main.py              # FastAPI app: mounts routers, static files, templates
│   ├── api/
│   │   ├── subscribers.py   # /api/subscribers, /api/subscribers/{userId}/devices
│   │   └── devices.py       # /api/devices/{deviceId}/usage
│   ├── data/
│   │   └── dummy_data.py    # subscribers, devices_by_user, usage_by_device
│   ├── static/
│   │   ├── app.js           # Table rendering, search/filter, chart
│   │   └── style.css
│   └── templates/
│       └── index.html       # Dashboard page
├── tests/
│   ├── req1_test_template.py
│   └── reports/             # Generated verification reports
└── requirements.txt
```

## Requirements

| # | Scope | Backend | Frontend (`app.js`) |
|---|-------|---------|---------------------|
| 1 | Subscriber list + search/filter | `GET /api/subscribers` | `fetchSubscribers`, `renderSubscribers` |
| 2 | Device list, usage detail, weekly chart | `GET /api/subscribers/{userId}/devices`, `GET /api/devices/{deviceId}/usage` | `selectSubscriber`, `renderDevices`, `selectDevice`, `renderUsageChart` |
| 3 | Status badge styling | — | `badgeClass` |

## Testing

The test script starts its own server on a free port, runs the checks, and writes a Markdown report:

```bash
python tests/req1_test_template.py
# Report: tests/reports/req1_report_template.md
```

## Team workflow

| Role | Responsibility |
|------|----------------|
| PM | Splits each requirement between FE/BE, manages branches, merges PRs after reviewing the TE report |
| BE | Implements the API endpoints in `app/api/` |
| FE | Implements rendering, search/filter, and the chart in `app/static/app.js` |
| TE | Writes test scenarios, verifies, and writes the report |

1. Branch off `main` and do your work there, never directly on `main`.
2. Commit only the files for your part, with a [Conventional Commits](https://www.conventionalcommits.org/) prefix, e.g. `feat: add devices list and usage APIs`.
3. Push your branch and open a pull request into `main`.
4. The PM merges once the TE's verification report passes.
