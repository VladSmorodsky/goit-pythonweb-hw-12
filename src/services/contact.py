from fastapi import HTTPException, status

from http.client import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repositories.contact import ContactRepository
from src.schemas import ContactCreate, ContactUpdate


class ContactService:
    def __init__(self, session: AsyncSession):
        self.repository = ContactRepository(session)

    async def get_all_contacts(self, user: User, name: str | None = None, last_name: str | None = None, email: str | None = None) -> list[Contact]:
        return await self.repository.get_all(user=user, name=name, last_name=last_name, email=email)

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        return await self.repository.get_by_id(contact_id, user)

    async def create_contact(self, contact_data: ContactCreate, user: User) -> Contact:
        try:
            contact_dict = contact_data.model_dump()
            return await self.repository.create(contact_dict, user)
        except Exception as e:
            await self.repository.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create contact. Please check the provided data.",
            )

    async def update_contact(self, contact_id: int, contact_data: ContactUpdate, user: User) -> Contact | None:
        contact_dict = contact_data.model_dump()
        return await self.repository.update(contact_id, contact_dict, user)

    async def delete_contact(self, contact_id: int, user: User) -> bool:
        return await self.repository.delete(contact_id, user)

    async def get_upcoming_birthdays(self, user: User, days: int = 7) -> list[Contact]:
        return await self.repository.get_upcoming_birthdays(user, days)
