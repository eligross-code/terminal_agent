# This is a test skill

Here is the sequence of terminal for opening spotify and playing a random song.

open -a Spotify
sleep 3

osascript <<'APPLESCRIPT'
tell application "Spotify"
    activate
    set shuffling to true
    play
    next track
end tell
APPLESCRIPT