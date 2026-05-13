import traceback
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func, desc, or_
from sqlalchemy.orm import Session
from starlette import status

from api.v1 import const
from api.v1.base.base import Object
from api.v1.base.base_invest import _get_invest, _get_users_invest_buy_waiting_transfer_total_num, _get_users_invest_active_group
from api.v1.base.base_wallet import _get_wallet_value

from api.v1.models import models_user, models_invest
from blockchain.nft_utils import mint_tokens_to_pooled_wallets


def _buy_user_invest_tokens(
        db: Session,
        
        user_id: int,
        invest_id: int,
        num_tokens: int,
        type_buy: int,
        buy_subtype: int = None,
        make_commit: bool = True,
        financing_phase: bool = True,
        user_contribution_by_admin: bool = False,
        date_created: datetime = None,
        user_invest_parent_id: int = 0,
        mint_tx: str = None,
        signature_documents_id: str = None,
        fees: float = 0,
):
    # metodo BASE para comprar tokens de la plataforma
    q = db.query(models_user.User.kyc_valid)
    q = q.filter(models_user.User.id == user_id)
    
    q = q.filter(models_user.User.is_active)
    db_user = q.first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.User not found")
    if int(db_user.kyc_valid) != 1:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="server.The user does not have a valid kyc")

    if not date_created:
        date_created = datetime.now()  # datetime.today().strftime('%Y-%m-%d %H:%M')

    status_invest = -1
    if financing_phase:
        status_invest = const.INVEST_STATUS_FINANCING_PHASE

    item_invest = _get_invest(db=db, invest_id=invest_id, status_invest=status_invest)

    # se recupera la fase actual de minteo de un proyecto para poder comprar en esa fase
    q = db.query(models_invest.InvestMintPhases)
    q = q.filter(models_invest.InvestMintPhases.invest_id == invest_id)
    q = q.filter(models_invest.InvestMintPhases.date_start <= date_created)
    q = q.filter(models_invest.InvestMintPhases.date_end >= date_created)
    phase = q.first()
    if not phase:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="server.The project has not a phase")

    # si es fase privada tengo que estar apuntado a ella
    # si es el usuario promotor no hace falta
    # si es desde el admin que estoy poniendo la contribucion del usuario tampoco hace falta
    if phase.is_private and user_id and not user_contribution_by_admin:
        q = db.query(models_user.UserInvestWhiteList)
        q = q.filter(models_user.UserInvestWhiteList.invest_id == invest_id)
        q = q.filter(models_user.UserInvestWhiteList.user_id == user_id)
        q = q.filter(models_user.UserInvestWhiteList.preference_to_buy == phase.phase)
        user_invest_whitelist = q.first()
        if not user_invest_whitelist:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="server.The user has not in whitelist")

    # se recuperan los tokens comprados por los usuarios para ver el maximo de token que quedan en este minteo
    q = db.query(func.sum(models_user.UsersInvest.num_tokens).label("num_tokens"))
    q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    q = q.filter(models_user.UsersInvest.phase == phase.phase)
    # las que han sido pagadas y validadas
    q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY)
    # solo las compras a la plataforma
    q = q.filter(models_user.UsersInvest.other_user_id == None)
    sold_tokens = q.first().num_tokens

    if user_contribution_by_admin:
        # si somos admin, quedan todos los tokens para poder validar las transacciones
        remaining_tokens = phase.max_tokens
    else:
        if sold_tokens is not None:
            remaining_tokens = phase.max_tokens - sold_tokens
        else:
            remaining_tokens = phase.max_tokens

        # se le resta los tokens esperando transferencia para reservarlos
        remaining_tokens -= _get_users_invest_buy_waiting_transfer_total_num(db=db, invest_id=invest_id, phase=phase.phase)

    # si los token comprados es mayor que los que quedan error
    if num_tokens > remaining_tokens:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="server.superado maximo numero de tokens")

    # si el numero de tokens comprado es menor que el ticket minimo y si solo quedan menos que el ticket minimo hay que comprar los que quedan
    if num_tokens < phase.num_tokens_min_to_buy and num_tokens != remaining_tokens:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="server.numero tokens comprado menor que ticket minimo")

    try:
        # se guarda la compra
        user_tokens = models_user.UsersInvest(
            user_id=user_id,
            invest_id=invest_id,
            num_tokens=num_tokens,
            price_token=phase.price_fiat,
            value=num_tokens * phase.price_fiat,
            date_created=date_created,
            type=type_buy,
            buy_subtype=buy_subtype,
            phase=phase.phase,
            fees=fees
        )
        # si tiene relacion con otro registro
        if user_invest_parent_id != 0:
            user_tokens.parent_id = user_invest_parent_id

        # Eliminar todas las consultas pendientes en la sesión porque hacia un update y quitaba los datos de num_tokens de users_invest
        db.expunge_all()

        db.add(user_tokens)
        db.flush()

        # si se hace con blockchain
        if type_buy == const.USERS_INVEST_TYPE_BUY:
            try:
                if mint_tx:
                    user_tokens.tx = mint_tx
                elif item_invest.contract_address:
                    result = mint_tokens_to_pooled_wallets(item_invest, num_tokens, user_id, db, phase)
                    if result['status'] != 1 and result['status'] != True:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="server.fallo al realizar el mint de los tokens")
                    user_tokens.tx = result['tx']
            except Exception as e:
                print(traceback.format_exc())
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="server.error in buy")

        # por si no se quiere hacer el commit todavia porque hay mas transacciones despues
        if make_commit:
            db.commit()

        aux = Object()
        aux.id = user_tokens.id
        aux.user_id = user_id
        aux.invest_id = invest_id
        aux.price_token = phase.price_fiat
        aux.num_tokens = num_tokens
        aux.phase = phase.phase
        aux.type = type_buy
        aux.blockchain_network = item_invest.blockchain_network
        aux.contract_address = item_invest.contract_address
        return aux

    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="server.error in buy")


def _get_user_invest_my_tokens(
        db: Session,
        
        user_id: int,
        invest_id: int = 0
):
    current_datetime = datetime.now()

    # listado de mis inversiones
    list_my_invest_active = _get_users_invest_active_group(db=db, user_id=user_id, invest_id=invest_id)
    list_my_invest = []
    for item in list_my_invest_active:
        # solo se cogen para poder vender los tokens que estan sus inversiones en fase de financiacion o en progreso
        if item.status == const.INVEST_STATUS_IN_PROGRESS or item.status == const.INVEST_STATUS_FINANCING_PHASE:
            # se recupera el ultimo precio de la fase
            q = db.query(models_invest.InvestMintPhases.price_fiat)
            q = q.filter(models_invest.InvestMintPhases.invest_id == item.id)
            q = q.filter(models_invest.InvestMintPhases.date_start <= current_datetime)
            last_price = q.order_by(desc(models_invest.InvestMintPhases.date_end)).first()
            aux = Object()
            aux.price_token = last_price.price_fiat
            aux.invest_id = item.id
            aux.name = item.name
            aux.slug = item.slug
            aux.num_tokens = item.num_tokens
            aux.category_id = item.category_id
            list_my_invest.append(aux)

    # listado de inversiones en venta que son mias
    q = db.query(
        models_user.UsersInvest.id,
        models_user.UsersInvest.invest_id,
        models_user.UsersInvest.num_tokens)
    q = q.filter(models_user.UsersInvest.user_id == user_id)
    q = q.filter(models_user.UsersInvest.invest_id == models_invest.Invest.id)
    q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_PUT_ON_SALE)
    
    list_my_current_sales = q.order_by(desc(models_user.UsersInvest.date_created)).all()

    # a mis tokens actuales le resto los tokens que tengo en venta menos los que he retirado de la venta
    for sale in list_my_current_sales:
        # se busca si esa venta se ha retirado o ya esta esperando la compra de otro usuario, es asi si tiene parent_id
        q = db.query(models_user.UsersInvest.id, models_user.UsersInvest.invest_id, models_user.UsersInvest.type)
        q = q.filter(models_user.UsersInvest.invest_id == sale.invest_id)
        q = q.filter(models_user.UsersInvest.parent_id == sale.id)
        item_retired = q.first()
        for my_invest in list_my_invest:
            if sale.invest_id == my_invest.invest_id:
                if not item_retired:
                    my_invest.num_tokens = my_invest.num_tokens - sale.num_tokens
                elif item_retired.type == const.USERS_INVEST_TYPE_WAITING_OTHER_USER_FOR_SALE:
                    # si se habia puesto a la venta hay que ver si se vendio despues
                    q = db.query(models_user.UsersInvest.id, models_user.UsersInvest.invest_id, models_user.UsersInvest.type)
                    q = q.filter(models_user.UsersInvest.parent_id == item_retired.id)
                    q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_SOLD, models_user.UsersInvest.type == const.USERS_INVEST_TYPE_SALE_REJECTED))
                    item_child = q.first()
                    # si tiene hijo pero es una venta entonces no se le resta
                    if not item_child:
                        my_invest.num_tokens = my_invest.num_tokens - sale.num_tokens

    return [x for x in list_my_invest if x.num_tokens > 0]
