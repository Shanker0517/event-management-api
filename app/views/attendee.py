from io import StringIO
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import csv
from app import schema, crud, models
from app.dependency import get_db
from app.auth import get_current_user


class AttendeeView:
    async def register_attendee(
        self, 
        attendee: schema.AttendeeCreate, 
        db: Session = Depends(get_db), 
        user=Depends(get_current_user)
    ):
        db_attendee, error = crud.create_attendee(db, attendee)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return schema.AttendeeResponse.model_validate(db_attendee)

    async def check_in_attendee(
        self, 
        attendee_id: int, 
        db: Session = Depends(get_db), 
        user=Depends(get_current_user)
    ):
        checked_in_attendee = crud.check_in_attendee(db, attendee_id)
        if not checked_in_attendee:
            raise HTTPException(status_code=404, detail="Attendee not found")
        return schema.AttendeeResponse.model_validate(checked_in_attendee)

    async def list_attendees(
        self, 
        event_id: int, 
        check_in_status: Optional[bool] = None,
        db: Session = Depends(get_db)
    ):
        attendees = crud.get_attendees(db, event_id)
        
        if check_in_status is not None:
            attendees = [att for att in attendees if att.check_in_status == check_in_status]

        if not attendees:
            raise HTTPException(status_code=404, detail="No attendees found")

        return [schema.AttendeeResponse.model_validate(att) for att in attendees]

    async def bulk_check_in(
        self, 
        file: UploadFile = File(...), 
        db: Session = Depends(get_db), 
        user=Depends(get_current_user)
    ):
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="No file was uploaded")

        # Ensure it's a CSV file
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")

        # Read the file content and decode it
        content = await file.read()
        csv_reader = csv.reader(content.decode("utf-8-sig").splitlines())
        
        attendee_ids = []
        for row in csv_reader:
            if row:
                attendee_id = row[0].strip()  # Remove extra spaces
                if attendee_id.isdigit():
                    attendee_ids.append(int(attendee_id))  # Convert to integer
        
        if not attendee_ids:
            raise HTTPException(status_code=400, detail="Invalid or empty CSV file")

        updated_attendees = crud.bulk_check_in(db, attendee_ids)

        if not updated_attendees:
            raise HTTPException(status_code=404, detail="No valid attendees found for check-in")

        return [schema.AttendeeResponse.model_validate(att) for att in updated_attendees]