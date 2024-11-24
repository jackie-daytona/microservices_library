# Danny Caspary
# CS361: Microservice A -- SKU alert
# Fall 2024
# Using ZeroMQ API, code adapted from example in "Introduction to ZeroMQ"
#     by Luis Flores

import zmq
import time
from datetime import date
import json

context = zmq.Context()

socket = context.socket(zmq.REP)

socket.bind("tcp://*:1738")

while True:
    data = socket.recv_json()
    obj = json.loads(data)
    if len(obj) >= 2:           # send sku alert to main program
        item, days_overdue = obj
        alert = f"{item} is overdue by {abs(days_overdue)} days!"
        socket.send_string(alert)
    else:                       # else send confirmation message and end microservice
        if obj == "Q":
            socket.send_string("MSA_complete")
            print("message received")
            break

context.destroy()
