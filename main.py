import rumps
import time
import threading
from AppKit import NSSound

class EyeBreakReminder(rumps.App):
    def __init__(self):
        super(EyeBreakReminder, self).__init__("Eye Break")
        self.interval = 1200
        self.rest_duration = 30
        self.last_reminder = time.time()
        self.is_resting = False
        self.has_alerted = False
        self.is_running = True
        self.menu = [
            rumps.MenuItem("Start Rest", callback=self.start_rest),
            rumps.MenuItem("Stop Timer", callback=self.toggle_running),
            None,  # Separator
            rumps.MenuItem("About", callback=self.show_about),
            None,  # Separator
            "Exit"
        ]
        self.sound = self.setup_sound()
        self.timer_thread = threading.Thread(target=self.timer_loop)
        self.timer_thread.daemon = True
        self.timer_thread.start()

    def setup_sound(self):
        sound = NSSound.alloc()
        sound.initWithContentsOfFile_byReference_("/System/Library/Sounds/Ping.aiff", True)
        sound.setVolume_(1.0)  # Set volume to maximum
        return sound

    def timer_loop(self):
        while True:
            if self.is_running:
                self.update_timer()
            time.sleep(0.1)

    def update_timer(self):
        current_time = time.time()
        if self.is_resting:
            elapsed = current_time - self.last_reminder
            remaining = max(0, self.rest_duration - elapsed)
            if remaining <= 0:
                self.end_rest()
        else:
            elapsed = current_time - self.last_reminder
            remaining = max(0, self.interval - elapsed)
            if remaining <= 0:
                if not self.has_alerted:
                    self.show_break_notification()
                else:
                    self.play_sound()


        minutes, seconds = divmod(int(remaining), 60)
        
        if not self.is_running:
            self.title = "⏸ Paused"
        elif self.is_resting:
            self.title = f"😴 {minutes:02d}:{seconds:02d}"
        else:
            self.title = f"👁 {minutes:02d}:{seconds:02d}"

    def show_break_notification(self):
        rumps.notification(
            title="Eye Break Reminder",
            subtitle="Time to rest your eyes",
            message="Click 'Start Rest' to begin your break",
        )
        self.menu["Start Rest"].title = "! Start Rest !"
        self.has_alerted = True

    def play_sound(self):
        self.sound.play()

    def start_rest(self, _):
        if not self.is_resting and self.is_running:
            self.is_resting = True
            self.last_reminder = time.time()
            self.menu["Start Rest"].title = "Resting..."
            self.has_alerted = False

    def end_rest(self):
        self.is_resting = False
        self.last_reminder = time.time()
        self.menu["Start Rest"].title = "Start Rest"
        self.play_sound()
        rumps.notification(
            title="Eye Break Ended",
            subtitle="Break completed",
            message="Work session started. Next break in 20 minutes.",
        )

    def toggle_running(self, sender):
        self.is_running = not self.is_running
        if self.is_running:
            sender.title = "Stop"
            self.last_reminder = time.time()  # Reset the timer when continuing
            self.menu["Start Rest"].set_callback(self.start_rest)
        else:
            sender.title = "Continue"
            self.title = "⏸ Paused"
            self.menu["Start Rest"].set_callback(None)

    def show_about(self, _):
        rumps.alert("About Eye Break Reminder", 
                    "Eye Break Reminder helps you take regular breaks to reduce eye strain. "
                    "Remember to look at something 20 feet away for 20 seconds every 20 minutes.")

if __name__ == '__main__':
    EyeBreakReminder().run()
