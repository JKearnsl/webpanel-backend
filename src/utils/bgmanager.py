from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tzlocal import get_localzone


class BGManager:
    """
    Менеджер фоновых задач

    """

    def __init__(self):
        self._scheduler = AsyncIOScheduler(timezone=str(get_localzone()))

    def add_job(self, func, trigger: str = None, **kwargs) -> str:
        """
        Добавление задачи в планировщик

        :param func: функция
        :param trigger: триггер
        :param kwargs:

        Пример:
            `bg_manager.add_job(renewal_requests, "cron", hour=4, minute=20, args=(async_session,))`
        """
        job = self._scheduler.add_job(func, trigger, **kwargs)
        return job.id

    def remove_job(self, job_id) -> None:
        """
        Удаление задачи из планировщика

        :param job_id: идентификатор задачи
        """
        self._scheduler.remove_job(job_id)

    def get_job(self, job_id) -> Job:
        """
        Получение задачи из планировщика

        :param job_id: идентификатор задачи
        """
        return self._scheduler.get_job(job_id)

    def get_jobs(self) -> list[Job]:
        """
        Получение всех задач из планировщика
        """
        return self._scheduler.get_jobs()

    def start(self) -> None:
        """
        Запуск планировщика
        """
        self._scheduler.start()

    def shutdown(self) -> None:
        """
        Остановка планировщика
        """
        self._scheduler.shutdown()
