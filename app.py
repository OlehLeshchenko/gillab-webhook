from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

GITLAB_TOKEN = os.environ["GITLAB_TOKEN"]
API_URL = "https://gitlab.com/api/v4"

def update_issue(project_id, issue_iid, add=None, remove=None, close=False):
    payload = {}
    if add:
        payload["add_labels"] = add
    if remove:
        payload["remove_labels"] = remove
    if close:
        payload["state_event"] = "close"

    httpx.put(
        f"{API_URL}/projects/{project_id}/issues/{issue_iid}",
        headers={"PRIVATE-TOKEN": GITLAB_TOKEN},
        json=payload
    )

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    event = request.headers.get("X-Gitlab-Event")

    if event == "Merge Request Hook":
        mr = data["object_attributes"]
        project_id = data["project"]["id"]
        issues = data.get("issues", [])

        if not issues:
            return {"status": "no linked issue"}

        issue_iid = issues[0]["iid"]

        if mr["action"] == "open":
            update_issue(project_id, issue_iid, add="Doing", remove="To Do")

        if mr["action"] == "merge":
            update_issue(project_id, issue_iid, remove="Doing", close=True)

        if mr["action"] == "close":
            update_issue(project_id, issue_iid, remove="Doing", close=True)

    return {"status": "ok"}
