from fastapi.requests import Request

from src.services.repository import RepoFactory


async def get_repos(request: Request) -> RepoFactory:
    async with request.app.state.db_session() as session:
        yield RepoFactory(session, debug=request.app.state.config.DEBUG)
