from datetime import datetime, timedelta

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, user: User, name: str | None = None, last_name: str | None = None, email: str | None = None) -> list[Contact]:
        """Get all contacts with optional search filters."""
        stmt = select(Contact).filter_by(user_id=user.id)

        filters = []
        if name:
            filters.append(Contact.name.ilike(f"%{name}%"))
        if last_name:
            filters.append(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            filters.append(Contact.email.ilike(f"%{email}%"))

        if filters:
            stmt = stmt.where(or_(*filters))

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, contact_id: int, user: User) -> Contact | None:
        """Get a contact by ID."""
        stmt = select(Contact).where(Contact.id == contact_id).filter_by(user_id=user.id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, contact_data: dict, user: User) -> Contact:
        """Create a new contact in the database."""
        contact = Contact(**contact_data, user_id=user.id)
        self.session.add(contact)
        await self.session.commit()
        await self.session.refresh(contact)
        return contact

    async def update(self, contact_id: int, contact_data: dict, user: User) -> Contact | None:
        """Update an existing contact."""
        contact = await self.get_by_id(contact_id, user)
        if contact is None:
            return None

        for key, value in contact_data.items():
            setattr(contact, key, value)

        await self.session.commit()
        await self.session.refresh(contact)
        return contact

    async def delete(self, contact_id: int, user: User) -> bool:
        """Delete a contact by ID. Returns True if deleted, False if not found."""
        contact = await self.get_by_id(contact_id, user)
        if contact is None:
            return False

        await self.session.delete(contact)
        await self.session.commit()
        return True

    async def get_upcoming_birthdays(self, user: User, days: int = 7) -> list[Contact]:
        """Get contacts with birthdays in the next N days."""
        today = datetime.now().date()
        end_date = today + timedelta(days=days)

        stmt = select(Contact).filter_by(user_id=user.id)
        result = await self.session.execute(stmt)
        all_contacts = result.scalars().all()

        upcoming = []
        for contact in all_contacts:
            try:
                # Parse birthday string (format: YYYY-MM-DD)
                bday = datetime.strptime(contact.birthday, "%Y-%m-%d").date()
                # Get birthday this year
                bday_this_year = bday.replace(year=today.year)

                # If birthday already passed this year, check next year
                if bday_this_year < today:
                    bday_this_year = bday.replace(year=today.year + 1)

                # Check if birthday is within the next N days
                if today <= bday_this_year <= end_date:
                    upcoming.append(contact)
            except (ValueError, AttributeError):
                # Skip contacts with invalid birthday format
                continue

        return upcoming
