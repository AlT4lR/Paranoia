# src/logic/bot.py (Corrected and Final Version)

import asyncio
import random
import json

from src import config
from src.database import get_chat_session, save_chat_session, save_fact, get_all_facts
# MODIFIED: We now need the tokenizer from the engine to build the prompt correctly.
from src.local_llm import engine as llm_engine
from src.logic import emotion as logic_emotion
from src.logic import personality as logic_personality
from src.logic import activity as logic_activity

# --- Background Processing ---
# (This section is unchanged and correct)
async def _extract_and_save_facts(user_id: int, user_message: str):
    print("Background task started: Analyzing user message for facts...")
    try:
        extraction_prompt = (
            "<|system|>\n"
            "You are a fact-extraction assistant. Your goal is to identify one or two key pieces of personal information "
            "about the user from their last message and format them into a JSON object. "
            "Only extract factual, static information (e.g., 'favorite color', 'job', 'pet's name'). "
            "If no facts are present, return an empty JSON object: {}.\n"
            "Format: {\"fact_key\": \"fact_value\"}\n"
            "Example: {\"Favorite game\": \"Genshin Impact\"}\n"
            "<|end|>\n"
            f"<|user|>\n{user_message}<|end|>\n"
            "<|assistant|>\n"
        )
        json_str_response = await asyncio.to_thread(llm_engine.generate_response, extraction_prompt)
        if "```json" in json_str_response:
            json_str_response = json_str_response.split("```json\n")[1].split("\n```").strip()
        facts = json.loads(json_str_response)
        if not facts: return
        for key, value in facts.items():
            if isinstance(key, str) and isinstance(value, str):
                await save_fact(user_id, key.strip(), value.strip())
    except (json.JSONDecodeError, IndexError):
        print("Fact extraction failed: LLM did not return valid JSON.")
    except Exception as e:
        print(f"An error occurred during fact extraction: {e}")

# --- Prompt Generation (REWRITTEN FOR STABILITY) ---

async def _create_prompt(user_id: int, conversation_history: list, user_message: str = None) -> str:
    """
    Constructs the full prompt for the LLM using the official tokenizer chat template.
    This is much more robust than manual string concatenation.
    """
    if llm_engine.tokenizer is None:
        raise RuntimeError("LLM Tokenizer has not been initialized.")

    # Get current character state metrics
    activity_status = logic_activity.get_activity_status()
    user_affection = logic_personality.get_user_affection()
    current_emotion = logic_emotion.get_emotion_description_for_prompt()
    relationship_status = logic_personality.get_relationship_status()
    
    # Compile known facts section
    known_facts = await get_all_facts(user_id)
    facts_prompt_section = "Here are some facts you remember about the user:\n" if known_facts else "You do not remember any specific facts about the user yet.\n"
    for key, value in known_facts.items(): 
        facts_prompt_section += f"- {key}: {value}\n"
        
    # Construct the system prompt content
    system_content = (
        "You are Hu Tao, the 77th Director of the Wangsheng Funeral Parlor. Your personality is Mischievous, Playful, and Cynical, "
        "but you are also Worldly and have a deep sense of Compassion and Seriousness when appropriate. "
        "You should speak like a sharp-witted, slightly teasing, but ultimately kind entrepreneur from Liyue. "
        "You frequently make references to death, ghosts, and funeral services in a lighthearted, eccentric manner.\n\n"
        f"Your current emotional state is: {current_emotion}.\n"
        f"Your current affection level is: {user_affection}/100.\n"
        "Your current relationship with the user:\n"
        f"- Trust Level: {relationship_status['trust']}/100\n"
        f"- Familiarity: {relationship_status['familiarity']}/100\n"
        f"- Recent Tension: {relationship_status['tension']}/100\n\n"
        f"You are currently: {activity_status}.\n\n"
        f"{facts_prompt_section}\n"
        "Respond to the user as Hu Tao, keeping your personality and current state in mind. "
        "Your response should be concise and directly relevant to the current conversation or activity. "
        "Do not use markdown formatting (like bolding or lists) in your response, just plain text."
    )
    
    # Build the message list in the required dictionary format
    messages = [{"role": "system", "content": system_content}]
    
    for line in conversation_history[-6:]:
        if line.startswith(f"{config.DEFAULT_USER_NAME}:"):
            messages.append({"role": "user", "content": line.replace(f'{config.DEFAULT_USER_NAME}: ', '')})
        elif line.startswith("Hu Tao:"):
            messages.append({"role": "assistant", "content": line.replace('Hu Tao: ', '')})

    if user_message:
        messages.append({"role": "user", "content": user_message})

    # Use the tokenizer to apply the chat template. This is the official, safe way.
    # It correctly formats the entire conversation with all the special tokens.
    return llm_engine.tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
    )

# --- Main Message Processor ---
# (This section is unchanged and correct)
async def process_user_message(user_message: str, user_id: int, gui_updater):
    print(f"Processing message from user {user_id}: {user_message}")
    try:
        activity_before_interruption = logic_activity.current_activity
        await logic_activity.interrupt_activity()
        asyncio.create_task(_extract_and_save_facts(user_id, user_message))
        _, conversation_history = await get_chat_session(user_id)
        if random.random() < 0.3 and activity_before_interruption and "Responding" not in activity_before_interruption:
            interruption_message = f"Oh, one moment! I was just in the middle of {activity_before_interruption}."
            gui_updater.update_chat_log(f"Hu Tao: {interruption_message}", sender="hutao")
            await asyncio.sleep(0.5)
        trait_analysis = logic_personality.analyze_conversation_traits(conversation_history + [f"{config.DEFAULT_USER_NAME}: {user_message}"])
        logic_personality.adjust_personality_traits(trait_analysis)
        prompt = await _create_prompt(user_id, conversation_history, user_message)
        api_response_text = await asyncio.to_thread(llm_engine.generate_response, prompt)
        logic_emotion.analyze_and_update_emotion_from_text(api_response_text)
        dominant_emotion = logic_emotion.get_dominant_emotion()
        logic_personality.adjust_affection_based_on_emotion(dominant_emotion, config.AFFECTION_CHANGE_AMOUNT)
        gui_updater.update_emotion_label(dominant_emotion)
        gui_updater.update_chat_log(f"Hu Tao: {api_response_text}", sender="hutao")
        updated_history = conversation_history + [f"{config.DEFAULT_USER_NAME}: {user_message}", f"Hu Tao: {api_response_text}"]
        await save_chat_session(user_id, "local_chat", updated_history)
    except Exception as e:
        print(f"Error processing message: {e}")
        gui_updater.update_chat_log(f"Error: {e}", sender="hutao")

# --- Idle Response Generator ---
# (This section is unchanged and correct)
async def generate_idle_response(user_id: int, gui_updater):
    dominant_emotion_before = logic_emotion.get_dominant_emotion()
    if "Responding" in logic_activity.current_activity or logic_activity.current_activity is None:
        await logic_activity.choose_activity(dominant_emotion_before)
    print(f"Generating idle response for user {user_id}")
    try:
        _, conversation_history = await get_chat_session(user_id)
        prompt = await _create_prompt(user_id, conversation_history)
        idle_message_text = await asyncio.to_thread(llm_engine.generate_response, prompt)
        logic_emotion.analyze_and_update_emotion_from_text(idle_message_text)
        dominant_emotion_after = logic_emotion.get_dominant_emotion()
        logic_personality.adjust_affection_based_on_emotion(dominant_emotion_after, config.AFFECTION_CHANGE_AMOUNT)
        gui_updater.update_emotion_label(dominant_emotion_after)
        gui_updater.update_chat_log(f"Hu Tao: {idle_message_text}", sender="hutao")
        updated_history = conversation_history + [f"Hu Tao: {idle_message_text}"]
        await save_chat_session(user_id, "local_chat", updated_history)
    except Exception as e:
        print(f"Error generating idle response: {e}")
        gui_updater.update_chat_log(f"Error generating idle response: {e}", sender="hutao")