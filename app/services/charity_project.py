from sqlalchemy import select  # type: ignore

from app.models import CharityProject


async def get_project_fully_invested_false_objects(session):
    projects = await session.execute(
        select(CharityProject).where(
            CharityProject.fully_invested is not True
        ).order_by(CharityProject.create_date)
    )

    return projects
