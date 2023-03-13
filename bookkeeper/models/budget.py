from dataclasses import dataclass
from datetime import datetime, timedelta

from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.models.expense import Expense


@dataclass
class Budget:
    """
    Атрибуты класса budget: 
    period - название периода - день, неделя или месяц 
    limit - максимальное ограничение на затраты за период,
    spent - сумма, потрачнная за период
    """
    period: str
    limit: int
    spent: int = 0
    pk: int = 0
    def __init__(self, limit: int, period: str,
                       spent: int = 0, pk: int = 0):
        if period not in ["day", "week", "month"]:
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
        date = datetime.now().isoformat()[:10] # YYYY-MM-DD format
        if self.period.lower() == "day": #DAY
            date_mask = f"{date}"
            period_exps = exp_repo.get_all_like(like={"expense_date":date_mask})
        elif self.period.lower() == "week": #WEEK
            weekday_now = datetime.now().weekday() 
            day_now = datetime.fromisoformat(date) #текущая дата в удобном формате
            first_week_day = day_now - timedelta(days=weekday_now) #дата 1го дня недели
            exps_in_period = [] #список трат
            for i in range(7):
                weekday = first_week_day + timedelta(days=i)
                date_mask = f"{weekday.isoformat()[:10]}"
                exps_in_period += exp_repo.get_all_like(like={"expense_date":date_mask})
        elif self.period.lower() == "month": #MONTH
            date_mask = f"{date[:7]}-"
            exps_in_period = exp_repo.get_all_like(like={"expense_date":date_mask})
        self.spent = sum([int(exp.amount) for exp in exps_in_period])


