import asyncio
import logging
from datetime import timedelta, datetime

from sqlalchemy.orm import sessionmaker

from base.emails import send_email_project_on_funding_before, send_email_project_on_funding, send_email_project_in_course
from database import engine
from models import models_invest, models_user

phases_email_sended = []

logging.basicConfig(filename='send_email_phases_status.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


async def _get_whitelabel_users():
    query = db.query(models_user.User)
    query = query.filter(models_user.User.is_active == 1)
    users = query.all()
    return users


async def _get_invest(phase):
    query = db.query(models_invest.Invest.name, models_invest.Invest.slug, models_invest.Invest.id)
    query = query.filter(models_invest.Invest.id == phase.invest_id)
    invest = query.first()
    return invest


async def send_email_when_phase_is_close_to_start():

    query = db.query(models_invest.InvestMintPhases)
    query = query.filter(models_invest.InvestMintPhases.date_start > datetime.now())
    query = query.filter(models_invest.InvestMintPhases.date_start < datetime.now() + timedelta(hours=1))
    query = query.filter(models_invest.InvestMintPhases.is_email_on_funding_back == 0)
    phases_close_to_start = query.all()

    for phase in phases_close_to_start:
        if f"{phase.invest_id}_{phase.phase}" in phases_email_sended:
            continue

        invest = await _get_invest(phase)

        users = await _get_whitelabel_users()

        phases_email_sended.append(f"{invest.id}_{phase.phase}")

        logging.info(f"Phase {phase.phase} is close to start, sending email to users...")
        for user in users:
            logging.info(f"Sending email to {user.email}")
            await send_email_project_on_funding_before("es",
                                               user.email,
                                               invest.name,
                                               invest.slug,
                                               phase.phase)

        phase.is_email_on_funding_back = 1


async def send_email_when_phase_start_right_now():


    query = db.query(models_invest.InvestMintPhases)
    query = query.filter(models_invest.InvestMintPhases.date_start > datetime.now() - timedelta(minutes=5))
    query = query.filter(models_invest.InvestMintPhases.date_start < datetime.now() + timedelta(minutes=5))
    query = query.filter(models_invest.InvestMintPhases.is_email_on_funding == 0)
    phases_close_to_start = query.all()

    for phase in phases_close_to_start:
        invest = await _get_invest(phase)

        users = await _get_whitelabel_users()

        phases_email_sended.append(f"{invest.id}_{phase.phase}")

        logging.info(f"Phase {phase.phase} is starting right now, sending email to users...")
        for user in users:
            logging.info(f"Sending email to {user.email}")
            await send_email_project_on_funding("es",
                                               user.email,
                                               invest.name,
                                               invest.slug,
                                               phase.phase)

        phase.is_email_on_funding = 1
        db.commit()


async def send_email_when_phase_is_ended():
    query = db.query(models_invest.InvestMintPhases)
    query = query.filter(models_invest.InvestMintPhases.date_end > datetime.now())
    query = query.filter(models_invest.InvestMintPhases.is_email_in_course == 0)
    phases_close_to_start = query.all()

    for phase in phases_close_to_start:
        invest = await _get_invest(phase)

        users = await _get_whitelabel_users()

        phases_email_sended.append(f"{invest.id}_{phase.phase}")

        logging.info(f"Phase {phase.phase} is ended, sending email to users...")
        for user in users:
            logging.info(f"Sending email to {user.email}")
            await send_email_project_in_course("es",
                                               user.email,
                                               invest.name,
                                               invest.slug,
                                               phase.phase)

        phase.is_email_in_course = 1
        db.commit()

logging.info("")
logging.info("-------------------------------------------------")
logging.info("Starting process to send email phases status")

models_invest.Base.metadata.create_all(bind=engine)
models_user.Base.metadata.create_all(bind=engine)

session = sessionmaker(bind=engine)
# models_invest.Base.metadata.create_all(bind=engine)
db = session()

loop = asyncio.get_event_loop()
loop.run_until_complete(send_email_when_phase_start_right_now())
loop.run_until_complete(send_email_when_phase_is_close_to_start())
loop.run_until_complete(send_email_when_phase_is_ended())
loop.close()

logging.info("Process to send email phases status finished")
logging.info("-------------------------------------------------")
logging.info("")


