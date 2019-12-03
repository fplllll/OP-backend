from __future__ import absolute_import, unicode_literals

import numpy as np
from celery import Celery
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base

from db.conn_engine import meta_engine, station_engines
from db.db_config import session_make
from db_model import VibFeature, VibData
from db_model import MeasurePoint
from services.signal.vibration.vibration_class import VibrationSignal
import os
# from utils import vib_feature_tools
# from services.signal.electric.elec_feature_tools import threephase_deserialize, feature_calculator

Base = declarative_base()

app = Celery(
    "tasks",
    broker=os.getenv('RABBITMQ_URL'),
    # broker='pyamqp://guest@localhost//',
    # backend='redis://@localhost'
)

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=10, timezone="Asia/Shanghai", worker_max_tasks_per_child=100
)

app.conf.beat_schedule = {
    "cal-vib-feature-in-60-seconds-task": {
        "task": "core.celery.cal_vib_feature",
        "schedule": 60.0,
    },
}


@app.task(ignore_result=True)
def cal_vib_feature():
    session = session_make(engine=meta_engine)
    mps = (
        session.query(MeasurePoint.db_id, MeasurePoint.id_inner_station)
        .filter(MeasurePoint.type == 0)
        .all()
    )
    session.close()

    group_dict = {}
    for mp in mps:
        if mp.db_id not in group_dict.keys():
            group_dict[mp.db_id] = []
        group_dict[mp.db_id].append(mp.id_inner_station)

    for db_id in group_dict.keys():
        mp_ids = group_dict[db_id]
        for mp_id in mp_ids:
            engine = station_engines[db_id - 1]
            s = text(
                "SELECT d.id,d.time as time, d.ima as vib "
                "from b_vib_{} as d "
                "LEFT JOIN b_fea_{} as f on d.id = f.data_id "
                "where f.data_id is null "
                "limit 10;".format(
                    mp_id, mp_id
                )
            )
            conn = engine.connect()
            result = conn.execute(s)
            data = result.fetchall()
            result.close()

            if len(data) > 0:

                data_model = VibData.model(point_id=mp_id, base=Base)
                feature = VibFeature.model(point_id=mp_id, base=Base)

                to_save = []
                for row in data:
                    signal = np.fromstring(row.vib, dtype=np.float32)
                    signal = VibrationSignal(data=signal,fs=10000)
                    to_save.append(
                        feature(
                            rms=signal.rms_fea,
                            max=signal.max_fea,
                            p2p=signal.pp_fea,
                            avg=np.mean(signal.data),
                            var=signal.var_fea,
                            kurtosis=signal.kurtosis,
                            data_id=row.id,
                            time=row.time,
                        )
                    )
                session = session_make(engine=engine)
                try:
                    session.add_all(to_save)
                    session.commit()
                    session.close()
                    print("inserted rows: {}".format(len(to_save)))
                except Exception as e:
                    session.rollback()
                    print(e)

            else:
                print("No new row detected")
