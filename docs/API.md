# API Documentation

## Trading Endpoints

### Get Open Positions
- **URL:** `/api/positions`
- **Method:** `GET`
- **Description:** Returns a list of all currently open trading positions.
- **Response:** `List[PositionRead]`

### Get Trade History
- **URL:** `/api/history`
- **Method:** `GET`
- **Description:** Returns a list of closed trades (history).
- **Parameters:**
    - `limit` (int, default=50)
    - `offset` (int, default=0)
- **Response:** `List[PositionRead]`

### Place Order
- **URL:** `/api/place-order`
- **Method:** `POST`
- **Description:** Places a manual trade order.
- **Body:** `PositionCreate`
- **Response:** `PositionRead`

### Close Position
- **URL:** `/api/close-position/{position_id}`
- **Method:** `POST`
- **Description:** Manually closes an open position.
- **Parameters:**
    - `exit_price` (float)
- **Response:** `PositionRead`

### Get Settings
- **URL:** `/api/settings`
- **Method:** `GET`
- **Description:** Returns current trading settings (e.g., paper vs. live mode).
- **Response:** `{"mode": str}`

### Update Settings
- **URL:** `/api/settings`
- **Method:** `POST`
- **Description:** Updates trading settings.
- **Parameters:**
    - `mode` (str): `paper` or `live`
- **Response:** `{"mode": str, "status": "updated"}`

## Signal Endpoints

### Get Signals
- **URL:** `/api/signals`
- **Method:** `GET`
- **Description:** Returns a list of recent trading signals.
- **Parameters:**
    - `strategy` (str, optional)
    - `limit` (int, default=100)
    - `offset` (int, default=0)
- **Response:** `List[SignalRead]`

### Create Signal
- **URL:** `/api/signals`
- **Method:** `POST`
- **Description:** Manually creates a signal (mostly for testing or strategy integration).
- **Body:** `SignalCreate`
- **Response:** `SignalRead`

## Auth Endpoints

### Zerodha OAuth Callback
- **URL:** `/auth/zerodha/callback`
- **Method:** `GET`
- **Description:** Handles the Zerodha OAuth redirect callback.
- **Parameters:**
    - `request_token` (str)
- **Response:** `{"status": str, "note": str}`
