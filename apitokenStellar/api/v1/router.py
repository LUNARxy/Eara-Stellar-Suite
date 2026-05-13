from fastapi import APIRouter

api_router = APIRouter(include_in_schema=False)

#################################################################################################################
#       VERSIÓN 1 DEL API
#################################################################################################################
from api.v1.endpoints.public import (
    public_login,
)
from api.v1.endpoints.private import (
    wallet,
    users,
    follows,
    invest,
    portfolio,
    marketplace,
    tokens,
    invest_phases,
    invest_profits,
    invest_media,
    invest_documents,
    invest_news,
    invest_team,
    invest_questions,
    invest_status_description,
    portfolio_nuevo,
    private_stellar,
)

# PARTE PUBLICA DEL API
api_router.include_router(
    public_login.router, prefix="/v1/public/login", tags=["PUBLIC CREDENTIALS"]
)


# PARTE PRIVADA DEL API
api_router.include_router(
    invest.router, prefix="/v1/private/invest", tags=["PRIVATE INVEST"]
)
api_router.include_router(
    invest_phases.router,
    prefix="/v1/private/invest/phases_mint",
    tags=["PRIVATE INVEST PHASES"],
)
api_router.include_router(
    invest_profits.router,
    prefix="/v1/private/invest/profits",
    tags=["PRIVATE INVEST PROFITS"],
)
api_router.include_router(
    invest_media.router,
    prefix="/v1/private/invest/media",
    tags=["PRIVATE INVEST MEDIA"],
)
api_router.include_router(
    invest_documents.router,
    prefix="/v1/private/invest/documents",
    tags=["PRIVATE INVEST DOCUMENTS"],
)
api_router.include_router(
    invest_news.router, prefix="/v1/private/invest/news", tags=["PRIVATE INVEST NEWS"]
)
api_router.include_router(
    invest_team.router, prefix="/v1/private/invest/team", tags=["PRIVATE INVEST TEAM"]
)
api_router.include_router(
    invest_questions.router,
    prefix="/v1/private/invest/questions",
    tags=["PRIVATE INVEST QUESTIONS"],
)
api_router.include_router(
    invest_status_description.router,
    prefix="/v1/private/invest/status_description",
    tags=["PRIVATE INVEST STATUS DESCRIPTION"],
)
api_router.include_router(
    wallet.router, prefix="/v1/private/wallet", tags=["PRIVATE WALLET"]
)
api_router.include_router(
    users.router, prefix="/v1/private/users", tags=["PRIVATE USERS"]
)
api_router.include_router(
    follows.router, prefix="/v1/private/follows", tags=["PRIVATE FOLLOWS"]
)
api_router.include_router(
    portfolio.router, prefix="/v1/private/portfolio", tags=["PRIVATE PORTFOLIO"]
)
api_router.include_router(
    portfolio_nuevo.router,
    prefix="/v1/private/portfolio_nuevo",
    tags=["PRIVATE PORTFOLIO"],
)
api_router.include_router(
    marketplace.router, prefix="/v1/private/marketplace", tags=["PRIVATE MARKETPLACE"]
)
api_router.include_router(
    tokens.router, prefix="/v1/private/tokens", tags=["PRIVATE TOKENS"]
)
api_router.include_router(
    private_stellar.router, prefix="/v1/private/stellar", tags=["PRIVATE STELLAR"]
)
