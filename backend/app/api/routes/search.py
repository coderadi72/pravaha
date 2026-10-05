from typing import Literal
from fastapi import APIRouter,Query
from backend.app.api.deps import CurrentUser,SessionDep
from backend.app.db.search_repository import search
router=APIRouter(tags=['Search'])

@router.get('/api/search')
def search_records(session:SessionDep,user:CurrentUser,q:str=Query('',max_length=120),kind:Literal['all','projects','activities','field-updates','versions','warnings','audit','memory']='all',limit:int=Query(20,ge=1,le=100),offset:int=Query(0,ge=0)):
    return search(session,user,q.strip(),kind,limit,offset)
