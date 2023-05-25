from datetime import datetime
from typing import Optional

from fastapi.encoders import jsonable_encoder  # type: ignore
from sqlalchemy import select  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore

from app.crud.base import CRUDBase
from app.models import CharityProject
from app.services.donation import (
    get_donation_fully_invested_false_objects
)


class CRUDCharityProject(CRUDBase):

    async def create(
            self,
            obj_in,
            session: AsyncSession,
    ):
        obj_in_data = obj_in.dict(exclude_unset=True)

        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)

        donations = await get_donation_fully_invested_false_objects(session)
        donations = donations.scalars().all()

        if donations:
            right_amount = db_obj.full_amount
            for donation in donations:
                if right_amount <= 0:
                    break

                to_add = min(
                    donation.full_amount - donation.invested_amount, right_amount)

                if to_add >= right_amount:
                    to_add = right_amount

                    donation.invested_amount += to_add
                    db_obj.invested_amount += to_add
                    db_obj.fully_invested = True
                    db_obj.close_date = datetime.utcnow()
                    right_amount -= to_add

                else:
                    donation.invested_amount += to_add
                    donation.fully_invested = True
                    donation.close_date = datetime.utcnow()
                    db_obj.invested_amount += to_add
                    right_amount -= to_add

                session.add(donation)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession,
    ):
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_project_id_by_name(
            self,
            project_name: str,
            session: AsyncSession,
    ) -> Optional[int]:
        project = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        project = project.scalar_one_or_none()
        return project


charity_project_crud = CRUDCharityProject(CharityProject)
