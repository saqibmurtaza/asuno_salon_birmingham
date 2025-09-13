# from fastapi import FastAPI
# from contextlib import asynccontextmanager
# from asuno_salon_birmingham.backend.database import create_db_tables
# from fastapi.middleware.cors import CORSMiddleware
# from asuno_salon_birmingham.backend.models.booking_models import Booking, BookingCreate, BookingOut
# from asuno_salon_birmingham.backend.database import get_db, supabase_public, supabase_admin
# from sqlalchemy.ext.asyncio import AsyncSession
# from fastapi import Depends, HTTPException
# from sqlalchemy import select
# from datetime import datetime, timezone, timedelta
# from asuno_salon_birmingham.backend.utils import get_service_duration, generate_time_slots
# from asuno_salon_birmingham.chainlit_frontend.opening_hours import OPENING_HOURS
# import logging

# # Setup logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("asuna_salon")

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     logger.info("Starting up Asuna Salon backend...")
#     logger.info("CREATING DATABASE TABLES...")
#     await create_db_tables()
#     logger.info("Database tables created successfully.")
    
#     yield
#     logger.info("Shutting down Asuna Salon backend...")

# # FastAPI application
# app = FastAPI(
#     lifespan=lifespan,
#     title="Asuna Salon Backend",
#     version="1.0.0",
# )

# servers=[
#         {
#             "url": "http://localhost:8001",
#             "description": "Local development server",
#         },
#         {
#             "url": "https://your-backend-api.vercel.app",  # Replace with real domain if deployed
#             "description": "Production server",
#         }
#     ]


# origins = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     "https://curated-shop-ruby.vercel.app",
#     "https://curated-shop-australia.vercel.app"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"], 
# )


# @app.get("/")
# async def root():
#     return {"message": "Welcome to Asuna Salon API"}

# # --------- ENDPOINTS ---------

# @app.post("/bookings", response_model=BookingOut)
# async def create_booking(data: BookingCreate):
#     """Create a new booking with a unique reference code."""
    
#     # 1. Fetch existing bookings for the date using the REST API
#     # The 'eq' filter is used for an exact match.
#     # The 'count=exact' parameter tells Supabase to return the total count of rows
#     # without returning the actual data, which is more efficient.
#     response = supabase_admin.from_('bookings').select(
#         '*', count='exact'
#     ).eq('date', str(data.date)).execute()
    
#     # Supabase's Python client returns a "PostgrestResponse" object.
#     # You access the count from its 'count' attribute.
#     bookings_today_count = response.count
    
#     # 2. Generate the unique reference code
#     base_ref = f"ASU-{data.date.strftime('%Y%m%d')}"
#     # The count is 0-indexed, so the suffix starts at 1
#     suffix = bookings_today_count + 1
#     reference = f"{base_ref}-{suffix:03d}"
    
#     # 3. Insert the new booking into the database
#     new_booking_data = data.dict()
#     new_booking_data['reference'] = reference
    
#     # The insert method handles the POST request to the Supabase REST API
#     insert_response = supabase_admin.from_('bookings').insert([new_booking_data]).execute()
    
#     if insert_response.data:
#         # The Supabase client returns a list of inserted objects
#         # We assume one object was inserted
#         new_booking_dict = insert_response.data[0]
#         # We need to parse the dictionary back into our Pydantic model
#         return BookingOut(**new_booking_dict)
#     else:
#         raise HTTPException(
#             status_code=400, 
#             detail="Could not save booking."
#         )


# @app.get("/bookings/available-times/{date}")
# async def get_available_times(date: str, service: str):
#     try:
#         service_minutes = get_service_duration(service)
#         check_date = datetime.strptime(date, "%Y-%m-%d").date()

#         for _ in range(14): # look up to 14 days ahead
#             weekday = check_date.weekday()
#             hours = OPENING_HOURS.get(weekday)
            
#             if not hours:
#                 check_date += timedelta(days=1)
#                 continue

#             all_slots = generate_time_slots(hours["start"], hours["end"], service_minutes)
            
#             # 1. Fetch only the 'time' column for the specified date
#             # The 'eq' filter is used to get exact matches for the date.
#             # Using 'select("time")' is more efficient as it reduces the payload size.
#             response = supabase_admin.from_('bookings').select(
#                 'time'
#             ).eq('date', str(check_date)).execute()
            
#             # The Supabase client returns a list of dictionaries, e.g., [{'time': '10:00:00'}, ...]
#             booked = [t['time'] for t in response.data]
#             available = [t for t in all_slots if t not in booked]

#             if available:
#                 return {"date": str(check_date), "available": available}

#             check_date += timedelta(days=1)

#         return {"date": None, "available": []}
        
#     except Exception as e:
#         # Never leak raw tracebacks
#         return {"date": None, "available": [], "error": str(e)}




from fastapi import FastAPI
from contextlib import asynccontextmanager
from asuno_salon_birmingham.backend.database import create_db_tables
from fastapi.middleware.cors import CORSMiddleware
from asuno_salon_birmingham.backend.models.booking_models import Booking, BookingCreate, BookingOut
from asuno_salon_birmingham.backend.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from sqlalchemy import select
from datetime import datetime, timezone, timedelta
from asuno_salon_birmingham.backend.utils import get_service_duration, generate_time_slots
from asuno_salon_birmingham.chainlit_frontend.opening_hours import OPENING_HOURS
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("asuna_salon")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Asuna Salon backend...")
    logger.info("CREATING DATABASE TABLES...")
    await create_db_tables()
    logger.info("Database tables created successfully.")
    
    yield
    logger.info("Shutting down Asuna Salon backend...")

# FastAPI application
app = FastAPI(
    lifespan=lifespan,
    title="Asuna Salon Backend",
    version="1.0.0",
)

servers=[
        {
            "url": "http://localhost:8001",
            "description": "Local development server",
        },
        {
            "url": "https://your-backend-api.vercel.app",  # Replace with real domain if deployed
            "description": "Production server",
        }
    ]


origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://curated-shop-ruby.vercel.app",
    "https://curated-shop-australia.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)


@app.get("/")
async def root():
    return {"message": "Welcome to Asuna Salon API"}

# --------- ENDPOINTS ---------

@app.post("/bookings", response_model=BookingOut)
async def create_booking(data: BookingCreate, db: AsyncSession = Depends(get_db)):
    """Create a new booking with a unique reference code."""
    base_ref = f"ASU-{data.date.strftime('%Y%m%d')}"
    result = await db.execute(select(Booking).where(Booking.date == data.date))
    bookings_today = result.scalars().all()
    suffix = len(bookings_today) + 1
    reference = f"{base_ref}-{suffix:03d}"

    new_booking = Booking(
        service=data.service,
        category=data.category,
        date=data.date,
        time=data.time,
        client_name=data.client_name,
        reference=reference,
    )
    db.add(new_booking)

    try:
        await db.commit()
        await db.refresh(new_booking)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Could not save booking: {str(e)}")

    return new_booking



@app.get("/bookings/available-times/{date}")
async def get_available_times(
    date: str, 
    service: str, 
    db: AsyncSession = Depends(get_db)):
    try:
        service_minutes = get_service_duration(service)
        check_date = datetime.strptime(date, "%Y-%m-%d").date()

        for _ in range(14):  # look up to 14 days ahead
            weekday = check_date.weekday()
            hours = OPENING_HOURS.get(weekday)

            if not hours:
                check_date += timedelta(days=1)
                continue

            all_slots = generate_time_slots(hours["start"], hours["end"], service_minutes)

            result = await db.execute(
                select(Booking.time).where(Booking.date == check_date)
            )
            booked = [row[0] for row in result.fetchall()]
            available = [t for t in all_slots if t not in booked]

            if available:
                return {"date": str(check_date), "available": available}

            check_date += timedelta(days=1)

        return {"date": None, "available": []}

    except Exception as e:
        # Never leak raw tracebacks
        return {"date": None, "available": [], "error": str(e)}
    