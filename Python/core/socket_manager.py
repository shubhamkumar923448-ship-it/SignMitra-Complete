import socketio
import asyncio
import base64
import numpy as np
import cv2
import time 
import json

from vision.landmarks import process_frame_with_mediapipe
from vision.sequence_buffer import SignSequenceBuffer
from vision.sign_classifier import SignLanguageClassifier
from speech.tts import generate_audio_base64
from nlp.context_engine import process_sign_sequence 
from nlp.context_engine import process_teacher_reply_multimodal
from nlp.context_engine import process_smart_doubt_on_send

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

client_sentences = {}
client_cooldown = {} 
client_last_time = {} 
client_last_frame_time = {} 

ai_buffer = SignSequenceBuffer(sequence_length=15)
classifier = SignLanguageClassifier()

@sio.on('connect')
async def connect(sid, environ):
    print(f"🟢 Client Connected [Session: {sid}]")
    client_sentences[sid] = []
    client_cooldown[sid] = 0
    client_last_time[sid] = time.time() 
    client_last_frame_time[sid] = 0
    await sio.emit('system_status', {'message': 'Connected to Neural AI Node'}, to=sid)

@sio.on('disconnect')
async def disconnect(sid):
    client_sentences.pop(sid, None)
    client_cooldown.pop(sid, None)
    client_last_time.pop(sid, None)
    client_last_frame_time.pop(sid, None)

@sio.on('clear_memory')
async def handle_clear_memory(sid):
    client_sentences[sid] = []
    ai_buffer.clear()
    client_last_time[sid] = time.time()
    await sio.emit('translation_result', {'translation': 'Waiting for ISL Gestures...', 'is_final': False}, room=sid)

# ==========================================
# 1. TEACHER TO STUDENT FLOW (Classroom)
# ==========================================
@sio.on('process_teacher_text')
async def handle_teacher_text(sid, data):
    raw_text = data.get('text', '')
    if not raw_text:
        return
        
    print(f"🎤 Teacher Raw Text: {raw_text}")
    
    try:
        result = await process_sign_sequence([raw_text], mode="teacher_to_student")
        final_text = result["text"]
        visual_keywords = result["keywords"]
        
        await sio.emit('teacher_text_polished', {
            'text': final_text, 
            'keywords': visual_keywords
        }, room=sid)
        
    except Exception as e:
        print(f"❌ Teacher NLP Error: {e}")

# ==========================================
# 2. STUDENT FRAME PROCESSOR (Separated Modes for Bridge vs Class)
# ==========================================
async def background_ai_prediction(sid, sequence):
    try:
        new_word = await asyncio.to_thread(classifier.predict_sign, sequence)
        
        if new_word and new_word != "...":
            sentences = client_sentences.get(sid, [])
            
            if not sentences or sentences[-1] != new_word:
                sentences.append(new_word)
                client_last_time[sid] = time.time() 
                client_cooldown[sid] = 15 
                
                await sio.emit('translation_result', {
                    'translation': " ".join(sentences),
                    'is_final': False 
                }, room=sid)
    except Exception as e:
        print(f"Prediction Error: {e}")

@sio.on('process_frame')
async def handle_process_frame(sid, data):
    current_time = time.time()
    
    # 🚀 FPS Limiter (Fast Camera)
    if (current_time - client_last_frame_time.get(sid, 0)) < 0.1:
        return
    client_last_frame_time[sid] = current_time

    # 🔴 FRONTEND SE AAYA HUA CONTEXT (class, bridge, search, doubt)
    client_context = data.get('context', 'class')

    try:
        sentences = client_sentences.get(sid, [])

        # 🔴 SILENCE DETECTOR
        if len(sentences) > 0 and (current_time - client_last_time.get(sid, 0)) > 4.0:
            words_to_process = sentences.copy()
            client_sentences[sid] = [] 
            client_last_time[sid] = current_time 

            # 🟢 SIRF TABHI NLP / VOICE BANAO JAB CLASS YA BRIDGE ME HO
            if client_context in ['class', 'bridge']:
                await sio.emit('translation_result', {'translation': "🤔 Processing...", 'is_final': False}, room=sid)
                print(f"🤫 Silence Detected in '{client_context}' mode! Sending to NLP: {words_to_process}")

                async def enhance_and_speak(raw_words, context_mode):
                    try:
                        # Mitra Bridge ke liye 'casual', baki ke liye 'academic'
                        mode_to_use = "casual" if context_mode == "bridge" else "academic"
                        
                        final_text = await process_sign_sequence(raw_words, mode=mode_to_use)
                        print(f"🌟 AI Translation [{mode_to_use}]: {final_text}")
                        
                        await sio.emit('translation_result', {
                            'translation': final_text,
                            'is_final': True 
                        }, room=sid)

                        audio_data = await generate_audio_base64(final_text)
                        if audio_data:
                            await sio.emit('audio_ready', {'audio': audio_data}, room=sid)
                    except Exception as e:
                        print(f"❌ Background Process Error: {e}")
                
                asyncio.create_task(enhance_and_speak(words_to_process, client_context))
            else:
                # Agar Search ya Doubt khula hai, toh chup chaap buffer clear kar do, AI text mat banao
                print(f"🤫 Silence in '{client_context}' mode. Skipping NLP Audio generation.")

        if client_cooldown.get(sid, 0) > 0:
            client_cooldown[sid] -= 1
            return

        image_data = data.get('image')
        if not image_data: return
            
        encoded_data = image_data.split(',')[1]
        
        processed_image_b64, keypoints, hands_visible = await asyncio.to_thread(
            process_frame_to_base64, encoded_data
        )
        
        if processed_image_b64:
            await sio.emit('translation_result', {'processed_image': processed_image_b64}, room=sid)

            if hands_visible:
                ai_buffer.add_frame(keypoints)

                if ai_buffer.is_ready():
                    sequence = ai_buffer.get_sequence()
                    ai_buffer.clear()
                    asyncio.create_task(background_ai_prediction(sid, sequence))

    except Exception as e:
        pass

def process_frame_to_base64(encoded_data: str):
    try:
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        frame = cv2.resize(frame, (640, 480))
        
        processed_frame, keypoints = process_frame_with_mediapipe(frame)
        
        hands_visible = False
        if keypoints is not None:
            if np.sum(keypoints) > 0.0:
                hands_visible = True

        _, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
        processed_b64 = base64.b64encode(buffer).decode('utf-8')
        
        return f"data:image/jpeg;base64,{processed_b64}", keypoints, hands_visible
    except Exception as e:
        return None, None, False

# ==========================================
# 3. SMART DOUBTS & SEARCH & TRANSCRIPTS
# ==========================================
@sio.on('request_smart_doubt')
async def handle_smart_doubt(sid, data):
    raw_signs = data.get('rawSigns', [])
    typed_text = data.get('typedText', '')
    
    print(f"🧠 Processing Smart Doubt for SID {sid}...")
    polished_doubt = await process_smart_doubt_on_send(raw_signs, typed_text)
    
    await sio.emit('smart_doubt_result', {
        'doubt_text': polished_doubt
    }, room=sid)

@sio.on('request_teacher_reply_enhancement')
async def handle_teacher_reply_enhancement(sid, data):
    raw_text = data.get('text', '')
    audio_b64 = data.get('audio_b64', None) 
    
    print(f"🧠 Processing Multimodal Teacher Reply for SID {sid}...")
    
    if not raw_text.strip() and not audio_b64:
        await sio.emit('teacher_reply_result', {
            'text': "Please provide a text or audio reply.", 
            'keywords': []
        }, room=sid)
        return

    try:
        result = await process_teacher_reply_multimodal(raw_text, audio_b64)
        await sio.emit('teacher_reply_result', {
            'text': result.get("text", raw_text),
            'keywords': result.get("keywords", [])
        }, room=sid)
    except Exception as e:
        print(f"❌ Teacher Reply AI Error: {e}")
        await sio.emit('teacher_reply_result', {'text': raw_text, 'keywords': []}, room=sid)

@sio.on('request_smart_search')
async def handle_smart_search(sid, data):
    raw_signs = data.get('rawSigns', [])
    print(f"🔍 Processing Smart Visual Search for SID {sid}... Signs: {raw_signs}")
    
    if not raw_signs:
        await sio.emit('smart_search_result', {"subject": "General", "query": ""}, room=sid)
        return
        
    try:
        result = await process_sign_sequence(raw_signs, mode="smart_finder")
        await sio.emit('smart_search_result', result, room=sid)
    except Exception as e:
        print(f"❌ Smart Search Error: {e}")
        await sio.emit('smart_search_result', {"subject": "General", "query": " ".join(raw_signs)}, room=sid)

@sio.on('request_lecture_transcript')
async def handle_lecture_transcript(sid, data):
    lecture_title = data.get('title', 'General Lecture')
    subject = data.get('subject', 'Education')
    
    print(f"🎬 Generating AI Transcript for Lecture: {lecture_title} ({subject})")
    
    prompt = f"""
    You are an AI educational synchronizer for deaf students.
    Generate a short, 4-step timestamped transcript sequence for a recorded video titled '{lecture_title}' in subject '{subject}'.
    Return ONLY a valid JSON array of objects with keys: "time_start", "time_end", "text", and a list of "keywords".
    Example format:
    [
      {{"time_start": 0, "time_end": 5, "text": "Welcome to today's module on {lecture_title}.", "keywords": ["welcome", "module"]}},
      {{"time_start": 5, "time_end": 15, "text": "Let us explore the core concepts of {subject}.", "keywords": ["explore", "concepts"]}}
    ]
    """
    
    try:
        response = await model.generate_content_async(prompt)
        raw_output = response.text.strip()
        
        clean_json = raw_output.replace('```json', '').replace('```', '').strip()
        transcript_data = json.loads(clean_json)
        
        await sio.emit('lecture_transcript_result', {'transcript': transcript_data}, room=sid)
        
    except Exception as e:
        print(f"❌ Transcript AI Error: {e}")
        fallback = [
            {"time_start": 0, "time_end": 10, "text": f"Welcome to {lecture_title}.", "keywords": ["welcome"]}
        ]
        await sio.emit('lecture_transcript_result', {'transcript': fallback}, room=sid)