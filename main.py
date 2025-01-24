from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

app=FastAPI()

# @app.get("/")
# async def root():
#     return ({"message":"hello world"})

@app.post("/")
async def handle_request(request:Request):
    payload=await request.json()

    intent=payload["queryResult"]["intent"]["displayName"]
    parameters=payload["queryResult"]["parameters"]
    outputContexts=payload["queryResult"]["outputContexts"]

    if intent=="track.order-context:ongoing-tracking":

        return JSONResponse(content={"fulfillmentText":"received intent track.order in the backend !"})