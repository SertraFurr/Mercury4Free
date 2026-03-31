import uuid
import json
import time
import requests

class MercuryClient:
    def __init__(self, base_url="https://chat.inceptionlabs.ai"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session_token = None
        self._setup_headers()
        self.refresh_session()

    def _setup_headers(self):
        self.session.headers.update({
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'Origin': self.base_url,
            'Referer': f"{self.base_url}/",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        })

    def refresh_session(self):
        try:
            r = self.session.get(f"{self.base_url}/api/session", timeout=10)
            if r.ok:
                data = r.json()
                token = data.get("token")
                if token:
                    self.session_token = token
                    self.session.headers["x-session-token"] = token
                    return True
        except Exception:
            pass
        return False

    def stream_chat(self, messages, model="mercury-2", reasoning_effort="medium", web_search_enabled=False):
        if reasoning_effort not in ["instant", "low", "medium", "high"]:
            raise ValueError(f"reasoning_effort must be one of ['instant', 'low', 'medium', 'high'], got '{reasoning_effort}'")
        if not self.session_token:
            if not self.refresh_session():
                yield "error", "Failed to obtain session token."
                return

        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "id": str(uuid.uuid4())[:16],
                "role": msg.get("role", "user"),
                "parts": [{"type": "text", "text": msg.get("content", "")}]
            })

        payload = {
            "reasoningEffort": reasoning_effort,
            "webSearchEnabled": web_search_enabled,
            "voiceMode": False,
            "id": str(uuid.uuid4())[:16],
            "messages": formatted_messages,
            "trigger": "submit-message"
        }

        try:
            r = self.session.post(
                f"{self.base_url}/api/chat", 
                json=payload, 
                stream=True,
                timeout=60
            )

            if r.status_code == 401:
                if self.refresh_session():
                    r = self.session.post(f"{self.base_url}/api/chat", json=payload, stream=True, timeout=60)
            
            r.raise_for_status()

            for line in r.iter_lines():
                if not line:
                    continue
                
                decoded_line = line.decode('utf-8', errors='ignore').strip()
                if decoded_line.startswith("data: "):
                    content = decoded_line[6:].strip()
                    
                    if content == "[DONE]":
                        yield "done", ""
                        break
                        
                    try:
                        msg_data = json.loads(content)
                        msg_type = msg_data.get("type")
                        
                        if msg_type == "text-delta":
                            yield "text", msg_data.get("delta", "")
                        elif msg_type == "reasoning-delta":
                            yield "reasoning", msg_data.get("delta", "")
                        elif msg_type == "reasoning-start":
                            yield "reasoning_start", msg_data
                        elif msg_type == "reasoning-end":
                            yield "reasoning_end", msg_data
                        elif msg_type == "text-start":
                            yield "text_start", msg_data
                        elif msg_type == "text-end":
                            yield "text_end", msg_data
                        else:
                            yield "debug", msg_data
                            
                    except json.JSONDecodeError:
                        continue

        except requests.exceptions.HTTPError as he:
            yield "error", f"HTTP Error {he.response.status_code}: {he.response.text[:200]}"
        except Exception as e:
            yield "error", f"Stream Error: {e}"

    def send_message(self, prompt, model="mercury-2", history=None, reasoning_effort="medium"):
        messages = history or []
        messages.append({"role": "user", "content": prompt})
        
        full_text = ""
        full_reasoning = ""
        
        for msg_type, delta in self.stream_chat(messages, model=model, reasoning_effort=reasoning_effort):
            if msg_type == "text":
                full_text += delta
            elif msg_type == "reasoning":
                full_reasoning += delta
            elif msg_type == "error":
                full_text += f"\n[API ERROR: {delta}]"
                
        full_text = full_text.replace("\u202f", " ").replace("\u200b", "").replace("\u00a0", " ")
        return full_text
