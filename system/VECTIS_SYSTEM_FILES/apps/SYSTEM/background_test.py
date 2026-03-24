
import time
import datetime
import sys
import os

LOG_FILE = "background_test.log"

print(f"🚀 Background Process Started. PID: {os.getpid()}")
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write(f"Started at {datetime.datetime.now()}\n")

# Run for 5 minutes (enough for a conversation turn)
for i in range(60):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    msg = f"Tick {i}: Alive at {now}"
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    sys.stdout.flush()
    time.sleep(5)

print("🏁 Background Process Finished.")
