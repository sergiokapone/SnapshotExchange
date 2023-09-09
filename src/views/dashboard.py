from fastapi.responses import HTMLResponse
from fastapi import (
    APIRouter,
    Request,
)

from fastapi.templating import Jinja2Templates

from src.conf.info_dict import project_info

from src.services.documentation import rst_to_html

templates = Jinja2Templates(directory="templates")
templates.env.globals["rst_to_html"] = rst_to_html
router = APIRouter(tags=["Views"])


@router.get("/list", tags=["Root"], include_in_schema=False)
async def show_route_list(request: Request):
    routes = [
        {
            "path": str(request.base_url)[:-1] + route.path,
            "name": route.name,
            "method": route.methods,
            "description": route.description,
        }
        for route in request.app.routes
        if hasattr(route, "description") and route.description is not None
    ]
    return templates.TemplateResponse(
        "api_description.html", {"request": request, "routes": routes}
    )


@router.get(
    "/dashboard", response_class=HTMLResponse, include_in_schema=False, name="dashboard"
)
async def root(request: Request):
    """
    Project Information Page

    This endpoint serves an HTML page displaying information about the project.

    :param request: The HTTP request object.
    :type request: Request
    :return: The HTML page displaying project information.
    :rtype: HTMLResponse
    """

    str(request.base_url)[:-1]
    project_info.update(
        {"request": request, "current_base": str(request.base_url)[:-1]}
    )
    return templates.TemplateResponse("index.html", project_info)
