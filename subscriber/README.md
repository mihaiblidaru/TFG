## Actions supported by the client daemon

### open-session
#### Request
```json
{
    "action": "open-session",
    "params":{
        "host": "127.0.0.1",
        "port": 55555
    }
}
```

#### Responses
```json
{"status": "ok", "session_id":12}
```
```json
{"status": "error"}
```

### close-session
#### Request
```json
{
    "action": "close-session",
    "params":{
        "session_id": 12,
    }
}
```

#### Responses
```json
{"status": "ok"}
```

### get-active-sessions

