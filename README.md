# PULSELINK
- A Virtual Health Companion Supporting Users In Their Daily Lives. [URL]()
## Getting Started
### Quick Start
- Terminal A:
```bash
npm run dev
```
- Terminal B:
```bash
source .venv/bin/activate
fastapi dev scriptname.py (tbd)
```
### Initial Setup
- First run the following command to run the app on [http://localhost:3000](http://localhost:3000) in your browser, allowing you to test the application and view code changes live
```
npm run dev
```
- Next for the Backend running on python, you need to create a *Virtual Environment*:
```
python -m venv .venv
source .venv/bin/activate
```
- Then we install backend's FastAPI and any other libraries needed. *note: scripts using fastAPI need to be run using `fastapi dev script.py`*
```
pip install -r requirements.txt
```
- For Database Access and Middleware we use Firebase, both the JavaScript SDK and Python Admin SDK.

## Technology Stack
- *Framework*:
  - `NextJS`
- *Front-end*:
  - `ReactJS`
  - `Material UI`
- *Middle-ware*:
  - `Firebase`
- *Back-end*:
  - `Python FastAPI`
- *DB*:
  - `Firestore`
## Resources
To learn more about Next.js, take a look at the following resources:
- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.