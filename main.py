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
        "order.complete-context:ongoing-order":complete_order,
        "order.remove-context: ongoing-order":remove_from_order,
        "track.order-context:ongoing-tracking":track_order
    }

    return intent_handler_dict[intent](parameters,session_id)

def remove_from_order(parameters:dict,session_id:str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={"fulfillmentText":"Sorry No order found !"})

    current_order=inprogress_orders[session_id]

    food_items=parameters["food-item"]
    removed_items=[]
    no_such_items=[]

    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    if len(removed_items)>0:
        fulfillmenttext=f"Removed {','.join(removed_items)} from your order"
    if len(no_such_items)>0:
        fulfillmenttext=f"Your current order doesnt have {','.join(no_such_items)}"
    if len(current_order.keys())==0:
        fulfillmenttext="you order is empty"

    order_str=generic_helper.get_str_from_food_dict(current_order)
    fulfillmenttext+=f" your current order contains {order_str}"

    return JSONResponse(content={"fulfillmentText":fulfillmenttext})


        


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


        fulfillmenttext=f"so far you have ordered {order_str} \n anything else ?"

    return JSONResponse(content={"fulfillmentText":fulfillmenttext})

def complete_order(parameters:dict,session_id:str):
    if session_id not in inprogress_orders:
        fulfillmenttext="No order please order again"
    else:
        order=inprogress_orders[session_id]
        order_id=save_to_db(order)

        if order_id==-1:
            fulfillmenttext="Sorry no order found"
        else:
            order_total=db_helper.get_total_order_price(order_id)
            fulfillmenttext=f"Your order has been placed Your order id : {order_id} Order total : {order_total}"


        del inprogress_orders[session_id]
    return JSONResponse(content={"fulfillmentText":fulfillmenttext})

def save_to_db(order: dict):

    next_order_id=db_helper.get_next_order_id()

    for food_item,quantity in order.items(): 
        rcode=db_helper.insert_order_item(food_item,quantity,next_order_id)

        if rcode==-1:
            return -1

    db_helper.insert_order_tracking(next_order_id,"in progress")    
    
    return next_order_id

def track_order(parameters:dict,sesssion_id:str):
    order_id=int(parameters["order_id"])
    order_status=db_helper.get_order_status(order_id)

    if order_status:
        fulfillmenttext=f"Order Status: {order_status} for OrderId: {order_id}"
    else:
        fulfillmenttext=f"No order found with OrderId: {order_id}"

    return JSONResponse(content={"fulfillmentText":fulfillmenttext})
