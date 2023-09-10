function getWebSocketProtocol() {
  const protocol = window.location.protocol;
  const isSecure = protocol === "https:";
  const soketprotocol = isSecure ? "wss://" : "ws://";
  const host = window.location.host;
  return `${soketprotocol}//${host}`;
}

function sendMessage(event) {
  var input = document.getElementById("messageText");
  ws.send(input.value);
  input.value = "";
  event.preventDefault();
}

const ws = new WebSocket(`${getWebSocketProtocol()}/views/ws`);
ws.onmessage = function (event) {
  const messages = document.getElementById("messages");
  const message = document.createElement("li");
  const content = document.createTextNode(event.data);
  message.appendChild(content);
  messages.appendChild(message);
};
