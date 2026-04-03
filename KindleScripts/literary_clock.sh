#!/bin/sh
# Name: Literary Clock
# DontUseFBInk: true

PID_FILE=/tmp/literary_clock.pid
CSV=/mnt/us/timelit/litclock.csv
FONT=/mnt/us/timelit/LinLibertine_RZ.ttf
IMAGES=/mnt/us/timelit/images

run_clock() {
    # Detect display mode once at startup
    if command -v fbink > /dev/null 2>&1; then
        DISPLAY_MODE=fbink
    else
        DISPLAY_MODE=eips
    fi

    while true; do
        TIME=$(date +"%H:%M")
        TIME_KEY=$(date +"%H%M")

        if [ "$DISPLAY_MODE" = fbink ]; then
            # --- FBInk path ---
            LINE=$(awk -F'|' -v t="$TIME" '
                BEGIN { srand() }
                $1 == t { a[++n] = $0 }
                END { if (n > 0) print a[int(rand() * n) + 1] }
            ' "$CSV")

            if [ -z "$LINE" ]; then
                sleep "$((60 - $(date +%S)))"
                continue
            fi

            QUOTE=$(printf '%s' "$LINE"  | awk -F'|' '{print $3}')
            SOURCE=$(printf '%s' "$LINE" | awk -F'|' '{print $4}')
            AUTHOR=$(printf '%s' "$LINE" | awk -F'|' '{print $5}')

            fbink -c -f
            fbink -m -M -t "regular=$FONT,size=36px,padding=HORIZONTAL" -- "$QUOTE"
            fbink -y -3 -M -t "regular=$FONT,size=24px" -- "— $SOURCE, $AUTHOR"

        else
            # --- eips fallback path ---
            MATCHES=$(ls "${IMAGES}/quote_${TIME_KEY}_"*.png 2>/dev/null)

            if [ -z "$MATCHES" ]; then
                sleep "$((60 - $(date +%S)))"
                continue
            fi

            IMAGE=$(printf '%s\n' $MATCHES | awk '
                BEGIN { srand() }
                { a[++n] = $0 }
                END { print a[int(rand() * n) + 1] }
            ')

            eips -c
            eips -g "$IMAGE"
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
