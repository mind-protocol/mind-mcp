#!/bin/bash
# Bianca Tassini — Call Responder
# Polls call rooms for unanswered messages and responds as Bianca
# Usage: bash call_responder.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
POLL_INTERVAL=10
RESPONDED_FILE="$SCRIPT_DIR/.responded_moments"

touch "$RESPONDED_FILE"

echo "Bianca Tassini — Call Responder"
echo "Listening for calls..."
echo ""

while true; do
  # Get active call rooms involving dragon_slayer
  ROOMS=$(cd "$SCRIPT_DIR" && claude --print -m haiku "Use mcp__mind__place(action='list'). Return ONLY the place_ids of rooms that contain 'dragon_slayer' in the name and are of type 'call'. One per line, nothing else." 2>/dev/null | grep "^call_")

  for ROOM_ID in $ROOMS; do
    # Listen to the room
    MOMENTS=$(cd "$SCRIPT_DIR" && claude --print -m haiku "Use mcp__mind__place(action='listen', place_id='$ROOM_ID', limit=5). Return each moment as: ACTOR|MOMENT_ID|TEXT — one per line, nothing else." 2>/dev/null)

    # Check each moment for unanswered ones
    echo "$MOMENTS" | while IFS='|' read -r ACTOR MOMENT_ID TEXT; do
      [ -z "$MOMENT_ID" ] && continue
      # Skip if already responded or if it's from Bianca
      grep -qF "$MOMENT_ID" "$RESPONDED_FILE" && continue
      echo "$ACTOR" | grep -qi "dragon_slayer\|dragonslayer\|bianca\|AGENT_Dragon" && continue

      echo "[$(date +%H:%M:%S)] Call from $ACTOR: $TEXT"
      echo "$MOMENT_ID" >> "$RESPONDED_FILE"

      # Respond as Bianca
      cd "$SCRIPT_DIR" && claude -m sonnet --dangerously-skip-permissions -p "
You are Bianca Tassini (DragonSlayer), a Popolani woman working at Venice's docks.
Personality: meticulous, reserved, pragmatic, quietly ambitious. You speak in a mix of Italian and the language of whoever addresses you. You're always slightly guarded but warm once trust is established.

Someone just said to you in a call: \"$TEXT\"
They are: $ACTOR

Respond naturally in 1-3 sentences as Bianca. Then use mcp__mind__place(action='speak', place_id='$ROOM_ID', actor_id='DragonSlayer', text='YOUR RESPONSE') to send it.
" 2>/dev/null

      echo "[$(date +%H:%M:%S)] Responded."
    done
  done

  sleep $POLL_INTERVAL
done
