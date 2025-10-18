from fastapi import FastAPI, Request, BackgroundTasks
from pydantic import BaseModel
app = FastAPI()

class TaskIn(BaseModel):
    title: str
    project_id: int
    skills: dict | None = None
    estimate_hours: float | None = 1.0

@app.get('/health')
async def health():
    return {'status': 'ok'}

@app.post('/assignments/simulate')
async def simulate_assignments(tasks: list[dict]):
    from collabmate.backend.ai_task_splitter import fairness_aware_assign
    members = [
        {'id':1, 'skills':{'python':3,'react':1,'ml':0}, 'capacity_hours':8, 'prior_assignments':2},
        {'id':2, 'skills':{'python':1,'react':4,'ml':2}, 'capacity_hours':8, 'prior_assignments':5},
    ]
    assignments = fairness_aware_assign(members, tasks)
    return {'assignments': assignments}

@app.post('/webhook/github')
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    return {'status': 'accepted'}
