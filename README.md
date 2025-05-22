# Microservices Library Catalog

CS 361: Software Engineering I
Author: Danny Caspary
Overview

This project is a command-line library catalog system designed to demonstrate key software engineering principles — including modularity, user interaction, and the use of microservices. Users can sign up or log in, browse books, check items out, view their due dates, and return items. The system is powered by two supporting microservices:

    Microservice A: Alerts users when they have overdue items.

    Microservice B: Allows users to view the catalog by genre.

ZeroMQ is used for communication between the main program and the microservices, demonstrating inter-process communication (IPC) and distributed system design in a local environment.

## Features
Main Program (library.py)

    User Management

        New user registration with randomly generated IDs

        Returning user login with password validation

    Book Catalog

        View the entire catalog or browse by genre (via Microservice B)

        Check the availability of individual titles

        Check out and return books

    Item Status

        Displays checked-out items and due dates

        Sends overdue alerts (via Microservice A)

    CLI Navigation

        Simple, clear text prompts with input validation

        Graceful loopback and exit options

Microservice A: msa_send_alert.py

    Communicates with the main app using ZeroMQ

    Receives overdue items and returns an alert message

Microservice B: msb_genre_lookup.py

    Accepts a list of genres and the catalog dictionary

    Returns a neatly formatted string of available titles by genre

## How to Run

    Install dependencies
    Only ZeroMQ and pyzmq are required:

pip install pyzmq

Start Microservices
In two separate terminal windows or background processes, run:

python msa_send_alert.py
python msb_genre_lookup.py

Run the Main Program
In a third terminal window:

    python library.py

## Technologies Used

    Python 3.11+

    ZeroMQ / pyzmq

    JSON for data serialization

    CLI-based UX

## Possible Improvements

This project was built with future extensibility in mind. Planned upgrades include:

    Migrating the catalog and user data to a database (e.g., SQLite or PostgreSQL)

    Building a graphical interface (GUI) using tkinter or a web frontend

    Enhanced error handling for malformed input or broken connections

    Unit tests for key logic and microservice communication

## Project Structure

library/
 - library.py              # Main CLI-based library app
 - msa_send_alert.py       # Microservice A (Overdue Alerts)
 - msb_genre_lookup.py     # Microservice B (Genre Lookup)
 - README.md               # Project documentation

## Notes

    The generate_id() function uses a limited character set for easier typing and debugging.

    Microservices send a termination signal "Q" to indicate when the task is complete.

## Acknowledgments

    Adapted ZeroMQ examples from "Introduction to ZeroMQ" by Luis Flores.

    Random ID generation logic adapted from GeeksForGeeks.

    CLI and datetime techniques pulled from Stack Overflow and Python documentation.
