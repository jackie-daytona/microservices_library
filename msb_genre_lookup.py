# Danny Caspary
# CS361: Software Engineering I
# Microservice B: Genre Lookup for Library Catalog
# Using ZeroMQ API, based on "Introduction to ZeroMQ" pdf by Luis Flores

import zmq
import time
import json

context = zmq.Context()

socket = context.socket(zmq.REP)

socket.bind("tcp://*:1739")


def print_by_genre(genres, books):
    """builds message of books sorted by genre to send back to main program"""
    message = ""
    for genre in genres:
        message += f"\n{genre}:\n"
        for book in books:
            if books[book]["genre"] == genre:
                message += f"{book}\n"
        time.sleep(2)
    return message


while True:
    data = socket.recv_json()
    obj = json.loads(data)
    if len(obj) >= 2:           # send genres and titles back to library.py
        genres, books = obj     # unpack tuple to get data for display
        response = print_by_genre(genres, books)
        socket.send_string(response)
        time.sleep(3)
    else:                       # else send confirmation message and end microservice
        if obj == "Q":
            socket.send_string("display complete")
            print("message received")
            break

context.destroy()


