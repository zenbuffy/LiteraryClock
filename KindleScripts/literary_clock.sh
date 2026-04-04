#!/bin/sh
# Name: Literary Clock
# DontUseFBInk: true

PID_FILE=/tmp/literary_clock.pid
LOG=/tmp/literary_clock.log
CSV=/mnt/us/timelit/litclock_annotated_improved.csv
FONT=/mnt/us/timelit/LinLibertine_RZ.ttf
IMAGES=/mnt/us/timelit/images

log() { echo "$(date '+%H:%M:%S') $*" >> "$LOG"; }

run_clock() {
    log "run_clock started"

    # Detect display mode once at startup
    if command -v fbink > /dev/null 2>&1; then
        DISPLAY_MODE=fbink
        log "display mode: fbink"
    else
        DISPLAY_MODE=eips
        log "display mode: eips (fbink not found)"
    fi

    if [ "$DISPLAY_MODE" = fbink ]; then
        if [ ! -f "$CSV" ]; then
            log "ERROR: CSV not found: $CSV"
            return 1
        fi
        if [ ! -f "$FONT" ]; then
            log "ERROR: font not found: $FONT"
            return 1
        fi
    else
        if [ ! -d "$IMAGES" ]; then
            log "ERROR: images dir not found: $IMAGES"
            return 1
        fi
    fi

    while true; do
        TIME=$(date +"%H:%M")
        TIME_KEY=$(date +"%H%M")
        log "tick $TIME"

        if [ "$DISPLAY_MODE" = fbink ]; then
            # --- FBInk path ---
            LINE=$(awk -F'|' -v t="$TIME" '
                BEGIN { srand() }
                $1 == t { a[++n] = $0 }
                END { if (n > 0) print a[int(rand() * n) + 1] }
            ' "$CSV")

            if [ -z "$LINE" ]; then
                log "no quote for $TIME, sleeping"
                sleep "$((60 - $(date +%S)))"
                continue
            fi

            QUOTE=$(printf '%s' "$LINE"  | awk -F'|' '{print $3}')
            SOURCE=$(printf '%s' "$LINE" | awk -F'|' '{print $4}')
            AUTHOR=$(printf '%s' "$LINE" | awk -F'|' '{print $5}')
            log "quote: $QUOTE"

            fbink -c -f
            fbink -m -M -t "regular=$FONT,size=36px,padding=HORIZONTAL" -- "$QUOTE" \
                >> "$LOG" 2>&1
            fbink -y -3 -M -t "regular=$FONT,size=24px" -- "— $SOURCE, $AUTHOR" \
                >> "$LOG" 2>&1

        else
            # --- eips fallback path ---
            MATCHES=$(ls "${IMAGES}/metadata/quote_${TIME_KEY}_"*_credits.png 2>/dev/null)

            if [ -z "$MATCHES" ]; then
                log "no images for $TIME_KEY, sleeping"
                sleep "$((60 - $(date +%S)))"
                continue
            fi

            IMAGE=$(printf '%s\n' $MATCHES | awk '
                BEGIN { srand() }
                { a[++n] = $0 }
                END { print a[int(rand() * n) + 1] }
            ')
            log "image: $IMAGE"

            eips -c >> "$LOG" 2>&1
            eips -g "$IMAGE" >> "$LOG" 2>&1
        fi

        sleep "$((60 - $(date +%S)))"
    done
}

# Toggle: if already running, kill and exit
if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    kill "$(cat "$PID_FILE")"
    rm -f "$PID_FILE"
    exit 0
fi

# Start clock loop in background
run_clock &
echo $! > "$PID_FILE"
