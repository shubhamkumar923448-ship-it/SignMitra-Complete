import edge_tts
import base64

async def generate_audio_base64(text: str, voice: str = "en-IN-NeerjaNeural"):
    if not text or text.strip() == "":
        return None
        
    try:
        # rate="+15%" lagaya hai taaki AI thoda jaldi bole, jisse response snappy lage
        communicate = edge_tts.Communicate(text, voice, rate="+15%")
        
        # 🟢 Seedha RAM (Memory) me audio collect karenge, Hard Disk ka use 0%
        audio_data = bytearray()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.extend(chunk["data"])
                
        if audio_data:
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            return f"data:audio/mp3;base64,{audio_b64}"
            
        return None
        
    except Exception as e:
        print(f"TTS Error: {e}")
        return None