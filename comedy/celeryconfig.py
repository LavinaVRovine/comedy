broker_url ="redis://localhost:6379/0"
result_backend="redis://localhost:6379/0"

timezone= "UTC"
beat_schedule= {
    "no-idea": {
        "task": "worker.test_celery",
        "schedule": 5.,
        "args": ("lala",)
    }
}