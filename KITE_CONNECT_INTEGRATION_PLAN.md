# Kite Connect Integration Plan

Kite Connect is a good fit for Financial Board's India market-data layer. The
first release should be read-only: quotes, instrument metadata, and historical
candles should feed the existing cache and prediction engine. Prediction output
must never place an order automatically.

Official references:

- [Kite Connect introduction](https://kite.trade/docs/connect/v3/)
- [Login and token exchange](https://kite.trade/docs/connect/v3/user/)
- [Market quotes and instruments](https://kite.trade/docs/connect/v3/market-quotes/)
- [WebSocket streaming](https://kite.trade/docs/connect/v3/websocket/)
- [Historical candles](https://kite.trade/docs/connect/v3/historical/)
- [Current plan and pricing summary](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/what-are-the-charges-for-kite-apis)

## Recommended scope

### Phase 1: Read-only provider

- Add a shared `kite` quote/history adapter in `server.py`.
- Map `.NS` symbols to `NSE:<tradingsymbol>` and `.BO` symbols to
  `BSE:<tradingsymbol>` through shared region-aware helpers.
- Fetch and persist the daily instrument dump. Use
  `exchange + tradingsymbol` as the durable key because instrument tokens may
  be reused after derivative expiry.
- Use snapshot quotes for initial render and the official WebSocket client for
  the live edge.
- Persist historical candles in the existing local cache. Calculate 5-day and
  25-day moving averages from that point-in-time series.
- Preserve the current fallback chain and label every value with provider,
  timestamp, freshness, and fallback state.

### Phase 2: Reliability

- Maintain one server-side WebSocket connection and fan normalized ticks into
  the dashboard's existing server-sent-event stream.
- Use bounded reconnects with jitter and a visible degraded/fallback state.
- Download the instrument manifest once each trading day, ideally after the
  documented morning refresh, rather than on every dashboard load.
- Add centralized throttling. Treat quote snapshots as one request per second
  and historical candles as three requests per second unless current Zerodha
  documentation specifies a lower limit.
- Handle missing instruments individually; do not fail the whole watchlist.

### Phase 3: Optional account context

Portfolio and margin endpoints should remain a separate, explicit feature flag.
They are not needed for predictions and expose more sensitive account data.
Keep them disabled until the read-only market-data adapter is stable.

Order, GTT, and alert-management endpoints are out of scope. If they are ever
added, they need a separate threat review, explicit user confirmation for every
order, an emergency kill switch, audit records, and isolation from prediction
output.

## Authentication design

Kite does not permit the API to be called directly from the browser. The
backend must own the complete token exchange:

1. `GET /api/providers/kite/login` creates a cryptographically random,
   short-lived state value and redirects to Kite's public login page.
2. Zerodha redirects to the registered local callback with a one-time
   `request_token`.
3. `GET /api/providers/kite/callback` validates the state and immediately
   exchanges the request token with `api_key + api_secret`.
4. The backend stores the access token only in an ignored local file with mode
   `0600`, or in an operating-system secret store.
5. Browser responses expose only booleans such as `kiteConfigured` and
   `kiteSessionActive`.

The API secret, request token, access token, checksum, client ID, holdings,
positions, and margins must never appear in:

- `app.js`, `index.html`, browser local storage, or query strings owned by this
  dashboard;
- application logs, screenshots, error payloads, analytics, or source labels;
- Git commits, GitHub Actions variables printed to logs, issue text, or chat.

Kite access tokens expire at 6 AM the next day unless invalidated earlier, so
the dashboard should expect one manual Zerodha login per day. Do not automate
the user's password, PIN, TOTP, or login form.

## Steps for the user

Do these steps only; do not send the resulting credentials through chat:

1. Confirm that the Zerodha account is active and TOTP two-factor
   authentication is enabled.
2. Sign in at [Kite Connect Developer](https://developers.kite.trade/) and
   choose the **Connect** plan if the dashboard needs live WebSocket quotes and
   historical candles. Zerodha currently lists it at ₹500 per app per month;
   the free Personal plan does not include those data feeds.
3. Create an app named something like `Financial Board Local`.
4. Enter the Zerodha client ID requested by the developer portal.
5. Set the redirect URL to:

   ```text
   http://127.0.0.1:8000/api/providers/kite/callback
   ```

   Zerodha permits `http://127.0.0.1` for local testing. Use HTTPS for any
   non-loopback deployment.
6. Leave the postback URL empty for the read-only integration.
7. Save the generated API key and API secret in a password manager. Do not add
   them to this repository, a screenshot, a shell-history command, or a GitHub
   secret until the backend adapter is ready.
8. Tell the developer only that the app is created and the redirect URL is
   accepted. The backend login/callback routes can then be implemented.
9. After implementation, enter credentials through the local settings flow or
   operating-system environment—not by editing tracked source files.
10. Complete the Zerodha login once per trading day and verify that the
    dashboard labels Kite data with a current exchange timestamp.

## Security acceptance criteria

- A repository safety check blocks common credentials and all local market-data
  paths before push.
- Kite secrets and session material are ignored by Git and stored with mode
  `0600`.
- The browser can never retrieve a raw Kite secret or access token.
- OAuth-style callback state is random, single-use, and expires quickly.
- Only `api.kite.trade`, `kite.zerodha.com`, and `ws.kite.trade` are allowlisted
  for the provider.
- Redirects are not followed during the server-side token exchange.
- Logs redact authorization headers, tokens, checksums, user IDs, and account
  payloads.
- Rate limits, retries, and circuit breakers are centralized.
- Tests cover token redaction, callback-state validation, symbol mapping,
  fallback behavior, stale timestamps, and partial provider failure.
- Market-data integration remains separate from order execution.
