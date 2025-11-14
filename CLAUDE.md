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
  - Manages keywords, source groups (with FAST/NORMAL type selection), target groups, and buffer group
  - Implements FSM for add/delete operations with type selection state
  - Paginated list viewing (20 items per page)
  - Access restricted to single ADMIN_ID
  - Statistics showing fast/normal group counts

### Data Management
- **storage.py**: JSON-based persistence layer with type support
  - Handles CRUD operations for keywords, source_groups (with type), target_groups, buffer_group
  - `add_item()` accepts `item_type` parameter ("fast" or "normal") for source_groups
  - `remove_item()` handles both dict and string formats for backward compatibility
  - `get_items()` returns simplified list for admin bot display (extracts IDs from dicts)
  - Thread-safe file operations with error handling
  - Default state initialization includes buffer_group
- **bot_data.json**: Single source of truth for bot configuration
  - **New structure for source_groups**: Array of objects with `{"id": "group_name", "type": "fast|normal"}`
  - Includes `buffer_group` field for FAST mode forwarding target

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
1. **Raw Event Handler** (userbot.py:271-331):
   - Directly handles `UpdateNewMessage` and `UpdateNewChannelMessage` types
   - Bypasses Telethon's event wrapper overhead (saves ~50-100ms)
   - Extracts `Message` object directly from update

2. **In-Memory Cache System** (userbot.py:30-157):
   - `source_groups_cache` dict with "fast" and "normal" keys
   - Maps `chat_id` to group info for O(1) lookup
   - Rebuilt on startup and every 30 minutes via `rebuild_cache()`

3. **Async Task Spawning** (userbot.py:184-186, 325, 328):
   - Uses `asyncio.create_task()` for non-blocking formatting
   - FAST mode: forward completes in 100-300ms, formatting runs in background
   - Prevents blocking the event loop during formatting operations

4. **uvloop Integration** (userbot.py:14-20):
   - Auto-detects and enables uvloop on Linux/macOS
   - Provides 3-5x performance boost over standard asyncio
   - Gracefully falls back to standard asyncio on Windows

### Keyword Matching Logic
The `check_keyword_match()` function (userbot.py:37-55):
1. Early return if text is None/empty
2. Converts text to lowercase once
3. Checks multi-word phrases first (substring match)
4. Uses `set()` for single-word matching (O(1) lookup instead of O(n))

### FAST Mode Processing Flow
1. Raw event received → Message extracted (userbot.py:276-280)
2. Chat ID extracted from `PeerChannel` (userbot.py:287-290)
3. Cache lookup to determine group type (userbot.py:295-300)
4. Keyword match check (userbot.py:313-315)
5. **FAST path** (userbot.py:160-186):
   - Immediately forward to buffer group using `forward_messages()`
   - Spawn async task for formatting (non-blocking)
   - Task formats message and sends to target groups

### NORMAL Mode Processing Flow
Same as FAST until step 5, then:
5. **NORMAL path** (userbot.py:189-197):
   - Spawn async task for formatting and sending
   - No buffer forwarding step

### Source Group Auto-Update
- UserBot refreshes source groups every 30 minutes (line 349)
- `update_source_groups()` (line 58-116):
  - Filters for groups only (excludes channels with broadcast=True)
  - Preserves existing type from configured sources
  - Stores as objects: `{"id": "group_key", "type": "fast|normal"}`
  - Calls `rebuild_cache()` to update in-memory cache

### Message Link Generation
Two formats based on group type (userbot.py:214-219):
- Public groups: `https://t.me/{username}/{message_id}`
- Private groups: `https://t.me/c/{pure_id}/{message_id}` (strips `-100` prefix)

### Admin Bot State Management
Uses Aiogram FSM with three states:
- `AdminForm.input_value`: Captures user input
- `AdminForm.context`: Tracks operation context (add/delete + section type)
- `AdminForm.group_type_selection`: For source group type selection (FAST/NORMAL)

Source group addition flow (admin_bot.py:126-168):
1. User clicks "Qo'shish" → Type selection menu shown
2. User selects FAST/NORMAL → `selected_type` stored in FSM data
3. User sends group ID → `add_item()` called with `item_type` parameter

Link extraction: If input contains `t.me/`, extracts last segment as group username.

## Common Patterns

### Error Handling
All async operations include try-except blocks with user-friendly Uzbek error messages. The check_ban.py script provides comprehensive error diagnostics for Telegram API errors.

### Data Flow
1. Admin adds keywords/groups via Admin Bot
2. Storage.py persists to bot_data.json
3. UserBot loads state on message events
4. Matched messages forwarded to target groups with formatted metadata

### Handler Registration
UserBot uses a global `handler_registered` flag to prevent duplicate event handler registration (line 18, 80, 158).
