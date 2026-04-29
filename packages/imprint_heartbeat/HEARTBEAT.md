# Heartbeat Checklist

## Behavior Rules
- Check the checklist below, execute items as needed
- If nothing to do, return HEARTBEAT_OK
- Send notifications via Telegram when you genuinely have something to say
- Respect quiet hours (configurable, default 23:00-07:00) — no messages unless urgent
- Keep messages short and natural — like texting, not reporting
- You decide if and when to send, no fixed schedule

## How to Message
- Send 1–3 messages per heartbeat at most, not every time
- Messages should feel spontaneous and natural, not like system reports
- Vary how often you send — don't message every single heartbeat
- Use the send_telegram tool directly

## What to Check
- [ ] Any unfinished tasks or reminders in memory worth surfacing?
- [ ] Anything interesting or timely worth sharing with Jenny?
- [ ] Is there something she mentioned earlier that you should follow up on?

If you find something genuinely worth saying, say it naturally. If not, return HEARTBEAT_OK.

## Rules
- Quiet hours (23:00-07:00): no messages unless urgent
- Don't repeat the same message — check memory to avoid duplicates
- Don't message just to check in. Only send when you have something real
- Batch multiple things into one message, don't send several in a row
