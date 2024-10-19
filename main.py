import rumps
import time
from AppKit import NSSound

class EyeBreakReminder(rumps.App):
    def __init__(self):
        super(EyeBreakReminder, self).__init__("👁")
        self.interval = 1200  
        self.rest_duration = 30  
        self.last_reminder = time.time()
        self.show_time = True
        self.is_resting = False
        self.has_alerted = False
        self.menu = ["Start Rest", "Toggle Time Display", None, "Exit"]
        self.sound = self.setup_sound()
        self.timer = rumps.Timer(self.update_timer, 1)
        self.timer.start()

    def setup_sound(self):
        sound = NSSound.alloc()
        sound.initWithContentsOfFile_byReference_("/System/Library/Sounds/Sosumi.aiff", True)
        sound.setVolume_(1.0)  
        return sound

    def update_timer(self, _):
        current_time = time.time()
        if self.is_resting:
            elapsed = current_time - self.last_reminder
            remaining = max(0, self.rest_duration - elapsed)
        else:
            elapsed = current_time - self.last_reminder
            remaining = max(0, self.interval - elapsed)

        minutes, seconds = divmod(int(remaining), 60)
        
        if self.is_resting:
            self.title = f"😴 {minutes:02d}:{seconds:02d}"
        elif self.show_time:
            self.title = f"👁 {minutes:02d}:{seconds:02d}"
        else:
            self.title = "👁"

        if not self.is_resting and remaining <= 0:
            if not self.has_alerted:
                self.show_break_notification()
                self.has_alerted = True
            else:
                self.play_intrusive_sound()
        elif self.is_resting and remaining <= 0:
            self.end_rest()

    def show_break_notification(self):
        rumps.notification(
            title="Eye Break Reminder",
            subtitle="Time to rest your eyes",
            message="Click 'Start Rest' to begin your break",
            sound=True
        )
        self.make_start_rest_button_red()

    def make_start_rest_button_red(self):
        self.menu["Start Rest"].title = "⚠️ Start Rest ⚠️"

    @rumps.clicked("Start Rest")
    def start_rest(self, _):
        if not self.is_resting:
            self.is_resting = True
            self.last_reminder = time.time()
            self.menu["Start Rest"].title = "Resting..."
            self.has_alerted = False

    def end_rest(self):
        self.is_resting = False
        self.last_reminder = time.time()
        self.menu["Start Rest"].title = "Start Rest"
        rumps.notification(
            title="Eye Break Ended",
            subtitle="Break completed",
            message="Work session started. Next break in 20 minutes.",
            sound=True
        )

    @rumps.clicked("Toggle Time Display")
    def toggle_time_display(self, _):
        self.show_time = not self.show_time

    def play_intrusive_sound(self):
        self.sound.play()

if __name__ == '__main__':
    EyeBreakReminder().run()
