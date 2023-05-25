from datetime import datetime  # type: ignore

from sqlalchemy import select  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore

from app.models import User, Donation
from app.crud.base import CRUDBase
from app.services.charity_project import get_project_fully_invested_false_objects


class CRUDDonation(CRUDBase):

    async def create(
            self,
            obj_in,
            session: AsyncSession,
            user: User
    ):
        obj_in_data = obj_in.dict(exclude_unset=True)

        obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)

        projects = await get_project_fully_invested_false_objects(session)
        projects = projects.scalars().all()

        if projects:
            total_amount = db_obj.full_amount
            for project in projects:
                if total_amount <= 0:
                    break

                to_add = min(total_amount, project.full_amount - project.invested_amount)

                if to_add >= total_amount:
                    to_add = total_amount

                    project.invested_amount += to_add
                    if project.invested_amount == project.full_amount:
                        project.fully_invested = True

                    db_obj.invested_amount += to_add
                    db_obj.fully_invested = True
                    db_obj.close_date = datetime.utcnow()
                    total_amount -= to_add

                else:
                    project.invested_amount += to_add
                    project.fully_invested = True
                    project.close_date = datetime.utcnow()
                    db_obj.invested_amount += to_add
                    total_amount -= to_add

                session.add(project)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_user_donations(
            self,
            session: AsyncSession,
            user: User
    ):
        donations = await session.execute(
            select(Donation).where(
                Donation.user_id == user.id
            )
        )
        return donations.scalars().all()


donation_crud = CRUDDonation(Donation)
