import random, pygame, os
import tkinter as tk
from PIL import Image, ImageTk

class Robby:
    def __init__(self):
        # Initialize Pygame mixer for sound playback
        pygame.mixer.init()

        # Load sounds
        self.screamSound = pygame.mixer.Sound("sounds/scream.mp3")
        self.walkingSound = pygame.mixer.Sound("sounds/walking.mp3")
        self.flyingSound = pygame.mixer.Sound("sounds/dragon-flying.mp3")
        self.transformSound = pygame.mixer.Sound("sounds/transform.mp3")
        self.rawrSound = pygame.mixer.Sound("sounds/rawr.mp3")

        # Initial position of Robby
        self.x, self.y = 100, 100  # Start near the top-left instead of (0,0)

        # State variables
        self.talking = False  # Whether Robby is talking
        self.dragon = False   # Whether Robby is in dragon form
        self.mood = "normal"  # Current mood (normal/angry)

        # Create a window
        self.window = tk.Tk()

        # Load images
        self.talkingimg = [Image.open('images/stare.png'), Image.open('images/talking.png')]
        self.talkingimg[0] = self.talkingimg[0].convert("RGBA").resize((128, 128))
        self.talkingimg[1] = self.talkingimg[1].convert("RGBA").resize((128, 128))
        self.dragonimg = Image.open("images/dragon.png").convert("RGBA").resize((128, 128))
        self.folderimg = Image.open("images/foldericon.png").convert("RGBA").resize((80, 80))

        # Initialize image for label
        self.img_tk = ImageTk.PhotoImage(self.talkingimg[0])

        # Make window frameless and always on top
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.wm_attributes('-transparentcolor', 'white')

        # Create label for displaying Robby's image
        self.label = tk.Label(self.window, bd=0, bg='black', image=self.img_tk)
        self.label.pack()

        # Set initial window position
        self.window.geometry(f"128x128+{self.x}+{self.y}")

        # Bind events for dragging, hiding, and showing Robby
        self.label.bind("<ButtonPress-1>", self.start_move)
        self.label.bind("<ButtonRelease-1>", self.stop_move)
        self.label.bind("<B1-Motion>", self.do_move)

        self.label.bind("<Double-Button-1>", self.hide)  # Double-click to hide
        self.window.bind("<KeyPress-s>", self.show)  # Click anywhere to show again

        # Start random events and movement
        self.update_random_event()
        self.move_randomly()

        # Run the Tkinter main loop
        self.window.mainloop()

    def start_move(self, event):
        """Record the initial click position inside the window."""
        self.drag_x = event.x
        self.drag_y = event.y

        # Play sound while dragging Robby
        if self.dragon:
            self.rawrSound.play(loops=-1)
        else:
            self.screamSound.play(loops=-1)

    def stop_move(self, event):
        """Stop playing sound when the mouse is released."""
        self.rawrSound.stop()
        self.screamSound.stop()

    def do_move(self, event):
        """Move Robby when dragged with the mouse."""
        x = self.window.winfo_x() + event.x - self.drag_x
        y = self.window.winfo_y() + event.y - self.drag_y
        self.window.geometry(f"+{x}+{y}")
        self.x, self.y = x, y  # Update position

    def update_random_event(self):
        """Randomly change Robby's state (talking, dragon form, mood) every 30 seconds."""
        if not getattr(self, 'hidden', False):  # Only trigger random events if not hidden
            action = random.randint(0, 2)  # 0 = idle, 1 = talking, 2 = dragon
            self.mood = "angry" if random.randint(0, 1) else "normal"  # Random mood
            self.update(action)  # Apply changes
            self.window.after(30000, self.update_random_event)  # Repeat every 30 sec

    def update(self, eventChance):
        """Update Robby's state based on random eventChance."""
        self.talking = eventChance == 1
        self.dragon = eventChance == 2

        if self.talking:
            self.window.wm_attributes('-transparentcolor', 'white')
            self.yap()
            self.animate_talking()
        elif self.dragon:
            self.transformSound.play()
            self.window.wm_attributes('-transparentcolor', 'black')
            self.img_tk = ImageTk.PhotoImage(self.dragonimg)  # Switch to dragon image
            self.label.config(image=self.img_tk)
        else:
            self.window.wm_attributes('-transparentcolor', 'white')
            self.img_tk = ImageTk.PhotoImage(self.talkingimg[0])  # Set to idle
            self.label.config(image=self.img_tk)

    def hide(self, event):
        """Change Robby into a folder icon without hiding the window."""
        if not getattr(self, 'hidden', False) and not self.talking:  # Only hide if not already hidden
            self.window.wm_attributes('-transparentcolor', 'black')
            self.img_tk = ImageTk.PhotoImage(self.folderimg)  # Folder icon image
            self.label.config(image=self.img_tk)
            self.window.geometry("80x80")
            self.hidden = True  # Mark as hidden
            self.stop_random_events()  # Stop random events and movement when hidden

    def show(self, event=None):
        """Change Robby back to his normal image when clicked."""
        if getattr(self, 'hidden', False):  # Only switch if hidden
            self.window.geometry("128x128")
            self.window.wm_attributes('-transparentcolor', 'white')
            self.img_tk = ImageTk.PhotoImage(self.talkingimg[0])  # stare image
            self.hidden = False  # Mark as visible
            self.restart_random_events()  # Restart random events and movement

    def stop_random_events(self):
        """Stop all random events like movement and state changes."""
        self.window.after_cancel(self.move_randomly)
        self.window.after_cancel(self.update_random_event)

    def restart_random_events(self):
        """Restart random events when Robby is shown."""
        self.update_random_event()
        self.move_randomly()

    def yap(self):
        """Play a random talking sound and stop talking when done."""
        files = os.listdir("yappinglines")  # Get all sound files
        filename = os.fsdecode(random.choice(files))  # Pick a random file
        sent = pygame.mixer.Sound(f"yappinglines/{filename}")  # Load sound

        sent.set_volume(2.0)  # Increase volume
        sent.play()  # Play sound

        # Stop talking animation when sound ends
        duration = int(sent.get_length() * 1000)  # Convert to milliseconds
        self.window.after(duration, self.stop_talking)

    def animate_talking(self):
        """Animate Robby's mouth opening and closing while talking."""
        if not self.talking:
            return  # Stop animation if no longer talking

        talkingSpeed = 150 if self.mood == "angry" else 500  # Adjust speed
        self.img_tk = ImageTk.PhotoImage(self.talkingimg[0 if getattr(self, 'toggle', False) else 1])
        self.label.config(image=self.img_tk)

        self.toggle = not getattr(self, 'toggle', False)  # Toggle between images

        if self.talking:
            self.window.after(talkingSpeed, self.animate_talking)

    def stop_talking(self):
        """Stop talking animation and reset to idle face."""
        self.talking = False
        self.img_tk = ImageTk.PhotoImage(self.talkingimg[0])  # Idle image
        self.label.config(image=self.img_tk)

    def move_randomly(self):
        """Move Robby to a random screen position at intervals."""
        if not getattr(self, 'hidden', False):  # Only move if not hidden
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()

            target_x = random.randint(0, screen_width - 128)
            target_y = random.randint(0, screen_height - 128)

            self.slide_to(target_x, target_y)

            next_move = random.randint(5000, 20000)  # Move every 5-20 seconds
            self.window.after(next_move, self.move_randomly)

    def slide_to(self, target_x, target_y, steps=50):
        """Move Robby smoothly to a target position."""
        dx = (target_x - self.x) / steps
        dy = (target_y - self.y) / steps

        def step(i=0):
            if i < steps:
                self.x += dx
                self.y += dy
                self.window.geometry(f"128x128+{int(self.x)}+{int(self.y)}")
                self.window.after(40, step, i + 1)  # Move every 40ms

        step()

# Run the application
robby = Robby()
