import json
import re
import time
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st

#set up titles, layout, styles, etc.
st.set_page_config(page_title="My AI Chat", layout="wide", initial_sidebar_state="expanded")


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');

:root {
    --app-bg: #071638;
    --panel-bg: #13264a;
    --panel-border: #2b4068;
    --surface-bg: #0c2045;
    --surface-soft: #1a2d4f;
    --text-main: #e8edf7;
    --text-muted: #b5c2d9;
    --accent-red: #ef4444;
}

html, body, [class*="css"] {
    font-family: "Manrope", sans-serif;
}

[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
    height: 100vh;
    overflow: hidden;
}

[data-testid="stAppViewContainer"] {
    background: #0f172a;
    color: var(--text-main);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a2b4b 0%, #172740 100%);
    border-right: 1px solid var(--panel-border);
    min-width: 330px;
    max-width: 330px;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    padding-top: 0.75rem;
}

[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: var(--text-main) !important;
}

.block-container {
    padding-top: 0.9rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1400px;
    height: calc(100vh - 0.9rem);
    overflow: hidden;
}

.hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    color: #f4f7ff;
    margin: 0.15rem 0 0.55rem 0;
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    font-size: 0.94rem;
    line-height: 1.45;
}

[data-testid="stChatMessageContent"] p,
[data-testid="stChatMessageContent"] li {
    font-size: 0.93rem;
    line-height: 1.4;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid #c9d4eb !important;
    border-radius: 0 !important;
    background: transparent !important;
    padding: 0.55rem 0.65rem 0.65rem 0.65rem !important;
    margin-bottom: 0 !important;
    overflow-y: scroll !important;
    scrollbar-gutter: stable;
    overscroll-behavior: contain;
}

[data-testid="stVerticalBlockBorderWrapper"]::-webkit-scrollbar {
    width: 10px;
}

[data-testid="stVerticalBlockBorderWrapper"]::-webkit-scrollbar-track {
    background: #0d1f42;
}

[data-testid="stVerticalBlockBorderWrapper"]::-webkit-scrollbar-thumb {
    background: #395784;
    border-radius: 8px;
}

[data-testid="stVerticalBlockBorderWrapper"]::-webkit-scrollbar-thumb:hover {
    background: #4b6e9f;
}

[data-testid="stChatInput"] {
    background: var(--surface-soft);
    border: 1px solid #c9d4eb;
    border-radius: 0;
    padding-left: 0.45rem;
    padding-right: 0.45rem;
    margin-top: -1px;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input {
    color: var(--text-main) !important;
}

[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInput"] input::placeholder {
    color: var(--text-muted) !important;
}

[data-testid="stChatInput"] button svg {
    transform: rotate(-90deg);
}

[data-testid="stButton"] > button {
    border-radius: 10px;
    border: 1px solid #3b4f75;
    background: #22375a;
    color: #eef3ff;
    font-weight: 600;
}

[data-testid="stButton"] > button:hover {
    border-color: #5f79a5;
    background: #2b436a;
}

[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="primary"] {
    background: #334f7d;
    border-color: #597db5;
}

[data-testid="stSidebar"] [data-testid="stExpanderDetails"] [data-testid="stButton"]:first-of-type button {
    background: var(--accent-red);
    border-color: #f87171;
    color: #fff7f7;
}

[data-testid="stSidebar"] [data-testid="column"]:last-child [data-testid="stButton"] > button {
    background: #ef4444 !important;
    border-color: #f87171 !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    min-height: 2.1rem;
    font-weight: 800;
}

[data-testid="stSidebar"] [data-testid="column"]:last-child [data-testid="stButton"] > button:hover {
    background: #dc2626 !important;
    border-color: #fca5a5 !important;
}

[data-testid="stSidebar"] [data-testid="stHeading"] {
    margin-bottom: 0.45rem;
}

[data-testid="stSidebar"] [data-testid="stExpander"] {
    border: 1px solid var(--panel-border);
    border-radius: 12px;
    background: #172b4b;
}

[data-testid="stSidebar"] [data-testid="stExpanderDetails"] {
    background: #132440;
}

[data-testid="stSidebar"] [data-testid="stJson"] {
    border-radius: 10px;
    border: 1px solid #2c4570;
}

[data-testid="stSidebar"] hr {
    border-color: #334b74 !important;
}

.chat-time-label {
    color: #b8c7df;
    font-size: 0.78rem;
    text-align: right;
    margin-top: 0.45rem;
    white-space: nowrap;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown('<h1 class="hero-title">My AI Chat</h1>', unsafe_allow_html=True)

#stores hard information
API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL_NAME = "meta-llama/Llama-3.2-1B-Instruct"
BASE_DIR = Path(__file__).resolve().parent
CHATS_DIR = BASE_DIR / "chats"
MEMORY_FILE = BASE_DIR / "memory.json"
STREAM_DELAY_SECONDS = 0.01
CANONICAL_MEMORY_KEYS = {
    "name",
    "preferred_language",
    "interests",
    "communication_style",
    "favorite_topics",
}

#keeps consistent date-time formatting
def now_label():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

#formats sidebar timestamp labels for recent chats
def format_sidebar_timestamp(timestamp, is_active):
    if is_active:
        return "Now"
    if not isinstance(timestamp, str) or timestamp.strip() == "":
        return ""
    try:
        parsed = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
        return parsed.strftime("%b %d")
    except ValueError:
        return timestamp

def sanitize_generated_title(title_text):
    if not isinstance(title_text, str):
        return ""
    cleaned = title_text.strip().replace("\n", " ")
    cleaned = re.sub(r"^['\"`]+|['\"`]+$", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(r"[^A-Za-z0-9\s&'-]", "", cleaned)
    if cleaned == "":
        return ""
    words = cleaned.split()
    if len(words) > 6:
        words = words[:6]
    return " ".join(words)[:42]

def singularize_simple(word):
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word

def is_weak_chat_title(title_text):
    title = sanitize_generated_title(title_text).lower()
    if title in {"", "new chat", "chat", "untitled", "untitled chat"}:
        return True
    words = title.split()
    if len(words) < 2:
        return True
    weak_words = {"help", "question", "chat", "thing", "stuff", "task"}
    if all(word in weak_words for word in words):
        return True
    interrogatives = {"what", "why", "how", "when", "where", "who", "which"}
    if words[0] in interrogatives and len(words) <= 3:
        return True
    return False

def generate_local_chat_title(user_prompt):
    text = user_prompt.strip()
    if text == "":
        return "New Chat"

    lowered = text.lower()
    lowered = re.sub(r"^(hello|hi|hey)\b[\s,!.-]*", "", lowered).strip()
    lowered = re.sub(
        r"^(can you|could you|would you|please|help me|i need|i want to|let's)\b[\s,:-]*",
        "",
        lowered,
    ).strip()
    lowered = re.sub(r"\?$", "", lowered).strip()

    normalized = re.sub(r"[^A-Za-z0-9\s'-]", " ", lowered)
    words = [word for word in normalized.split() if word]
    if not words:
        return "New Chat"

    action_suffix = ""
    action_map = {
        "generate": "Generator",
        "create": "Generator",
        "build": "Generator",
        "make": "Generator",
        "explain": "Guide",
        "teach": "Guide",
        "learn": "Practice",
        "practice": "Practice",
    }
    if words and words[0] in action_map:
        action_suffix = action_map[words[0]]
        words = words[1:]

    stop_words = {
        "a", "an", "and", "are", "as", "at", "be", "can", "do", "for", "from",
        "could", "would", "should", "some", "any", "just",
        "hello", "hey", "hi", "name", "chat",
        "get", "help", "how", "i", "im", "i'm", "in", "is", "it", "me", "my",
        "of", "on", "or", "please", "that", "the", "this", "to", "we", "with",
        "you", "your", "can", "could", "would",
    }
    candidates = [word for word in words if len(word) > 2 and word not in stop_words]
    if not candidates:
        candidates = [word for word in words if len(word) > 1]
    if not candidates and action_suffix:
        return action_suffix
    if not candidates:
        return "New Chat"

    title_words = candidates[:3]
    if action_suffix:
        title_words = [singularize_simple(word) for word in title_words[:2]]
        title_words.append(action_suffix.lower())
    title = " ".join(title_words).title()
    title = sanitize_generated_title(title)
    return title if title else "New Chat"

def generate_model_chat_title(headers, user_prompt):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Create a short chat title (2 to 5 words). "
                    "Use title case. Return title text only."
                ),
            },
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 20,
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code != 200:
            return None
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        candidate = sanitize_generated_title(content)
        if candidate == "":
            return None
        word_count = len(candidate.split())
        if word_count < 2 or word_count > 5:
            return None
        return candidate
    except Exception:
        return None

def generate_chat_title_from_prompt(user_prompt, headers):
    local_title = generate_local_chat_title(user_prompt)
    if not is_weak_chat_title(local_title):
        return local_title
    model_title = generate_model_chat_title(headers, user_prompt)
    if model_title:
        return model_title
    # Prevent weak titles like "What" when model fallback is unavailable.
    return "New Chat"

#creates a new chat with unique id, applies date-time, and returns information in dictinary format
def make_new_chat():
    chat_id = f"chat_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    return {
        "id": chat_id,
        "title": "New Chat",
        "timestamp": now_label(),
        "messages": [],
    }

#creates directory for new chats and path ( for chat id) is returned appropriately
def ensure_chats_dir():
    CHATS_DIR.mkdir(parents=True, exist_ok=True)

def chat_file_path(chat_id):
    return CHATS_DIR / f"{chat_id}.json"

#saves chat to disk (in json format) with the chat id
def save_chat(chat):
    path = chat_file_path(chat["id"])
    with path.open("w", encoding="utf-8") as file:
        json.dump(chat, file, indent=2)

#deletes chat from disk (removing it from json) through clicking x on sidebar
def delete_chat_file(chat_id):
    path = chat_file_path(chat_id)
    if path.exists():
        path.unlink()

#makes sure messages are correctly formatted as list of dictionaries, and have strings
def is_valid_messages(messages):
    if not isinstance(messages, list):
        return False
    for item in messages:
        if not isinstance(item, dict):
            return False
        if "role" not in item or "content" not in item:
            return False
        if not isinstance(item["role"], str) or not isinstance(item["content"], str):
            return False
    return True

#loads chats from disk, makes sure its valid, and if not returns error
def load_chats_from_disk():
    loaded = []
    warnings = []
    ensure_chats_dir()
    for path in sorted(CHATS_DIR.glob("*.json"), reverse=True):
        try:
            with path.open("r", encoding="utf-8") as file:
                chat = json.load(file)
        except Exception:
            warnings.append(f"Skipped malformed file: {path.name}")
            continue
#here it validates structure of chat making sure all components are good
        chat_id = chat.get("id")
        title = chat.get("title")
        timestamp = chat.get("timestamp")
        messages = chat.get("messages")
        valid_id = isinstance(chat_id, str) and chat_id.strip() != ""
        valid_title_or_time = (
            isinstance(title, str) and title.strip() != ""
        ) or (
            isinstance(timestamp, str) and timestamp.strip() != ""
        )
#invalid id handled by warning and will continue to next using default values
        if not valid_id or not valid_title_or_time or not is_valid_messages(messages):
            warnings.append(f"Skipped invalid chat structure: {path.name}")
            continue
        if not isinstance(title, str) or title.strip() == "":
            title = "Untitled Chat"
        if not isinstance(timestamp, str) or timestamp.strip() == "":
            timestamp = now_label()
        loaded.append(
            {
                "id": chat_id,
                "title": title,
                "timestamp": timestamp,
                "messages": messages,
            }
        )
    return loaded, warnings

#gets information for active chats by matching id and if not matched returns error
def get_active_chat():
    active_id = st.session_state.get("active_chat_id")
    for chat in st.session_state.chats:
        if chat["id"] == active_id:
            return chat
    return None

def load_memory():
    if not MEMORY_FILE.exists():
        return {}
#reads to see if file is valid and in dictionaty format and if not, continues with empty dictionary
    try:
        with MEMORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if key not in CANONICAL_MEMORY_KEYS:
                    continue
                sanitized[key] = value
            return sanitized
    except Exception:
        pass
    return {}

#saves memory from chat to disk in json formatting
def save_memory(memory_dict):
    with MEMORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(memory_dict, file, indent=2)

def clear_memory():
    save_memory({})

def normalize_memory_text(value):
    text = str(value)
    text = re.sub(r"\s+", " ", text).strip(" \t\n\r.,!?;:\"'()[]{}")
    return text

def normalize_list_item(item):
    cleaned = normalize_memory_text(item)
    if cleaned == "":
        return ""
    blocked_terms = {
        "stuff", "things", "something", "anything", "everything",
        "nothing", "it", "that", "this", "more", "less",
    }
    if len(cleaned) < 2:
        return ""
    if cleaned.lower() in blocked_terms:
        return ""
    return cleaned

def split_list_items(raw_text):
    text = normalize_memory_text(raw_text)
    if text == "":
        return []
    # Split comma-separated phrases and simple "and" lists.
    parts = re.split(r",|\band\b", text, flags=re.IGNORECASE)
    cleaned_parts = []
    for part in parts:
        cleaned = normalize_list_item(part)
        if cleaned:
            cleaned_parts.append(cleaned)
    return cleaned_parts

def normalize_for_match(text):
    normalized = str(text).lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized

def simple_singular(word):
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word

def simple_plural(word):
    if len(word) > 2 and not word.endswith("s"):
        return word + "s"
    return word

def phrase_explicitly_in_user_text(normalized_user_text, candidate_text):
    candidate_norm = normalize_for_match(candidate_text)
    if candidate_norm == "":
        return False

    padded_user = f" {normalized_user_text} "
    padded_candidate = f" {candidate_norm} "
    if padded_candidate in padded_user:
        return True

    words = candidate_norm.split()
    if not words:
        return False

    singular_phrase = " ".join(simple_singular(word) for word in words)
    plural_phrase = " ".join(simple_plural(word) for word in words)
    if f" {singular_phrase} " in padded_user:
        return True
    if f" {plural_phrase} " in padded_user:
        return True
    return False

#cleans up text to get json objects easily, formats json, if an error occurs, will return empty dictionary
def parse_json_object_from_text(text):
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()
#parses cleaned json to make sure its in dictionary format
    try:
        parsed = json.loads(cleaned)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        pass
#if above parsing fails, looks for the beginning and last brackets to find any jspn objects (like nesting)
#if that fails too, then returns empty dictionary
#here it begins finding brackets (beginning and end index)
    start_index = cleaned.find("{")
    end_index = cleaned.rfind("}")
    if start_index == -1 or end_index == -1 or end_index <= start_index:
        return {}
    candidate = cleaned[start_index:end_index + 1]
    try:
        parsed = json.loads(candidate)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}

#any changes to memory are incorperated with previous memory, combines lists
#removes repetitions and also handles different data types, and formatting
def merge_memory(existing, updates):
    merged = dict(existing)
    for key, value in updates.items():
        if key not in CANONICAL_MEMORY_KEYS:
            continue
        if isinstance(value, list):
            new_items = []
            for item in value:
                if not isinstance(item, (str, int, float, bool)):
                    continue
                normalized_item = normalize_list_item(item)
                if normalized_item:
                    new_items.append(normalized_item)
            old_value = merged.get(key, [])
            old_items = []
            if isinstance(old_value, list):
                for item in old_value:
                    normalized_item = normalize_list_item(item)
                    if normalized_item:
                        old_items.append(normalized_item)
            combined = old_items + new_items
#here it removes any repeating info and .strip on whitespace, etc.
            deduped = []
            seen = set()
            for item in combined:
                normalized = normalize_memory_text(item)
                dedupe_key = normalized.lower()
                if normalized and dedupe_key not in seen:
                    deduped.append(item)
                    seen.add(dedupe_key)
#only merges if there is info left after cleaning and checking for repetitions
            if deduped:
                merged[key] = deduped
        elif isinstance(value, (str, int, float, bool)):
            if isinstance(value, str):
                cleaned = normalize_memory_text(value)
                if cleaned:
                    merged[key] = cleaned
            else:
                merged[key] = value
    return merged

#checks to see if there is any actural disclosure of name which prevents guesswork from the model
#only updates if specifically stated
def is_plausible_name(name_text):
    if not isinstance(name_text, str):
        return False
    cleaned = name_text.strip()
    if cleaned == "":
        return False
    lower_cleaned = cleaned.lower()

    # Common occupation/context words that should not be treated as names.
    blocked_words = {
        "student", "engineer", "developer", "teacher", "doctor", "nurse",
        "manager", "designer", "accountant", "intern", "professor", "chef",
        "artist", "lawyer", "scientist", "consultant", "from", "old", "years",
    }
    if any(word in lower_cleaned.split() for word in blocked_words):
        return False
    if lower_cleaned.startswith(("a ", "an ", "the ")):
        return False

    # Keep only simple name-like formats (1 to 3 alphabetic words).
    parts = cleaned.split()
    if len(parts) < 1 or len(parts) > 3:
        return False
    for part in parts:
        if not re.fullmatch(r"[A-Za-z][A-Za-z'-]*", part):
            return False
    return True

def has_explicit_name_disclosure(user_message):
    text = user_message.strip()
    lower_text = text.lower()

    explicit_prefixes = ["my name is ", "call me ", "i am ", "i'm "]
    for prefix in explicit_prefixes:
        if prefix in lower_text:
            start_index = lower_text.find(prefix) + len(prefix)
            candidate = text[start_index:].strip()
            # Stop at punctuation so we only evaluate the direct phrase.
            candidate = re.split(r"[.!?,;:\n]", candidate)[0].strip()
            if is_plausible_name(candidate):
                return True
    return False

def get_display_name(memory_data):
    if not isinstance(memory_data, dict):
        return "User"
    stored_name = memory_data.get("name", "")
    if isinstance(stored_name, str) and is_plausible_name(stored_name):
        return normalize_memory_text(stored_name)
    return "User"

#here it checks for any word patterns that may hold personal preferences or information regarding the user
def should_extract_memory(user_message):
    disclosed_keys = get_disclosed_memory_keys(user_message)
    return len(disclosed_keys) > 0

def get_disclosed_memory_keys(user_message):
    text = user_message.strip()
    lowered = text.lower()
    disclosed = set()

    if has_explicit_name_disclosure(text):
        disclosed.add("name")

    if re.search(
        r"\b(i speak|my preferred language is|i prefer .* language)\b",
        lowered,
    ):
        disclosed.add("preferred_language")

    if re.search(
        r"\b(i like|i love|i enjoy|i am interested in|i'm interested in)\b",
        lowered,
    ):
        disclosed.add("interests")

    if re.search(
        r"\b(my favorite topic is|my favorite topics are|i like talking about|i enjoy talking about)\b",
        lowered,
    ):
        disclosed.add("favorite_topics")

    if re.search(
        r"\b(keep it|explain .* step by step|short answers?|detailed answers?|simple language|concise)\b",
        lowered,
    ):
        disclosed.add("communication_style")

    return disclosed

#passes any information that doesnt make approprite guesses, only overwrites when explicitly stated
def filter_memory_updates(user_message, updates):
    disclosed_keys = get_disclosed_memory_keys(user_message)
    filtered = {}
    for key, value in updates.items():
        if key not in CANONICAL_MEMORY_KEYS:
            continue
        if key not in disclosed_keys:
            continue
        # Protect stored name from being overwritten by model guesses.
        if key == "name":
            if not has_explicit_name_disclosure(user_message):
                continue
            cleaned_name = normalize_memory_text(value)
            if not is_plausible_name(cleaned_name):
                continue
            filtered[key] = cleaned_name
            continue
        filtered[key] = value
    return filtered

def extract_memory_updates_fallback(user_message):
    updates = {}
    text = user_message.strip()

    list_patterns = [
        ("interests", r"\b(?:i like|i love|i enjoy)\s+(.+?)(?:[.!?]|$)"),
        ("favorite_topics", r"\b(?:my favorite topics? (?:is|are)|i like talking about)\s+(.+?)(?:[.!?]|$)"),
    ]
    for key, pattern in list_patterns:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        items = []
        for match in matches:
            items.extend(split_list_items(match))
        if items:
            updates[key] = items

    language_match = re.search(r"\bi speak\s+([A-Za-z][A-Za-z\s-]{1,40})(?:[.!?,;]|$)", text, flags=re.IGNORECASE)
    if language_match:
        language_value = normalize_memory_text(language_match.group(1))
        if language_value:
            updates["preferred_language"] = language_value

    style_patterns = [
        r"\bkeep it\s+(.+?)(?:[.!?,;]|$)",
        r"\bexplain\s+(.+?)(?:[.!?,;]|$)",
    ]
    style_hits = []
    for pattern in style_patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            cleaned = normalize_memory_text(match)
            if cleaned:
                style_hits.append(cleaned)
    if re.search(r"\bshort answers?\b", text, flags=re.IGNORECASE):
        style_hits.append("short answers")
    if re.search(r"\bdetailed answers?\b", text, flags=re.IGNORECASE):
        style_hits.append("detailed answers")
    if style_hits:
        updates["communication_style"] = style_hits

    return updates

def extract_explicit_candidates_by_key(user_message):
    text = user_message.strip()
    candidates = {}

    if has_explicit_name_disclosure(text):
        lower_text = text.lower()
        for prefix in ["my name is ", "call me ", "i am ", "i'm "]:
            if prefix in lower_text:
                start_index = lower_text.find(prefix) + len(prefix)
                candidate = text[start_index:].strip()
                candidate = re.split(r"[.!?,;:\n]", candidate)[0].strip()
                cleaned = normalize_memory_text(candidate)
                if cleaned and is_plausible_name(cleaned):
                    candidates["name"] = [cleaned]
                    break

    language_values = []
    language_match = re.search(
        r"\bi speak\s+([A-Za-z][A-Za-z\s-]{1,40})(?:[.!?,;]|$)",
        text,
        flags=re.IGNORECASE,
    )
    if language_match:
        cleaned = normalize_memory_text(language_match.group(1))
        if cleaned:
            language_values.append(cleaned)
    preferred_match = re.search(
        r"\bmy preferred language is\s+([A-Za-z][A-Za-z\s-]{1,40})(?:[.!?,;]|$)",
        text,
        flags=re.IGNORECASE,
    )
    if preferred_match:
        cleaned = normalize_memory_text(preferred_match.group(1))
        if cleaned:
            language_values.append(cleaned)
    if language_values:
        candidates["preferred_language"] = language_values

    interests = []
    for pattern in [r"\b(?:i like|i love|i enjoy)\s+(.+?)(?:[.!?]|$)"]:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        for match in matches:
            interests.extend(split_list_items(match))
    if interests:
        candidates["interests"] = interests

    favorite_topics = []
    for pattern in [
        r"\b(?:my favorite topics? (?:is|are))\s+(.+?)(?:[.!?]|$)",
        r"\b(?:i like talking about|i enjoy talking about)\s+(.+?)(?:[.!?]|$)",
    ]:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        for match in matches:
            favorite_topics.extend(split_list_items(match))
    if favorite_topics:
        candidates["favorite_topics"] = favorite_topics

    style_hits = []
    if re.search(r"\bshort answers?\b", text, flags=re.IGNORECASE):
        style_hits.append("short answers")
    if re.search(r"\bdetailed answers?\b", text, flags=re.IGNORECASE):
        style_hits.append("detailed answers")
    for pattern in [r"\bkeep it\s+(.+?)(?:[.!?,;]|$)", r"\bexplain\s+(.+?)(?:[.!?,;]|$)"]:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            cleaned = normalize_memory_text(match)
            if cleaned:
                style_hits.append(cleaned)
    if style_hits:
        candidates["communication_style"] = style_hits

    return candidates

def enforce_strict_category_mapping(user_message, updates):
    explicit_candidates = extract_explicit_candidates_by_key(user_message)
    if not explicit_candidates:
        return {}

    mapped = {}
    for key, value in updates.items():
        allowed_values = explicit_candidates.get(key)
        if not allowed_values:
            continue

        if isinstance(value, list):
            value_items = [normalize_list_item(item) for item in value]
            value_items = [item for item in value_items if item]
            keep = []
            seen = set()
            for allowed in allowed_values:
                allowed_clean = normalize_list_item(allowed)
                if not allowed_clean:
                    continue
                for item in value_items:
                    if normalize_memory_text(item).lower() == normalize_memory_text(allowed_clean).lower():
                        dedupe = normalize_memory_text(item).lower()
                        if dedupe not in seen:
                            keep.append(item)
                            seen.add(dedupe)
                        break
            if keep:
                mapped[key] = keep
            continue

        if isinstance(value, (str, int, float, bool)):
            cleaned = normalize_memory_text(value)
            for allowed in allowed_values:
                allowed_clean = normalize_memory_text(allowed)
                if cleaned.lower() == allowed_clean.lower():
                    mapped[key] = allowed_clean
                    break

    return mapped

def deterministic_memory_recall_response(user_prompt, memory_data):
    if not isinstance(memory_data, dict):
        memory_data = {}
    text = normalize_for_match(user_prompt)
    if text == "":
        return None

    if ("what is my name" in text) or ("whats my name" in text):
        name = memory_data.get("name")
        if isinstance(name, str) and name.strip():
            return f"Your name is {name}."
        return "I don't know your name yet from your saved memory."

    if ("what language should you use" in text) or ("what language do i speak" in text):
        language = memory_data.get("preferred_language")
        if isinstance(language, str) and language.strip():
            return f"You prefer {language}."
        return "I don't know your preferred language yet from your saved memory."

    if ("what are my interests" in text) or ("what do i like" in text):
        interests = memory_data.get("interests")
        if isinstance(interests, list) and interests:
            return "Your interests are " + ", ".join(interests) + "."
        if isinstance(interests, str) and interests.strip():
            return f"Your interest is {interests}."
        return "I don't know your interests yet from your saved memory."

    if ("what are my favorite topics" in text) or ("what topics do i like" in text):
        topics = memory_data.get("favorite_topics")
        if isinstance(topics, list) and topics:
            return "Your favorite topics are " + ", ".join(topics) + "."
        if isinstance(topics, str) and topics.strip():
            return f"Your favorite topic is {topics}."
        return "I don't know your favorite topics yet from your saved memory."

    if ("guess my age" in text) or ("how old am i" in text):
        return "I don't know your age from your saved memory."

    return None

def combine_model_and_rule_updates(model_updates, rule_updates):
    combined = {}
    model_updates = model_updates if isinstance(model_updates, dict) else {}
    rule_updates = rule_updates if isinstance(rule_updates, dict) else {}

    for key in CANONICAL_MEMORY_KEYS:
        model_value = model_updates.get(key)
        rule_value = rule_updates.get(key)

        if isinstance(model_value, list) or isinstance(rule_value, list):
            merged_list = []
            if isinstance(model_value, list):
                merged_list.extend(model_value)
            if isinstance(rule_value, list):
                merged_list.extend(rule_value)
            if merged_list:
                combined[key] = merged_list
            continue

        # Favor model scalar values unless model scalar is empty.
        if isinstance(model_value, str):
            cleaned = normalize_memory_text(model_value)
            if cleaned:
                combined[key] = cleaned
                continue
        elif isinstance(model_value, (int, float, bool)):
            combined[key] = model_value
            continue

        if isinstance(rule_value, str):
            cleaned = normalize_memory_text(rule_value)
            if cleaned:
                combined[key] = cleaned
        elif isinstance(rule_value, (int, float, bool)):
            combined[key] = rule_value

    return combined

def ground_memory_updates_to_user_text(user_message, updates):
    if not isinstance(updates, dict):
        return {}

    normalized_user_text = normalize_for_match(user_message)
    if normalized_user_text == "":
        return {}

    grounded = {}
    scalar_keys = {"name", "preferred_language"}
    list_keys = {"interests", "favorite_topics", "communication_style"}

    for key, value in updates.items():
        if key not in CANONICAL_MEMORY_KEYS:
            continue

        if key in scalar_keys:
            if not isinstance(value, (str, int, float, bool)):
                continue
            cleaned_value = normalize_memory_text(value)
            if cleaned_value == "":
                continue
            if key == "name" and not is_plausible_name(cleaned_value):
                continue
            if phrase_explicitly_in_user_text(normalized_user_text, cleaned_value):
                grounded[key] = cleaned_value
            continue

        if key in list_keys:
            if isinstance(value, list):
                raw_items = value
            elif isinstance(value, (str, int, float, bool)):
                raw_items = split_list_items(str(value))
            else:
                raw_items = []

            kept_items = []
            seen = set()
            for item in raw_items:
                cleaned_item = normalize_list_item(item)
                if cleaned_item == "":
                    continue
                if not phrase_explicitly_in_user_text(normalized_user_text, cleaned_item):
                    continue
                dedupe_key = normalize_memory_text(cleaned_item).lower()
                if dedupe_key and dedupe_key not in seen:
                    kept_items.append(cleaned_item)
                    seen.add(dedupe_key)
            if kept_items:
                grounded[key] = kept_items

    return grounded

#extracts info to update memory when looking for personal info, and updates when pattern is picked up
def extract_memory_updates(headers, user_message):
    extraction_prompt = (
        "Given this user message, extract personal facts or preferences as JSON. "
        "Allowed keys: name, preferred_language, interests, communication_style, favorite_topics. "
        "For list-like keys (interests, communication_style, favorite_topics), "
        "return arrays of short strings. For scalar keys (name, preferred_language), "
        "return a single string. If no traits are present, return {}. Return JSON only, no extra text.\n\n"
        f"User message: {user_message}"
    )
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Return strict JSON only."},
            {"role": "user", "content": extraction_prompt},
        ],
        "max_tokens": 180,
    }
#if a valid json is not outputted, an empty dictionary will be returned in its place
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            return {}
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return parse_json_object_from_text(content)
    except Exception:
        return {}

#if response is not valid, error is displayed 
def stream_assistant_reply(headers, payload):
    assistant_text = ""
    try:
        with requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=60,
            stream=True,
        ) as response:
            if response.status_code != 200:
                yield None, f"API error ({response.status_code}): {response.text}"
                return
            for raw_line in response.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue
                if not raw_line.startswith("data:"):
                    continue
                event_data = raw_line[len("data:"):].strip()
                if event_data == "[DONE]":
                    break
#continues checking validation of json and if not, will keep going on until finds validity
                try:
                    event_json = json.loads(event_data)
                except json.JSONDecodeError:
                    continue
                choices = event_json.get("choices", [])
                if not choices:
                    continue
#handles different formats for streaming responses
                delta = choices[0].get("delta", {})
                chunk_text = delta.get("content", "")

#fallback for providers that send message or content shape
                if not chunk_text:
                    message = choices[0].get("message", {})
                    chunk_text = message.get("content", "")
                if chunk_text:
                    assistant_text += chunk_text
                    yield assistant_text, None
                    # Make streaming visibly incremental for very fast models.
                    time.sleep(STREAM_DELAY_SECONDS)
    except requests.exceptions.RequestException as error:
        yield None, f"Network/API connection error: {error}"
        return
    if assistant_text.strip() == "":
        yield None, "No response content was returned by the API."
        return
    yield assistant_text, None
#handles token retriving and validation and if missing, displays error and stops until valid token is provided
try:
    hf_token = st.secrets["HF_TOKEN"].strip()
except Exception:
    st.error(
        "Missing HF_TOKEN. Add it to .streamlit/secrets.toml "
        "(or Streamlit Cloud secrets) and rerun."
    )
    st.stop()
if not hf_token:
    st.error(
        "HF_TOKEN is empty. Add a valid Hugging Face token in "
        ".streamlit/secrets.toml and rerun."
    )
    st.stop()

# Part A: hardcoded test call (run once per session)
# Part B: chat UI replaces the Part A hardcoded test call.
#initializes session state from disk (or defaults) for necessary information
if "chats" not in st.session_state:
    loaded_chats, load_warnings = load_chats_from_disk()
    st.session_state.load_warnings = load_warnings
#if there are valid chats from disk, use them and if not start with new ones
    if loaded_chats:
        st.session_state.chats = loaded_chats
    else:
        first_chat = make_new_chat()
        st.session_state.chats = [first_chat]
        save_chat(first_chat)
#None if no chat is there, exists if active chat is going
if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = st.session_state.chats[0]["id"] if st.session_state.chats else None

#if active id is no longer valid it will choose first available chat (if there)
if get_active_chat() is None and st.session_state.chats:
    st.session_state.active_chat_id = st.session_state.chats[0]["id"]
if "memory_data" not in st.session_state:
    st.session_state.memory_data = load_memory()

#creates sidebar with appropriate options under chats
st.sidebar.header("Chats")
if st.sidebar.button("New Chat", use_container_width=True):
#new chat option made and assigned unique chat id and appropriate date-time
    new_chat = make_new_chat()
    st.session_state.chats.insert(0, new_chat)
    st.session_state.active_chat_id = new_chat["id"]
    save_chat(new_chat)
    st.rerun()
for warning_text in st.session_state.get("load_warnings", []):
    st.sidebar.warning(warning_text)
#saves user memory from chats and displays
with st.sidebar.expander("User Memory", expanded=False):
#clear memory option that deletes memory data from disk and UI
    if st.button("Clear Memory", use_container_width=True, type="primary", key="clear_memory_btn"):
        clear_memory()
        st.session_state.memory_data = {}
        st.rerun()

    if st.session_state.memory_data:
        st.json(st.session_state.memory_data)
    else:
        st.caption("No saved user memory yet.")
#create chat list and scrollable sidebar when content is long
st.sidebar.markdown("---")
st.sidebar.subheader("Recent Chats")
for chat in st.session_state.chats:
    is_active = chat["id"] == st.session_state.active_chat_id
    row_left, row_middle, row_right = st.sidebar.columns([0.62, 0.23, 0.15])
#displays chat and time, while using another color to show active chats that update as you switch between
    time_label = format_sidebar_timestamp(chat.get("timestamp"), is_active)
    indicator = "> " if is_active else ""
    chat_label = f"{indicator}{chat['title']}"
    if row_left.button(
        chat_label,
        key=f"select_{chat['id']}",
        use_container_width=True,
        type="primary" if is_active else "secondary",
    ):
        st.session_state.active_chat_id = chat["id"]
        st.rerun()
    row_middle.markdown(
        f'<div class="chat-time-label">{time_label}</div>',
        unsafe_allow_html=True,
    )
#if chat is deleted it is removed and previous chat is made active
    if row_right.button("✕", key=f"delete_{chat['id']}", use_container_width=True, type="secondary"):
        deleted_id = chat["id"]
        st.session_state.chats = [c for c in st.session_state.chats if c["id"] != deleted_id]
        delete_chat_file(deleted_id)
        if st.session_state.active_chat_id == deleted_id:
            if st.session_state.chats:
                st.session_state.active_chat_id = st.session_state.chats[0]["id"]
            else:
                st.session_state.active_chat_id = None
        st.rerun()

#for main active chat area to display messages, input, etc.
active_chat = get_active_chat()
#if no active chat, will say so until a new chat is made
if active_chat is None:
    st.info("No active chat. Click 'New Chat' in the sidebar to start one.")
    st.stop()
#formats and displays the messages showing all the appropriate information
chat_frame = st.container(height=620, border=True)
with chat_frame:
    for message in active_chat["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
user_prompt = st.chat_input("Type your message...")
if user_prompt:
    headers = {"Authorization": f"Bearer {hf_token}"}
    active_chat["messages"].append({"role": "user", "content": user_prompt})
#updates title from first user message for easy navigation
    if active_chat["title"] == "New Chat":
        active_chat["title"] = generate_chat_title_from_prompt(user_prompt, headers)

#update date-time so recent activity appears and is saved
    active_chat["timestamp"] = now_label()
    save_chat(active_chat)
    with chat_frame:
        with st.chat_message("user"):
            st.markdown(user_prompt)
#takes new info and dumps it for model to use for personalization and takes care of formatting
    request_messages = []
#checking for patterns that may have personal info and if so, is extracted for use
    memory_json = json.dumps(st.session_state.memory_data, ensure_ascii=True)
    display_name = get_display_name(st.session_state.memory_data)
    has_known_name = (
        isinstance(st.session_state.memory_data, dict)
        and isinstance(st.session_state.memory_data.get("name"), str)
        and st.session_state.memory_data.get("name").strip() != ""
    )
    request_messages.append(
        {
            "role": "system",
            "content": (
                "You are given trusted USER_MEMORY from this app session. "
                "Treat USER_MEMORY as true context provided by the user inside this app. "
                "Use it for personalization and recall questions. "
                "If the user asks what their name is and USER_MEMORY includes a name, answer with that name directly. "
                "Do not claim you have no information when USER_MEMORY already contains the requested fact. "
                "Only say a fact is unknown if it is missing from USER_MEMORY. "
                "Do not guess missing personal facts such as age or location. "
                "When referring to memory, use second-person phrasing (for example, 'your name is ...'). "
                "Never use first-person phrasing ('my name is ...'). "
                f"If no explicit name is known, address the user as '{display_name}'. "
                f"Known-name-available: {has_known_name}. "
                f"USER_MEMORY: {memory_json}"
            ),
        }
    )
    request_messages.extend(active_chat["messages"])

    deterministic_response = deterministic_memory_recall_response(
        user_prompt, st.session_state.memory_data
    )
    error_text = None
    assistant_text = ""

    if deterministic_response is not None:
        assistant_text = deterministic_response
        with chat_frame:
            with st.chat_message("assistant"):
                st.markdown(assistant_text)
    else:
        #sets up response formatting and streaming
        payload = {
            "model": MODEL_NAME,
            "messages": request_messages,
            "max_tokens": 512,
            "stream": True,
        }
        with chat_frame:
            with st.chat_message("assistant"):
                assistant_placeholder = st.empty()
                error_text = None
    #handles input and output of streaming responses whilre looking for any errors (displaying them if present)
                for streamed_text, streamed_error in stream_assistant_reply(headers, payload):
                    if streamed_error:
                        error_text = streamed_error
                        break
                    if streamed_text is not None:
                        assistant_text = streamed_text
                        assistant_placeholder.markdown(assistant_text)
    #here is specifically where errors are displayed
                if error_text:
                    assistant_placeholder.error(error_text)

    if not error_text:
        #once done streaming, the responses are saved in the appropriate format for recent activity
        active_chat["messages"].append({"role": "assistant", "content": assistant_text})
        active_chat["timestamp"] = now_label()
        save_chat(active_chat)

        #extracts any info that again, may be useful in identifying possible personal info or preferences
        model_memory_updates = extract_memory_updates(headers, user_prompt)
        fallback_memory_updates = {}
        if should_extract_memory(user_prompt):
            fallback_memory_updates = extract_memory_updates_fallback(user_prompt)
        memory_updates = combine_model_and_rule_updates(model_memory_updates, fallback_memory_updates)
        memory_updates = filter_memory_updates(user_prompt, memory_updates)
        memory_updates = enforce_strict_category_mapping(user_prompt, memory_updates)
        memory_updates = ground_memory_updates_to_user_text(user_prompt, memory_updates)

        #most recent info is merged with older info and saved
        if memory_updates:
            st.session_state.memory_data = merge_memory(st.session_state.memory_data, memory_updates)
            save_memory(st.session_state.memory_data)
            #rerun so the sidebar memory panel reflects updates immediately
            st.rerun()
