from sqlalchemy import select  # type: ignore

from app.models import Donation


async def get_donation_fully_invested_false_objects(session):
    donations = await session.execute(
        select(Donation).where(
            Donation.fully_invested is not True
        )
    )

    return donations
