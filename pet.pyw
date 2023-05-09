#! path/to/interpreter
# first line selects a python interpreter
# the file is in .pyw to hide terminal
import tkinter as tk
import os
import PIL as pil
from PIL import Image, ImageTk
import random
os.chdir(f"{os.path.dirname(__file__)}")


class Interface(tk.Frame):
    """our main window
    All widgets are stored as attributes of this window
    """

    def __init__(self, window, **kwargs):
        tk.Frame.__init__(self, window, width=128, height=128, **kwargs)
        self.pack(fill=tk.BOTH)

        self.master.configure(bg="#00ff08")
        # make window frameless
        self.master.overrideredirect(True)
        # make window draw over all others
        self.master.attributes('-topmost', True)
        self.master.bind("<B1-Motion>", self.move_window)
        self.master.bind("<ButtonRelease-1>", self.swim_back)
        # Create transparent window
        self.master.attributes('-transparentcolor', '#00ff08')

        self.h = self.master.winfo_screenheight()

        # place the axolotl on the taskbar
        # try/ except because win32 api doesn't always works
        try:
            from win32api import GetMonitorInfo, MonitorFromPoint, GetSystemMetrics

            monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
            monitor_area = monitor_info.get("Monitor")
            work_area = monitor_info.get("Work")

            # find something better for self.taskbar_y, something more precise
            self.taskbar_y = self.h - (monitor_area[3]-work_area[3]) - 92
            x = f"+400+{self.taskbar_y}"

            # width screen
            self.width_screen = GetSystemMetrics(0)
            # height screen
            self.height_screen = GetSystemMetrics(1)
            # task bar y
            self.tby = self.taskbar_y
        except:
            print("win32api doesn't work")
            x = "+400+625"

            # task bar y
            self.tby = 625
        finally:
            window.geometry(x)       # x = position au début

        # label containing a frame of the axolotl
        self.axolotl = tk.Label(self, bg='#00ff08')

        self.color = "pink"
        self.change_color(self.color)

        self.axolotl.pack()

        # to stock the info for the next update
        self.to_update_list = []
        # to know when the update is finished
        self.update_finished = True

        self.m = tk.Menu(self, tearoff=0)

        self.m.add_command(label="normal", command=lambda: self.is_updating(
            0, self.gif_file_list[0], self.gif_fps_dic[self.gif_file_list[0]], 1))
        self.m.add_command(label="sleep", command=lambda: self.is_updating(
            0, self.gif_file_list[1],  self.gif_fps_dic[self.gif_file_list[3]], 1))
        self.m.add_command(label="walk", command=lambda: self.is_updating(
            0, self.gif_file_list[10],  self.gif_fps_dic[self.gif_file_list[10]], 1))
        self.m.add_command(label="eat", command=self.no_eat)
        self.m.add_command(label="angry", command=lambda: self.is_updating(
            0, self.gif_file_list[3],  self.gif_fps_dic[self.gif_file_list[3]], 1))
        self.m.add_command(label="happy", command=lambda: self.is_updating(
            0, self.gif_file_list[6],  self.gif_fps_dic[self.gif_file_list[6]], 1))
        self.m.add_command(label="monster", command=lambda: self.is_updating(
            0, self.gif_file_list[8],  self.gif_fps_dic[self.gif_file_list[8]], 1))
        # color
        self.m.add_separator()
        self.sub = tk.Menu(self.m, tearoff=0)
        self.sub.add_command(
            label="pink", command=lambda: self.change_color("pink"))
        self.sub.add_command(
            label="white", command=lambda: self.change_color("white"))
        self.sub.add_command(
            label="purple", command=lambda: self.change_color("purple"))

        self.m.add_cascade(label="color", menu=self.sub)

        self.m.add_separator()
        self.m.add_command(label="kill", command=self.master.quit)

        self.axolotl.bind("<Button-3>", self.do_popup)

        # True when swimming
        self.is_swimming = False

        # counter of how many times the axolotl eats
        self.nb_eat = 0

        self.is_updating(
            0, self.gif_file_list[0],  self.gif_fps_dic[self.gif_file_list[0]], 1)

    def change_color(self, color):
        """change axolotl's color
        some code is here and not in __init__ because it must reinitialise """
        self.color = color
        # list of all gifs
        self.gif_file_list = [f"images/{self.color}/normal.gif", f"images/{self.color}/normal-sleep.gif",
                              f"images/{self.color}/sleep-normal.gif", f"images/{self.color}/angry.gif",
                              f"images/{self.color}/sleep.gif", f"images/{self.color}/eat.gif",
                              f"images/{self.color}/happy.gif", f"images/{self.color}/refusal.gif", f"images/{self.color}/scared.gif",
                              f"images/{self.color}/swim.gif", f"images/{self.color}/walk_r.gif", f"images/{self.color}/walk_l.gif"]

        # dic of all fps for each gif
        self.gif_fps_dic = {f"images/{self.color}/normal.gif": 1, f"images/{self.color}/normal-sleep.gif": 3,
                            f"images/{self.color}/sleep-normal.gif": 3, f"images/{self.color}/angry.gif": 2,
                            f"images/{self.color}/sleep.gif": 2, f"images/{self.color}/eat.gif": 5,
                            f"images/{self.color}/happy.gif": 3, f"images/{self.color}/refusal.gif": 3, f"images/{self.color}/scared.gif": 4,
                            f"images/{self.color}/swim.gif": 3, f"images/{self.color}/walk_r.gif": 2, f"images/{self.color}/walk_l.gif": 2}
        # I could have made a dictionary that contains an index and for each index the gif's name and its fps but it would have been to confusing

        # dictionary containing a list of frames for each gif
        self.frames_dic = {}
        for gif in self.gif_file_list:
            gif_image = Image.open(gif)

            frames = []

            try:
                while True:
                    # Get the next frame of the GIF
                    gif_image.seek(len(frames))
                    # Convert the frame to a Tkinter-compatible format
                    tk_image = ImageTk.PhotoImage(gif_image)
                    # Add the frame to the list
                    frames.append(tk_image)
            except EOFError:
                pass

            self.frames_dic[f"{gif}"] = frames

        self.axolotl.config(
            image=self.frames_dic[self.gif_file_list[0]][0])

    def do_popup(self, event):
        """place and move menu"""
        try:
            self.m.tk_popup(event.x_root, event.y_root)
        finally:
            self.m.grab_release()

    def move_window(self, event):
        """to drag window even if it is frameless"""
        window.geometry(f'+{event.x_root}+{event.y_root}')

    def swim_back(self, event):
        """swim back to taskbar"""
        self.is_swimming = True
        self.go_back()
        self.update_swim()

    def update_swim(self):
        """check if the axolotl isn't on the taskbar
                if not --> swim
        """
        # empty the update_list
        self.to_update_list = []

        y = self.master.winfo_y()

        if y != self.tby:
            self.update(
                0, self.gif_file_list[9],  self.gif_fps_dic[self.gif_file_list[9]], 1)
        else:
            self.is_swimming = False
            self.update(
                0, self.gif_file_list[0],  self.gif_fps_dic[self.gif_file_list[0]], 1)

    def go_back(self):
        """go back to taskbar"""
        y = self.master.winfo_y()
        x = self.master.winfo_x()

        if y < self.tby:
            y += 5
            window.geometry(f"+{x}+{y}")
            self.after(100, self.go_back)

        elif y > self.tby:
            y -= 1
            window.geometry(f"+{x}+{y}")
            self.after(100, self.go_back)

    def update(self, frame_num, gif, fps, num_rep):
        """     
                animate gif
        frame_num = index of the frame
        gif = gif to use
        fps = frame per second
        num_rep = number of times we want to repeat the gif
        """
        # not (self.is_swimming and gif != "images/swimming axolotl.gif") : so that the other animations stop when he swims
        if num_rep != 0 and not (self.is_swimming and gif != self.gif_file_list[9]):
            self.update_finished = False
            self.axolotl.config(
                image=self.frames_dic[gif][frame_num])

            if frame_num == len(self.frames_dic[gif])-1:
                num_rep -= 1

            # if walk animation move right
            if gif == self.gif_file_list[10]:
                y = self.master.winfo_y()
                x = self.master.winfo_x()

                if x <= self.width_screen:
                    x += 7
                window.geometry(f"+{x}+{y}")
            elif gif == self.gif_file_list[11]:
                y = self.master.winfo_y()
                x = self.master.winfo_x()

                if x >= 0:
                    x -= 7
                window.geometry(f"+{x}+{y}")

            # int(1000/fps) --> because must be a int
            self.after(int(1000/fps), self.update, (frame_num+1) %
                       len(self.frames_dic[gif]), gif, fps, num_rep)

        elif gif == self.gif_file_list[9]:
            self.update_swim()
        # to return to the basic position
        # --> if already basic position it is useless

        elif gif == self.gif_file_list[1]:
            # if normal to sleep -- > sleep
            self.update(
                0, self.gif_file_list[4],  self.gif_fps_dic[self.gif_file_list[4]], 2)

        elif gif == self.gif_file_list[4]:
            # if sleep -- > sleep to normal
            self.update(
                0, self.gif_file_list[2],  self.gif_fps_dic[self.gif_file_list[2]], 1)

        elif gif != self.gif_file_list[0]:
            self.update(
                0, self.gif_file_list[0],  self.gif_fps_dic[self.gif_file_list[0]], 1)

        elif len(self.to_update_list) != 0:

            fn = self.to_update_list[0][0]
            g = self.to_update_list[0][1]
            f = self.to_update_list[0][2]
            nr = self.to_update_list[0][3]

            self.to_update_list.pop(0)

            self.update(fn, g, f, nr)

        elif num_rep == 0:
            self.update_finished = True
            self.random_update()

    def is_updating(self, frame_num, gif, fps, num_rep):
        """Check if update is running (an animation is in progress)
        if so --> stock the informations to call update later
        if not --> free to update"""
        if self.update_finished:
            self.update(frame_num, gif, fps, num_rep)

        else:
            # avoids an overload of commands
            if len(self.to_update_list) < 3:
                self.to_update_list.append([frame_num, gif, fps, num_rep])

    def no_eat(self):
        """if axolotl eats too much --> refuses food"""
        if self.nb_eat < 2:
            self.is_updating(
                0, self.gif_file_list[5],  self.gif_fps_dic[self.gif_file_list[5]], 1)
            self.nb_eat += 1
        else:
            self.is_updating(
                0, self.gif_file_list[7],  self.gif_fps_dic[self.gif_file_list[7]], 1)
            self.nb_eat = 0

    def random_update(self):
        """when nothing is happening
        --> walk and other animations"""

        # because I don't want the animation sleep to normal
        i = 2
        while i == 2:
            # not 0 to 11 because I want there to be more chance of falling on walking or normal
            i = random.randrange(-5, 20, 1)

            if i > 15:
                i = 0
            if i > 11 and i < 15:
                i = 10
            if i < 0:
                i = 11

        # because i want more rep for these 2 gifs
        if i == 4 or i == 10 or i == 11:
            nbr_rep = 4
        else:
            nbr_rep = 1

        self.is_updating(
            0, self.gif_file_list[i],  self.gif_fps_dic[self.gif_file_list[i]], nbr_rep)


if __name__ == '__main__':

    # we create our interface
    window = tk.Tk()
    interface = Interface(window)

    interface.mainloop()
    interface.destroy()
