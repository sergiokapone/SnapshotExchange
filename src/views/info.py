from fastapi.responses import HTMLResponse
from fastapi import (
    APIRouter,
    Request,
)

from fastapi.templating import Jinja2Templates
from fastapi import APIRouter

from src.conf.info_dict import project_info

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["Views"])


@router.get("/info", response_class=HTMLResponse, include_in_schema=False, name="project_nfo")
async def root(request: Request):
    """
    Project Information Page

    This endpoint serves an HTML page displaying information about the project.

    :param request: The HTTP request object.
    :type request: Request
    :return: The HTML page displaying project information.
    :rtype: HTMLResponse
    """
    
    project_info.update({"request": request})
    return templates.TemplateResponse("index.html", project_info)
