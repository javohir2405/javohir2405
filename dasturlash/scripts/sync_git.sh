#!/bin/bash
# content/ va scripts/ ni har 3 daqiqada tayinlangan shoxga saqlab boradi (konteyner tiklansa ham ish yo'qolmasin)
cd /home/user/javohir2405 || exit 1
while true; do
  git add dasturlash/content dasturlash/scripts dasturlash/.gitignore >/dev/null 2>&1
  if ! git diff --cached --quiet; then
    git commit -q -m "Dasturlash materiallari: oraliq saqlash" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" >/dev/null 2>&1
    for i in 1 2 3 4; do git push -q -u origin claude/determined-hopper-s9djd1 >/dev/null 2>&1 && break; sleep $((2**i)); done
  fi
  sleep 180
done
