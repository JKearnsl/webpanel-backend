from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi import status as http_status
from fastapi.websockets import WebSocket
from fastapi.responses import HTMLResponse  # remove

from src.dependencies.services import get_services
from src.services import ServiceFactory


router = APIRouter()


@router.websocket("/ws")
async def stat_ws(websocket: WebSocket, services: ServiceFactory = Depends(get_services)):
    await services.stats.subscribe_to_stats(websocket)


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <button onclick="connect()">Connect to WS</button>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            let ws;
            function connect(){
                ws = new WebSocket("ws://127.0.0.1:8000/api/v1/stats/ws");
                ws.onmessage = async function(event) {
                    const messages = document.getElementById('messages')
                    const message = document.createElement('li')
                    
                    const str_data = await event.data.text()
                    const json_data = JSON.parse(str_data)
                    
                    const content = document.createTextNode(str_data);
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                ws.onclose = function (event) {
                    console.log('Socket is closed.', event.reason, event.code);
                    alert(event.code + ' ' + event.reason);
                };
            }
            
            
            function sendMessage(event) {
                const input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@router.get("/test", status_code=http_status.HTTP_200_OK)
async def test(request: Request):
    return HTMLResponse(html)
