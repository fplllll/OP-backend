from databases import Database
from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.responses import UJSONResponse
from datetime import datetime
from core.dependencies import get_mp_mapper
from crud.vib_data import get_latest, get_by_id, get_multi
from db.conn_engine import STATION_URLS
from model.vib_data import VibrationSignalSchema,VibrationSignalListSchema
from typing import List
router = APIRouter()


@router.get("/mp/{mp_id}/vib_data/latest/", response_class=UJSONResponse, response_model=VibrationSignalSchema)
async def read_the_latest_vibration_signal(
        mp_id: int,
        mp_mapper: dict = Depends(get_mp_mapper)
):
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info['type'] == 1:
        raise HTTPException(status_code=400,
                            detail="The given measure point collect elecdata, try to use the approaprite endpoint.")

    conn = Database(STATION_URLS[mp_shard_info['station_id']])
    res = await get_latest(conn=conn, shard_id=mp_shard_info['inner_id'])
    return {'id': res['id'],
            'time': res['time'],
            'vib': res['vib']}


@router.get("/mp/{mp_id}/vib_data/list/", response_class=UJSONResponse,response_model=List[VibrationSignalListSchema] )
async def read_all_vibration_signal_info(
        mp_id: int,
        time_before: datetime = Query(default='2016-01-01 00:00:00'),
        time_after: datetime = Query(default='2016-07-10 00:00:00'),
        mp_mapper: dict = Depends(get_mp_mapper)
):
    """
    Diagnosis info will be joined to the response in the future.
    """
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info['type'] == 1:
        raise HTTPException(status_code=400,
                            detail="The given measure point collect elecdata, try to use the approaprite endpoint.")

    conn = Database(STATION_URLS[mp_shard_info['station_id']])
    res = await get_multi(conn=conn, shard_id=mp_shard_info['inner_id'], time_before=time_before, time_after=time_after)
    if not res:
        raise HTTPException(status_code=400,
                            detail="No signal collected between the time range")
    return [dict(row) for row in res]


@router.get("/mp/{mp_id}/vib_data/{data_id}/}", response_class=UJSONResponse, response_model=VibrationSignalSchema)
async def read_vibration_signal_by_id(
        mp_id: int,
        data_id: int,
        mp_mapper: dict = Depends(get_mp_mapper)
):
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info['type'] == 1:
        raise HTTPException(status_code=400,
                            detail="The given measure point collect elecdata, try to use the approaprite endpoint.")

    conn = Database(STATION_URLS[mp_shard_info['station_id']])
    res = await get_by_id(conn=conn, shard_id=mp_shard_info['inner_id'], data_id=data_id)
    return dict(res)