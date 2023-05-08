from celery import Celery
# noinspection PyUnresolvedReferences
import celeryconfig



#celery_app = Celery("worker", broker="amqp://guest@localhost:5672//")
celery_app = Celery("worker",
                    #broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
                    )
#celery_app.conf.task_routes = {"app.worker.test_celery": "main-queue"}
celery_app.config_from_object("celeryconfig")
