import asyncio
import random
import json

from src import config
from src.database import get_chat_session, save_chat_session, save_fact, get_all_facts
from src.local_llm import engine as llm_engine
from src.logic import emotion as logic_emotion
from src.logic import personality as logic_personality
from src.logic import activity as logic_activity

# --- Background Processing ---

async def _extract_and_save_facts(user_id: int, user_message: str):
    """
    Background task to analyze the user message, extract facts, and save them to the database.
    """
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
        
        # Call LLM in a thread to avoid blocking the asyncio loop
        json_str_response = await asyncio.to_thread(llm_engine.generate_response, extraction_prompt)
        
        # Clean up the response to isolate the JSON string
        if "```json" in json_str_response:
            json_str_response = json_str_response.split("```json\n")[1].split("\n```")[0].strip()
        
        facts = json.loads(json_str_response)
        
        if not facts: 
            return
            
        for key, value in facts.items():
            if isinstance(key, str) and isinstance(value, str):
                await save_fact(user_id, key.strip(), value.strip())
                
    except (json.JSONDecodeError, IndexError):
        print("Fact extraction failed: LLM did not return valid JSON.")
    except Exception as e:
        print(f"An error occurred during fact extraction: {e}")

# --- Prompt Generation ---

async def _create_prompt(user_id: int, conversation_history: list, user_message: str = None) -> str:
    """
    Constructs the full prompt for the LLM, including persona, state, and history.
    """
    
    # Get current character state metrics
    activity_status = logic_activity.get_activity_status()
    user_affection = logic_personality.get_user_affection()
    current_emotion = logic_emotion.get_current_emotion()
    relationship_status = logic_personality.get_relationship_status() # NEW: Get relationship metrics
    
    # Compile known facts section
    known_facts = await get_all_facts(user_id)
    facts_prompt_section = "Here are some facts you remember about the user:\n" if known_facts else "You do not remember any specific facts about the user yet.\n"
    for key, value in known_facts.items(): 
        facts_prompt_section += f"- {key}: {value}\n"
        
    # Construct the system prompt
    system_prompt = (
        "<|system|>\n"
        "You are Hu Tao, the 77th Director of the Wangsheng Funeral Parlor. Your personality is Mischievous, Playful, and Cynical, "
        "but you are also Worldly and have a deep sense of Compassion and Seriousness when appropriate. "
        "You should speak like a sharp-witted, slightly teasing, but ultimately kind entrepreneur from Liyue. "
        "You frequently make references to death, ghosts, and funeral services in a lighthearted, eccentric manner.\n\n"
        
        f"Your current emotional state is: {current_emotion}.\n"
        f"Your current affection level is: {user_affection}/100.\n"
        
        # NEW: Inject relationship status into the prompt
        "Your current relationship with the user:\n"
        f"- Trust Level: {relationship_status['trust']}/100\n"
        f"- Familiarity: {relationship_status['familiarity']}/100\n"
        f"- Recent Tension: {relationship_status['tension']}/100\n\n"
        
        f"You are currently: {activity_status}.\n\n"
        f"{facts_prompt_section}\n"
        
        "Respond to the user as Hu Tao, keeping your personality and current state in mind. "
        "Your response should be concise and directly relevant to the current conversation or activity. "
        "Do not use markdown formatting (like bolding or lists) in your response, just plain text."
        "<|end|>\n"
    )
    
    # Construct history prompt (last 6 turns)
    history_prompt = ""
    for line in conversation_history[-6:]:
        if line.startswith(f"{config.DEFAULT_USER_NAME}:"): 
            history_prompt += f"<|user|>\n{line.replace(f'{config.DEFAULT_USER_NAME}: ', '')}<|end|>\n"
        elif line.startswith("Hu Tao:"): 
            history_prompt += f"<|assistant|>\n{line.replace('Hu Tao: ', '')}<|end|>\n"
            
    # Construct user message prompt
    user_prompt = f"<|user|>\n{user_message}<|end|>\n" if user_message else ""
    
    return system_prompt + history_prompt + user_prompt + "<|assistant|>\n"

# --- Main Message Processor ---

async def process_user_message(user_message: str, user_id: int, gui_updater):
    """Processes a user's message using the local LLM and updates the character state."""
    print(f"Processing message from user {user_id}: {user_message}")

    try:
        # Interrupt the current activity when the user sends a message.
        activity_before_interruption = logic_activity.current_activity
        await logic_activity.interrupt_activity()

        # Start fact extraction in the background
        asyncio.create_task(_extract_and_save_facts(user_id, user_message))

        _, conversation_history = await get_chat_session(user_id)

        # Randomly respond to the interruption to make it feel more natural
        if random.random() < 0.3 and activity_before_interruption and "Responding" not in activity_before_interruption:
            interruption_message = f"Oh, one moment! I was just in the middle of {activity_before_interruption}."
            gui_updater.update_chat_log(f"Hu Tao: {interruption_message}", sender="hutao")
            await asyncio.sleep(0.5)

        # State updates (before generating response for context)
        # Include the new user message in the analysis
        trait_analysis = logic_personality.analyze_conversation_traits(conversation_history + [f"{config.DEFAULT_USER_NAME}: {user_message}"])
        logic_personality.adjust_personality_traits(trait_analysis)
        
        # Generate the response
        prompt = await _create_prompt(user_id, conversation_history, user_message)
        api_response_text = await asyncio.to_thread(llm_engine.generate_response, prompt)
        
        # Post-response state updates
        response_emotion = logic_emotion.analyze_emotion(api_response_text)
        logic_emotion.set_current_emotion(response_emotion)
        logic_personality.adjust_affection_based_on_emotion(response_emotion, config.AFFECTION_CHANGE_AMOUNT)
        
        # Update GUI and save history
        gui_updater.update_emotion_label(logic_emotion.get_current_emotion())
        gui_updater.update_chat_log(f"Hu Tao: {api_response_text}", sender="hutao")
        
        updated_history = conversation_history + [f"{config.DEFAULT_USER_NAME}: {user_message}", f"Hu Tao: {api_response_text}"]
        await save_chat_session(user_id, "local_chat", updated_history)
        
    except Exception as e:
        print(f"Error processing message: {e}")
        gui_updater.update_chat_log(f"Error: {e}", sender="hutao")

# --- Idle Response Generator ---

async def generate_idle_response(user_id: int, gui_updater):
    """Generates an idle response from the local LLM if the character is left alone."""
    
    # If the bot is idle, it should choose a new activity for itself.
    if "Responding" in logic_activity.current_activity or logic_activity.current_activity is None:
        await logic_activity.choose_activity(logic_emotion.get_current_emotion())

    print(f"Generating idle response for user {user_id}")
    try:
        _, conversation_history = await get_chat_session(user_id)
        
        # Generate the response
        prompt = await _create_prompt(user_id, conversation_history)
        idle_message_text = await asyncio.to_thread(llm_engine.generate_response, prompt)

        # Post-response state updates
        idle_emotion = logic_emotion.analyze_emotion(idle_message_text)
        logic_emotion.set_current_emotion(idle_emotion)
        logic_personality.adjust_affection_based_on_emotion(idle_emotion, config.AFFECTION_CHANGE_AMOUNT)
        
        # Update GUI and save history
        gui_updater.update_emotion_label(logic_emotion.get_current_emotion())
        gui_updater.update_chat_log(f"Hu Tao: {idle_message_text}", sender="hutao")
        
        updated_history = conversation_history + [f"Hu Tao: {idle_message_text}"]
        await save_chat_session(user_id, "local_chat", updated_history)
        
    except Exception as e:
        print(f"Error generating idle response: {e}")
        gui_updater.update_chat_log(f"Error generating idle response: {e}", sender="hutao")