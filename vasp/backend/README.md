# diem-reference-merchant
Diem Reference Merchant - A demonstration merchant solution.


### Start docker compose and initial setup
```
mkdir data
docker-compose start
curl -s http://0.0.0.0:8000/supported_currencies

# Insert merchant token
sqlite3 data/vasp.db "INSERT INTO merchant (name,api_key) VALUES ('test_merchant', 'aaaaaaaaaaaaaaaa');"
```

### Generate new payment with random sum and generate UUID as order id
```
PAYMENT_ID=`curl -s http://0.0.0.0:8000/payments \
    -X POST \
    -H "Authorization: Bearer aaaaaaaaaaaaaaaa" \
    -H "Content-Type: application/json" \
    --data "{\"amount\": $RANDOM, \"requested_currency\": \"XUS\", \"merchant_reference_id\": \"$(uuidgen)\"}"  | jq -r '.["payment_id"]'`
```

### Generate new payment, get link to payment HTML
```
curl -s http://0.0.0.0:8000/payments \
    -X POST \
    -H "Authorization: Bearer aaaaaaaaaaaaaaaa" \
    -H "Content-Type: application/json" \
    --data "{\"amount\": $RANDOM, \"requested_currency\": \"XUS\", \"order_id\": \"$(uuidgen)\"}"  | jq -r '.["payment_form_url"]'
```

### Payment status endpoint
```
curl -s http://0.0.0.0:8000/$PAYMENT_ID/status \
    -H "Authorization: Bearer aaaaaaaaaaaaaaaa" \
    -H "Content-Type: application/json"
```

### Payment page
```
curl -s http://0.0.0.0:8000/$PAYMENT_ID \
    -H "Authorization: Bearer aaaaaaaaaaaaaaaa" \
    -H "Content-Type: application/json"
```
