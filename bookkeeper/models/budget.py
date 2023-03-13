from dataclasses import dataclass
from datetime import datetime, timedelta

from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.models.expense import Expense


@dataclass
class Budget:
    """
    Атрибуты класса budget:
    period - название периода: день, неделя или месяц
    limit - максимальное ограничение на затраты за период,
    spent - сумма, потрачнная за период
    """

    period: str
    limit: int = 0
    spent: int = 0
    pk: int = 0

    def __init__(self, period: str, limit: int = 0, spent: int = 0, pk: int = 0):
        if period not in ['Day', 'Week', 'Month']:
            raise ValueError(f'unknown period "{period}"')
        self.period = period
        self.limit = limit
        self.spent = spent
        self.pk = pk

    """
    Метод описывает изменение бюджета при тратах.
    Рассматриваем изменения за день/неделю/месяц.
    """

    def update_spent(self, exp_repo: AbstractRepository[Expense]) -> None:
        date = datetime.now().isoformat()[:10]  # YYYY-MM-DD format
        if self.period == "Day":  # траты за день
            date_mask = f"{date}"
            exps_in_period = exp_repo.get_all_like(like={"expense_date": date_mask})
        elif self.period == "Week":  # траты за неделю
            weekday_now = datetime.now().weekday()
            day_now = datetime.fromisoformat(date)
            first_week_day = day_now - timedelta(days=weekday_now)  # 1й день недели
            exps_in_period = []  # список всех трат за неделю
            for i in range(7):
                weekday = first_week_day + timedelta(days=i)
                date_mask = f"{weekday.isoformat()[:10]}"
                exps_in_period += exp_repo.get_all_like(like={"expense_date": date_mask})
        elif self.period == "Month":  # траты за месяц
            date_mask = f"{date[:7]}-"
            exps_in_period = exp_repo.get_all_like(like={"expense_date": date_mask})
        self.spent = sum([int(exp.amount) for exp in exps_in_period])
