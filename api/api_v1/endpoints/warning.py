from enum import Enum
from typing import List
from typing import Optional

from fastapi import APIRouter, HTTPException
from starlette.responses import UJSONResponse

from crud.warning import *
from db.conn_engine import META_URL
from model.log import WarningLogSchema

router = APIRouter()


class GroupRule(str, Enum):
    date = "date"
    station = "station"
    asset = "asset"
    isread = "isread"
    branch = "branch"
    region = "region"


@router.get(
    "/", response_class=UJSONResponse, response_model=List[Optional[WarningLogSchema]]
)
async def read_warning_logs(skip: int = None, limit: int = None, asset_id: int = None):
    """
    Get Warning List.
    """
    conn = Database(META_URL)
    items = await get_multi(conn=conn, skip=skip, limit=limit, asset_id=asset_id)
    return items


@router.get("/stat/", response_class=UJSONResponse)
async def read_warning_logs_statistic(group_by: GroupRule,):
    """
    Response Schema:

    - if **group_by = date**: [[date,warning number in this date],...]
    - if **group_by = station/region/company**: return two fields 'labels' and 'series' for pie chart drawing.
    - if **group_by = asset**: [[asset_id,warning number of this asset],...]
    - if **group_by = isread**: [[ 0,unread warninglog],[1,read warninglog]]

    """
    conn = Database(META_URL)

    if group_by == GroupRule.date:
        res = await get_warning_calendar(conn=conn)
        return res
    if group_by == GroupRule.station:
        res = await get_warning_stat_by_station(conn=conn)
        return res
    if group_by == GroupRule.asset:
        res = await get_warning_stat_by_asset(conn=conn)
        return res
    if group_by == GroupRule.isread:
        res = await get_warning_stat_by_isreadable(conn=conn)
        return res
    if group_by == GroupRule.branch:
        res = await get_warning_stat_by_branch_company(conn=conn)
        return res
    if group_by == GroupRule.region:
        res = await get_warning_stat_by_region_company(conn=conn)
        return res
    else:
        raise HTTPException(status_code=400, detail="Bad query parameters")


@router.get("/{id}/", response_class=UJSONResponse, response_model=WarningLogSchema)
async def read_warning_logs_by_id(id: int,):
    """
    Get warning log by ID.
    """
    conn = Database(META_URL)
    item = await get(conn=conn, id=id)
    if not item:
        raise HTTPException(status_code=400, detail="Item not found")
    return item
