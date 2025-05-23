# Currency Exchange Rate System

## Overview
This Django-based system manages currency exchange rates from multiple providers. It offers a flexible and robust solution for tracking currency conversions, supporting multiple data providers, and maintaining historical exchange rate data.

## Features
- Multiple currency support with automatic currency information population
- Exchange rate tracking from various providers
- Historical exchange rate data storage
- Soft deletion support for data integrity
- Priority-based provider system
- Automatic timestamp tracking for all records

## Models

### Currency
- Stores basic currency information (code, name, symbol)
- Automatically populates currency details for common currencies (USD, EUR, GBP)
- Implements soft deletion for data preservation

### CurrencyExchangeRateProvider
- Manages different exchange rate data sources
- Features include:
  - Priority-based ordering
  - Active/inactive status tracking
  - API key management
  - Unique provider names

### CurrencyExchangeRate
- Records individual exchange rates
- Stores:
  - Source and target currencies
  - Valuation date
  - Exchange rate value
  - Provider information
  - Timestamp of record creation

## Setup

1. Install required dependencies:

`pip install -r requirements.txt`
2. Run database migrations:

bash 
`python manage.py makemigrations python manage.py migrate
`
3. Create a superuser (optional):

bash `python manage.py createsuperuser`
4. Start the development server:

bash `python manage.py runserver`

## API Endpoints
Here are the core endpoints used for interacting with the system.

All endpoints return JSON responses and require application/json as Content-Type.

### Currency Endpoints

List all currencies `GET /api/currencies/`

Create a new currency `POST /api/currencies/`

### Exchange Rate Provider Endpoints

List all active providers: `GET /api/providers/`

Create a new provider: `POST /api/providers/`

Update a provider by ID: `PUT /api/providers/{id}/`

Soft-delete a provider: `DELETE /api/providers/{id}/`

### Exchange Rate Endpoints
List historical exchange rates (with filters): `GET /api/exchange-rate/`

Retrieve a specific exchange rate: `GET /api/exchange-rate/?source=USD&target=EUR&date=2025-05-23`

## Fetching Rates
To fetch new exchange rates from active providers:

bash `python manage.py fetch_rates`

This will:

Pull current exchange rates for defined currency pairs.

Cache the result.

Store it in the database (if not already present).

