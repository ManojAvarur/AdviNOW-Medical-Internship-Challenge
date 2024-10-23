from fastapi import APIRouter, Response

router = APIRouter()


@router.get('/status')
async def get_status(res: Response):
    try:
        # 100/0
        res.status_code = 500
        return {"Health OK"}

    except Exception as e:
        return 500, {'Error: ' + str(e)}
