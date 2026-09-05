import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
from nlp.prompt_schema import get_system_prompt
import base64

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Flash model lightweight aur fast hai
    model = genai.GenerativeModel('gemini-3.6-flash')
else:
    model = None
    print("⚠️ GEMINI_API_KEY load nahi hui!")

async def process_sign_sequence(raw_words_list, mode="academic"):
    """
    Super-fast asynchronous LLM processing with JSON handling.
    """
    if not model or not raw_words_list:
        return " ".join(raw_words_list)
        
    raw_text = " ".join(raw_words_list)
    system_instruction = get_system_prompt(mode)
    
    prompt = f"{system_instruction}\nInput words: {raw_text}\nOutput sentence:"
    
    try:
        response = await model.generate_content_async(prompt)
        raw_output = response.text.strip()
        
        #  Agar mode teacher_to_student hai, toh JSON parse karo
        if mode in ["teacher_to_student", "smart_finder"]:
            try:
                clean_json_str = raw_output.replace('```json', '').replace('```', '').strip()
                parsed_data = json.loads(clean_json_str)
                
                if mode == "teacher_to_student":
                    polished_text = parsed_data.get("polished_text", raw_output)
                    visual_keywords = parsed_data.get("visual_keywords", [])
                    print(f"🧠 AI Processed JSON: Text='{polished_text}', Keywords={visual_keywords}")
                    return {"text": polished_text, "keywords": visual_keywords}
                
                elif mode == "smart_finder":
                    subject = parsed_data.get("subject_category", "General")
                    query = parsed_data.get("search_query", raw_text)
                    print(f"🔍 Smart Finder JSON: Subject='{subject}', Query='{query}'")
                    return {"subject": subject, "query": query}
                    
            except json.JSONDecodeError:
                print("❌ Failed to parse JSON from Gemini. Fallback to raw text.")
                if mode == "teacher_to_student":
                    return {"text": raw_output, "keywords": []}
                return {"subject": "General", "query": raw_output}
        
        else:
            print(f"🧠 AI Processed: '{raw_text}' ➡️ '{raw_output}'")
            return raw_output
            
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        # Error aane par fallback: tuple me return karo teacher mode ke liye
        if mode == "teacher_to_student":
             return {"text": raw_text, "keywords": []}
        return raw_text

async def process_smart_doubt_on_send(raw_signs_list, typed_text=""):
    """
    Ye function tab chalega jab student 'Send' dabayega.
    Ye background buffer ke signs aur optional typed text ko mila kar ek professional question banayega.
    """
    signs_string = " ".join(raw_signs_list) if raw_signs_list else ""
    
    if not signs_string and not typed_text:
        return "No input provided."

    # Check karo ki input me kya-kya available hai
    if signs_string and typed_text:
        combined_input = f"Sign Language Gestures: '{signs_string}'\nTyped Text: '{typed_text}'"
        instruction = "Combine both inputs intelligently. The sign language shows the core concept and typed text gives specifics. Formulate ONE clear, polite, and professional question directed at the teacher."
    elif signs_string:
        combined_input = f"Sign Language Gestures: '{signs_string}'"
        instruction = "The student used sign language (which may be broken or keyword-based). Understand the core meaning and convert it into a polite, clear, and professional doubt for the teacher."
    else:
        combined_input = f"Typed Text: '{typed_text}'"
        instruction = "Polish this into a clean, professional question for the teacher."

    prompt = f"""
    You are an AI communication bridge for a deaf student in a live classroom.
    {instruction}
    
    Inputs:
    {combined_input}
    
    Constraints:
    - Output ONLY the final refined question sentence as plain text.
    - Do NOT include JSON, markdown, or extra explanations.
    """
    
    try:
        response = await model.generate_content_async(prompt)
        final_doubt = response.text.strip().replace('"', '')
        print(f"🧠 Smart Doubt Generated: {final_doubt}")
        return final_doubt
    except Exception as e:
        print(f"❌ Smart Doubt Error: {e}")
        return f"{signs_string} {typed_text}".strip()

async def process_teacher_reply_multimodal(typed_text, audio_b64=None):
    """
    Teacher ke text aur audio dono ko combine karke Gemini se process karwata hai.
    Gemini audio natively sun sakta hai.
    """
    system_instruction = get_system_prompt("teacher_to_student")
    
    # 🔴 AI ko kya bhejenge uski list banayenge
    prompt_content = [system_instruction]
    
    if typed_text:
        prompt_content.append(f"Teacher Typed Text: '{typed_text}'")
        
    if audio_b64:
        try:
            # Base64 ko bytes me wapas convert karke Gemini ko denge
            audio_bytes = base64.b64decode(audio_b64)
            prompt_content.append({
                "mime_type": "audio/webm", # Frontend WebM bhejta hai
                "data": audio_bytes
            })
            prompt_content.append("Listen to the attached audio recording from the teacher. Combine its meaning with the typed text (if any) to create the final response.")
        except Exception as e:
            print(f"❌ Audio Decode Error: {e}")

    try:
        # Multimodal request Gemini ko bheji
        response = await model.generate_content_async(prompt_content)
        raw_output = response.text.strip()
        
        # Output ko JSON me todna
        clean_json_str = raw_output.replace('```json', '').replace('```', '').strip()
        parsed_data = json.loads(clean_json_str)
        
        polished_text = parsed_data.get("polished_text", raw_output)
        visual_keywords = parsed_data.get("visual_keywords", [])
        
        print(f"🧠 AI Heard & Processed: Text='{polished_text}', Keywords={visual_keywords}")
        
        return {"text": polished_text, "keywords": visual_keywords}
        
    except json.JSONDecodeError:
        print("❌ JSON Parse Failed. Fallback to raw output.")
        return {"text": raw_output, "keywords": []}
    except Exception as e:
        print(f"❌ Multimodal AI Error: {e}")
        return {"text": typed_text or "Please listen to the attached audio.", "keywords": []}

