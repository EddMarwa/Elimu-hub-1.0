export function connectWebSocket(url: string, onMessage: (msg: any) => void) {
  const ws = new WebSocket(url);
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch {}
  };
  return ws;
} 