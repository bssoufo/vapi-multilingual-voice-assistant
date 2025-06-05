# Vapi Multilingual Assistant - Python API Demo

This project demonstrates how to programmatically create and manage a multilingual voice assistant setup on the [Vapi](https://vapi.ai) platform using their REST API with Python.

It implements a strategy where:
1.  A **Language Detector Assistant** first determines the caller's preferred language (English or French).
2.  The call is then transferred to either an **English Assistant** or a **French Assistant**.
3.  These assistants are grouped and managed by a **Vapi Squad**.

This API-first approach allows for version control (Git), easy replication, and scalable management of voice assistants.

## Features

*   Creates/updates 3 Vapi Assistants:
    *   `LanquageDetector`
    *   `EnglishAgent`
    *   `FrenchAgent`
*   Creates/updates 1 Vapi Squad (`DentalClinicSquad`) to orchestrate these assistants.
*   Uses Python with a structured project layout.
*   Includes a simple Vapi API client.
*   All configurations are managed in `vapi-dental-clinic/core/config.py`.

## Prerequisites

*   Python 3.8+
*   A Vapi Account and API Key
*   [Poetry](https://python-poetry.org/) for dependency management

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/bssoufo/vapi-multilingual-voice-assistant.git
    cd YOUR_REPOSITORY_NAME
    ```

2.  **Set up environment variables:**
    Create a `.env` file in the project root directory and add your Vapi API key:
    ```env
    VAPI_API_KEY="YOUR_VAPI_API_KEY_HERE"
    ```

3.  **Install dependencies using Poetry:**
    ```bash
    poetry install
    ```

## Running the Setup

To create or update the assistants and the squad on your Vapi account, run the main script:

```bash
poetry run python vapi-dental-clinic/main.py