"""
_random_generators.py

Synopsis:
    This file is for automatic testing of randomly generated tasks and sessions.
    This is supposed to be a test file but since we don't have a stable way of testing,
    yet I'm putting it here. In the future this file will be relocated to appropriate
    places.

Author:
    Bruh141
"""

import random
from datetime import timedelta
from task import *


def create_random_tasks(num_tasks: int) -> list[Task]:
    """
    Generate a list of realistic tasks using Faker for more lifelike data.

    Args:
        num_tasks (int): Number of random tasks to generate.

    Returns:
        list[Task]: A list of realistically generated Task objects.
    """
    categories = [None, 1, 2, 3]  # Example categories
    priorities = [1, 2, 3, 4, 5]  # Example priority levels
    task_list = []

    for i in range(num_tasks):
        task = Task(
            id=i + 1,
            title=fake.sentence(nb_words=4).rstrip("."),
            text=fake.text(max_nb_chars=100),
            completed=random.choice([True, False]),
            ongoing=random.choice([True, False]),
            priority=random.choice(priorities),
            category_id=random.choice(categories),
            attempts=random.randint(0, 10),
            time_spent=random.randint(0, 240),
            due_date=(
                fake.date_time_between(start_date="now", end_date="+30d")
                if random.choice([True, False])
                else None
            ),
            is_daily=random.choice([True, False]),
            is_weekly=random.choice([True, False]),
            is_monthly=random.choice([True, False]),
            is_yearly=random.choice([True, False]),
            days_of_week=random.sample(
                [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ],
                k=random.randint(0, 7),
            ),
        )
        task_list.append(task)

    return task_list


def create_random_sessions(num_sessions: int, task_pool: list[Task]) -> list[Session]:
    """
    Generate a list of realistic sessions using a given pool of tasks.

    Args:
        num_sessions (int): Number of random sessions to generate.
        task_pool (list[Task]): A list of tasks to randomly associate with sessions.

    Returns:
        list[Session]: A list of realistically generated Session objects.
    """
    sessions = []

    for i in range(num_sessions):
        num_tasks_in_session = random.randint(1, len(task_pool))
        session_tasks = random.sample(
            [task.id for task in task_pool], k=num_tasks_in_session
        )

        start_time = fake.date_time_between(start_date="-48h", end_date="now")
        end_time = (
            start_time + timedelta(minutes=random.randint(25, 240))
            if random.choice([True, False])
            else None
        )

        session = Session(
            id=i + 1,
            start_time=start_time,
            end_time=end_time,
            tasks=session_tasks,
            completed=random.choice([True, False]),
        )
        sessions.append(session)

    return sessions


if __name__ == "__main__":
    # for testing
    random_tasks = create_random_tasks(5)
    random_sessions = create_random_sessions(3, random_tasks)

    for task in random_tasks:
        print(task)

    for session in random_sessions:
        print(session)
