# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a high-performance Telegram keyword monitoring bot that forwards messages containing specific keywords from source groups to target groups. The system supports two operational modes:

1. **FAST mode** - For groups with admin bots that immediately delete messages (uses raw events + buffer forwarding)
2. **NORMAL mode** - For regular groups (standard event handling)

The system consists of two concurrent components:

1. **UserBot** (Telethon): Monitors source groups using raw events for maximum speed, forwards to buffer group, and sends formatted messages to target groups
2. **Admin Bot** (Aiogram): Provides admin interface for managing keywords, source groups (with type selection), target groups, and buffer group

Both bots run simultaneously via `main.py`.

## Architecture

### Dual Bot System
- **main.py**: Entry point that launches both bots concurrently using `asyncio.gather()`
- **userbot.py**: Telethon-based user client with performance optimizations:
  - **Raw Events Handler**: Uses `events.Raw([UpdateNewMessage, UpdateNewChannelMessage])` for maximum speed
  - **Cache System**: Stores source groups in memory (`source_groups_cache`) split by type (fast/normal)
  - **uvloop Support**: Automatically enables uvloop if available for 3-5x speed boost
  - **Dual Processing Modes**:
    - FAST: Immediately forwards to buffer group, then formats asynchronously with `asyncio.create_task()`
    - NORMAL: Standard formatting and sending
  - Auto-updates source groups every 30 minutes with cache rebuild
  - Uses separate API credentials (hardcoded in file lines 23-24, different from config.py)
- **admin_bot.py**: Aiogram-based bot that:
  - Provides admin panel with keyboard interface
  - Manages keywords, blackwords, source groups (with FAST/NORMAL type selection), target groups, and buffer group
  - Implements FSM for add/delete operations with type selection state
  - Paginated list viewing (20 items per page)
  - Access restricted to single ADMIN_ID
  - Statistics showing fast/normal group counts

### Data Management
- **storage.py**: JSON-based persistence layer with type support
  - Handles CRUD operations for keywords, source_groups (with type), target_groups, buffer_group, blackwords
  - `add_item()` accepts `item_type` parameter ("fast" or "normal") for source_groups
  - `remove_item()` handles both dict and string formats for backward compatibility
  - `get_items()` returns simplified list for admin bot display (extracts IDs from dicts)
  - Thread-safe file operations with error handling
  - Default state initialization includes buffer_group and blackwords
- **bot_state.json**: Single source of truth for bot configuration (storage.py:4)
  - **Structure for source_groups**: Array of objects with `{"id": "group_name", "type": "fast|normal"}`
  - Includes `buffer_group` field for FAST mode forwarding target
  - Includes `blackwords` array for filtering unwanted messages
  - **Note**: `bot_data.json` also exists but is not actively used by the application

### Utility Scripts
- **check_ban.py**: Diagnostic tool for Telegram flood bans
  - Detects FloodWaitError, PhoneNumberBannedError, ApiIdInvalidError
  - Provides detailed error explanations in Uzbek
  - Two modes: full check (sends code) and quick check (session only)
- **test_connection.py**: API validation tool
  - Tests Telegram API connectivity
  - Handles initial authorization flow
  - Cleans up test session files

## Development Commands

### Running the Bot
```bash
python main.py
```
Starts both UserBot and Admin Bot concurrently.

### Testing API Connection
```bash
python test_connection.py
```
Validates API credentials and phone number authorization.

### Checking Flood Ban Status
```bash
python check_ban.py
```
Diagnoses Telegram flood wait or ban issues.

### Installing Dependencies
```bash
pip install -r requirements.txt
```
Installs Telethon 1.34.0 and Aiogram 3.3.0.

## Configuration

### Critical Files
- **config.py**: Contains API credentials for admin bot (api_id, api_hash, BOT_TOKEN, ADMIN_ID)
- **userbot.py lines 13-15**: Separate hardcoded credentials for userbot client
- **admin_bot.py lines 11-12**: Hardcoded BOT_TOKEN and ADMIN_ID (duplicates config.py)

**Note**: There are duplicate API credentials across multiple files. The userbot uses different credentials than config.py (lines 13-15 in userbot.py vs config.py).

### Session Management
- UserBot creates `userbot_session.session` for Telethon client persistence
- Test scripts create temporary sessions that are auto-cleaned after execution

## Key Implementation Details

### Performance Optimizations
1. **Raw Event Handler** (userbot.py:471-566):
   - Directly handles `UpdateNewMessage` and `UpdateNewChannelMessage` types
   - Bypasses Telethon's event wrapper overhead (saves ~50-100ms)
   - Extracts `Message` object directly from update (userbot.py:476-480)

2. **In-Memory Cache System** (userbot.py:31-34, 199-248):
   - `source_groups_cache` dict with "fast" and "normal" keys
   - Maps `chat_id` to group info for O(1) lookup (userbot.py:494-501)
   - Rebuilt on startup and every 30 minutes via `rebuild_cache()`
   - FAST groups pre-cache users for faster username retrieval (userbot.py:232-241)

3. **Async Task Spawning** (userbot.py:300-301, 557, 560):
   - Uses `asyncio.create_task()` for non-blocking formatting
   - FAST mode: buffer send completes in 100-300ms, target formatting runs in background
   - Prevents blocking the event loop during formatting operations

4. **uvloop Integration** (userbot.py:14-20):
   - Auto-detects and enables uvloop on Linux/macOS
   - Provides 3-5x performance boost over standard asyncio
   - Gracefully falls back to standard asyncio on Windows

5. **Fast User Identifier Extraction** (userbot.py:527-552):
   - Extracts phone numbers directly from message entities (most reliable)
   - Falls back to post_author for channel posts
   - Uses Telethon's internal entity cache for username lookup (no API call)
   - Avoids slow `get_sender()` calls that would delay processing

### Keyword Matching Logic
The `check_keyword_match()` function (userbot.py:37-55):
1. Early return if text is None/empty
2. Converts text to lowercase once
3. Checks multi-word phrases first (substring match)
4. Uses `set()` for single-word matching (O(1) lookup instead of O(n))

### Blackwords Filtering
The `check_blackword()` function (userbot.py:58-77):
- Messages containing blackwords are skipped even if they match keywords
- Used to filter spam, ads, and unwanted content (e.g., "қўшилишингиз керак")
- Supports both single-word and multi-word blacklist phrases
- Checked after keyword match but before forwarding (userbot.py:514-520)
- Managed via admin bot interface alongside keywords

### FAST Mode Processing Flow
1. Raw event received → Message extracted (userbot.py:471-480)
2. Chat ID extracted from `PeerChannel` (userbot.py:486-491)
3. Cache lookup to determine group type (userbot.py:494-501)
4. Keyword match check (userbot.py:510-512)
5. Blackword filter check (userbot.py:514-520)
6. **FAST path** (userbot.py:555-557):
   - Extract user identifier (phone/username) from message (userbot.py:527-552)
   - Immediately send to buffer group with basic formatting
   - Spawn async task (`handle_fast_message`) for formatted delivery to target groups
   - Buffer send completes in 100-300ms, target formatting runs in background

### NORMAL Mode Processing Flow
Same as FAST until step 6, then:
6. **NORMAL path** (userbot.py:558-560):
   - Spawn async task (`handle_normal_message`) for full user lookup and formatting
   - No buffer forwarding step

### Source Group Auto-Update
- UserBot refreshes source groups every 30 minutes (userbot.py:579-583)
- `update_source_groups()` (userbot.py:138-196):
  - Filters for groups only (excludes channels with broadcast=True)
  - Preserves existing type from configured sources
  - Stores as objects: `{"id": "group_key", "type": "fast|normal"}`
  - Calls `rebuild_cache()` to update in-memory cache
- `rebuild_cache()` (userbot.py:199-248):
  - Clears and rebuilds in-memory cache split by group type
  - For FAST groups: pre-loads last 100 messages to cache users (lines 232-241)

### Message Link Generation
Two formats based on group type (userbot.py:326-331):
- Public groups: `https://t.me/{username}/{message_id}`
- Private groups: `https://t.me/c/{pure_id}/{message_id}` (strips `-100` prefix)

### Admin Bot State Management
Uses Aiogram FSM with three states:
- `AdminForm.input_value`: Captures user input (admin_bot.py:18)
- `AdminForm.context`: Tracks operation context (add/delete + section type) (admin_bot.py:19)
- `AdminForm.group_type_selection`: For source group type selection (FAST/NORMAL) (admin_bot.py:20)

Source group addition flow:
1. User clicks "Qo'shish" → Type selection menu shown (admin_bot.py:194-211)
2. User selects FAST/NORMAL → `selected_type` stored in FSM data (admin_bot.py:219-231)
3. User sends group ID → `add_item()` called with `item_type` parameter

Statistics display includes blackwords count and FAST/NORMAL breakdown (admin_bot.py:133-154)

Link extraction: If input contains `t.me/`, extracts last segment as group username.

## Common Patterns

### Error Handling
All async operations include try-except blocks with user-friendly Uzbek error messages. The check_ban.py script provides comprehensive error diagnostics for Telegram API errors.

### Data Flow
1. Admin adds keywords/blackwords/groups via Admin Bot
2. Storage.py persists to bot_state.json
3. UserBot loads state on message events
4. Messages checked against keywords and blackwords
5. Matched messages (without blackwords) forwarded to target groups with formatted metadata

### Handler Registration
UserBot uses a global `handler_registered` flag to prevent duplicate event handler registration (userbot.py:28, checked at line 465, set at line 565).
