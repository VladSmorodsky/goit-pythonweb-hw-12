from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import ContactCreate, ContactResponse, ContactUpdate
from src.services.contact import ContactService

from src.services.auth import get_current_user
from src.database.models import User

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/contacts/birthdays/upcoming", response_model=list[ContactResponse])
async def get_upcoming_birthdays(
    days: int = Query(7, ge=1, le=365, description="Number of days to look ahead"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get contacts with birthdays in the next N days (default: 7)."""
    service = ContactService(db)
    contacts = await service.get_upcoming_birthdays(current_user, days)
    return contacts


@router.get("/contacts", response_model=list[ContactResponse])
async def get_contacts(
    name: Optional[str] = Query(None, description="Search by name (partial match)"),
    last_name: Optional[str] = Query(None, description="Search by last name (partial match)"),
    email: Optional[str] = Query(None, description="Search by email (partial match)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all contacts with optional search filters."""
    service = ContactService(db)
    contacts = await service.get_all_contacts(current_user, name=name, last_name=last_name, email=email)
    return contacts


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ContactService(db)
    contact = await service.get_contact_by_id(contact_id, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(contact: ContactCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = ContactService(db)
    new_contact = await service.create_contact(contact, current_user)
    return new_contact


@router.put("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, contact: ContactUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = ContactService(db)
    updated_contact = await service.update_contact(contact_id, contact, current_user)
    if updated_contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return updated_contact


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = ContactService(db)
    deleted = await service.delete_contact(contact_id, current_user)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return None
