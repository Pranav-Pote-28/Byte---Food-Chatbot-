from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app=FastAPI()

# @app.get("/")
# async def root():
#     return ({"message":"hello world"})

inprogress_orders={}

@app.post("/")
async def handle_request(request:Request):
    payload=await request.json()

    intent=payload["queryResult"]["intent"]["displayName"]
    parameters=payload["queryResult"]["parameters"]
    outputContexts=payload["queryResult"]["outputContexts"]

    session_id=generic_helper.extract_session_id(outputContexts[0]["name"])

    intent_handler_dict={
        "order.add-context: ongoing-order":add_to_order,
        # "order.complete-context:ongoing-order":remove_from_order,
        # "order.remove-context: ongoing-order":complete_order,
        "track.order-context:ongoing-tracking":track_order
    }

    return intent_handler_dict[intent](parameters,session_id)




def add_to_order(parameters:dict,session_id:str):
    food_items=parameters["food-item"]
    quantities=parameters["number"]

    if len(food_items)!=len(quantities):
        fulfillmenttext="Please enter the quantity and fooditems respectively"
    else:
        new_food_dict=dict(zip(food_items,quantities))

        if session_id in inprogress_orders:
            current_food_dict=inprogress_orders[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_orders[session_id]=current_food_dict
        else:
            inprogress_orders[session_id]=new_food_dict
            print(inprogress_orders,session_id)

        order_str=generic_helper.get_str_from_food_dict(inprogress_orders[session_id])


        fulfillmenttext=f"so far you have ordered {order_str}"

    return JSONResponse(content={"fulfillmentText":fulfillmenttext})



def track_order(parameters:dict):
    order_id=int(parameters["order_id"])
    order_status=db_helper.get_order_status(order_id)

    if order_status:
        fulfillmenttext=f"Order Status: {order_status} for OrderId: {order_id}"
    else:
        fulfillmenttext=f"No order found with OrderId: {order_id}"

    return JSONResponse(content={"fulfillmentText":fulfillmenttext})
