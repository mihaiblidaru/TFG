## Actions supported by the client daemon

### open-session
#### Request
```json
{
    "action": "open-session",
    "params":{
        "host": "127.0.0.1",
        "port": 55555,
        "usename": "admin",
        "password": "admin"
    }
}
```

#### Responses
```json
{"status": "ok", "session_id":12}
```
```json
{
    "status": "error",
    "msg": "The cause of the error"
}
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



### get-full-client-info
#### Request
```json
{
    "action": "get-full-client-info",
}
```

#### Responses
```json
{"status": "ok", 
    "sesions":[
        {
            "session_id": 1,
            "host": "127.0.0.1",
            "subscriptions":[
                {
                    "sub_id": 1,
                },
                {
                    "sub_id": 2,
                }
            ]
        }
    ]
    }
```
```json
{
    "status": "error",
    "msg": "The cause of the error"
}
```