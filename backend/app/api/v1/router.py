from fastapi import APIRouter

from app.api.v1 import auth, candidates, jobs, matches, applications, notifications, admin, contact, managed_sites

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(candidates.router)
api_router.include_router(jobs.router)
api_router.include_router(matches.router)
api_router.include_router(applications.router)
api_router.include_router(notifications.router)
api_router.include_router(admin.router)
api_router.include_router(contact.router)
api_router.include_router(managed_sites.router)
