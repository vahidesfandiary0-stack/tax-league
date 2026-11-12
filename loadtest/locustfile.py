"""
Staging-only synchronized exam load test.

Prepare one distinct DRF token per test account in tokens.csv:
    token
    <token-1>
    <token-2>

Never use production tokens or run against a live competition.
"""
import csv
import os
from queue import Queue, Empty

from locust import HttpUser, between, events, task

TOKENS_FILE = os.getenv("TOKENS_FILE", "tokens.csv")
EXAM_ID = os.getenv("EXAM_ID", "")
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
token_pool = Queue()


@events.test_start.add_listener
def load_tokens(environment, **kwargs):
    if not EXAM_ID:
        raise RuntimeError("Set EXAM_ID to a published staging exam UUID.")
    with open(TOKENS_FILE, newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            token = row.get("token", "").strip()
            if token:
                token_pool.put(token)
    if token_pool.empty():
        raise RuntimeError("tokens.csv contains no usable tokens.")


class ExamParticipant(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.token = None
        try:
            self.token = token_pool.get_nowait()
        except Empty:
            self.environment.runner.quit()
            return
        self.client.headers.update({"Authorization": f"Token {self.token}"})
        self.attempt_id = None

    @task
    def start_synchronized_exam(self):
        if not self.token or self.attempt_id:
            return
        with self.client.post(
            f"{API_PREFIX}/exams/{EXAM_ID}/start/",
            json={},
            name="POST /exams/{id}/start",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"start returned HTTP {response.status_code}")
                return
            try:
                data = response.json()
                self.attempt_id = data["id"]
                questions = data.get("questions", [])
                if not questions:
                    response.failure("exam returned no questions")
                    return
                self.questions = questions
                response.success()
            except (ValueError, KeyError, TypeError):
                response.failure("invalid start response")
                return

        # Spread answer writes slightly; the start burst is the primary synchronized spike.
        for question in self.questions:
            options = question.get("options", [])
            if not options:
                continue
            self.client.post(
                f"{API_PREFIX}/exams/attempts/{self.attempt_id}/answers/",
                json={"question_id": question["id"], "option_id": options[0]["id"]},
                name="POST /exams/attempts/{id}/answers",
            )
