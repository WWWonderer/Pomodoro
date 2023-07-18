import customtkinter
from datetime import datetime, timedelta
import io
from math import floor
import matplotlib.pyplot as plt
import numpy as np
import os
from PIL import Image, ImageEnhance
import time
import winsound

# configure GUI style
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue")
customtkinter.set_widget_scaling(1.2)
# configure plot style
plt.style.use('dark_background')
# configure timer
STUDY_SESSION_MINS = 1500
BREAK_SESSION_MINS = 300

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.time_remaining = STUDY_SESSION_MINS
        self.last_click_time = datetime.now()
        self.last_update_time = self.last_click_time + timedelta(seconds=1)
        self.mode = "study" # "study" or "break"
        self.plot_mode = "weekly" # "weekly" or "monthly"
        self.current_pomodoro_session = 0
        self.pause = True # False or True
        self.data_folder = os.path.join(os.getenv("APPDATA"), "Pomodoro")

        # configure window
        self.iconbitmap(False, self._resource_path("resources\\tomato.ico"))
        self.title(" Pomodoro Timer")
        self.geometry(f"{1100}x{580}")

        # configure general grid 
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self)
        self.sidebar_frame.grid(column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure((0, 1, 2, 5, 6, 7, 8), weight=0)
        self.sidebar_frame.grid_rowconfigure((3, 4), weight=1)
        self.sidebar_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.reset_button = customtkinter.CTkButton(self.sidebar_frame, text="reset", command=self.reset)
        self.reset_button.grid(row=0, column=0, columnspan=4, padx=10, pady=(20, 5))
        self.done_button = customtkinter.CTkButton(self.sidebar_frame, text="done", command=self.done)
        self.done_button.grid(row=1, column=0, columnspan=4,  padx=10, pady=5)

        self.pomodoro_session1 = customtkinter.CTkLabel(self.sidebar_frame, text="", image=customtkinter.CTkImage(Image.open(self._resource_path("resources\\tomato_red_outline.png"))))
        self.pomodoro_session1.grid(row=2, column=0, padx=10, pady=5)
        self.pomodoro_session2 = customtkinter.CTkLabel(self.sidebar_frame, text="", image=customtkinter.CTkImage(Image.open(self._resource_path("resources\\tomato.png"))))
        self.pomodoro_session2.grid(row=2, column=1, padx=10, pady=5)
        self.pomodoro_session3 = customtkinter.CTkLabel(self.sidebar_frame, text="", image=customtkinter.CTkImage(Image.open(self._resource_path("resources\\tomato.png"))))
        self.pomodoro_session3.grid(row=2, column=2, padx=10, pady=5)
        self.pomodoro_session4 = customtkinter.CTkLabel(self.sidebar_frame, text="", image=customtkinter.CTkImage(Image.open(self._resource_path("resources\\tomato.png"))))
        self.pomodoro_session4.grid(row=2, column=3, padx=10, pady=5)

        self.plot_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Plot Mode:", anchor="w")
        self.plot_mode_label.grid(row=5, column=0, columnspan=4, padx=10, pady=5)
        self.plot_mode_optionmenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Weekly", "Monthly"], command=self.change_plot_mode_event)
        self.plot_mode_optionmenu.grid(row=6, column=0, columnspan=4, padx=10, pady=5)

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=7, column=0, columnspan=4, padx=10, pady=5)
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=8, column=0, columnspan=4, padx=10, pady=(5, 20))

        # create main frame with widgets
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0)

        # create timer (part 1 of main frame)
        self.timer = customtkinter.CTkFrame(self.main_frame)
        self.timer.grid(row=0, column=0, sticky="nsew")
        self.timer.grid_rowconfigure(0, weight=1)
        self.timer.grid_columnconfigure(0, weight=1)
        self.timer_btn = customtkinter.CTkButton(self.timer, text=self._get_formatted_time(self.time_remaining), font=customtkinter.CTkFont('Helvetica', 100), command=self.click_timer)
        self.timer_btn.grid(row=0, column=0, padx=(20,10), pady=20, sticky="nsew")
        
        # create chart (part 2 of main frame)
        self.chart = customtkinter.CTkFrame(self.main_frame)
        self.chart.grid(row=0, column=1, sticky="nsew")
        self.chart.grid_rowconfigure((0, 1), weight=1)
        self.chart.grid_columnconfigure(0, weight=1)

         # load and visualize data for study hours
        now = datetime.now()
        self.weekly_start_times, self.weekly_end_times, self.monthly_start_times, self.monthly_end_times = self._load_data(now)
        self.weekly_start_times_chart, self.weekly_end_times_chart, self.monthly_start_times_chart, self.monthly_end_times_chart = self.weekly_start_times, self.weekly_end_times, self.monthly_start_times, self.monthly_end_times
        self.chart_time = now
        self.img1, self.img2 = self._generate_charts()
        self.report1 = customtkinter.CTkLabel(self.chart, text="", image=customtkinter.CTkImage(self.img1, size=(300,215)))
        self.report1.grid(row=0, column=0, padx=(10,20), pady=(20, 5), sticky="nsew")
        self.report1.bind("<Enter>", self._on_enter_chart)
        self.report1.bind("<Leave>", self._on_leave_chart)
        self.report1.bind("<Button-1>", self.change_chart_display_data)
        self.report2 = customtkinter.CTkLabel(self.chart, text="", image=customtkinter.CTkImage(self.img2, size=(300,215)))
        self.report2.grid(row=1, column=0, padx=(10,20), pady=(5, 20), sticky="nsew")
        self.report2.bind("<Enter>", self._on_enter_chart)
        self.report2.bind("<Leave>", self._on_leave_chart)
        self.report2.bind("<Button-1>", self.change_chart_display_data)

    def change_chart_display_data(self, event):
        dialog = customtkinter.CTkInputDialog(text="Enter a date with format 'yyyy-mm-dd';\nor type 'p/n/c' for previous/next/current week", title="Choose a date to display data")
        input = dialog.get_input()

        if input == "p" or input == "P":
            if self.plot_mode == "weekly":
                self._update_charts(self.chart_time - timedelta(days=7))
            else:
                prev_month = 12 if self.chart_time.month == 1 else self.chart_time.month - 1
                year = self.chart_time.year - 1 if self.chart_time.month == 1 else self.chart_time.year
                self._update_charts(self.chart_time.replace(year=year, month=prev_month))
        elif input == "n" or input == "N":
            if self.plot_mode == "weekly":
                self._update_charts(self.chart_time + timedelta(days=7))
            else:
                next_month = 1 if self.chart_time.month == 12 else self.chart_time.month + 1
                year = self.chart_time.year + 1 if self.chart_time.month == 12 else self.chart_time.year
                self._update_charts(self.chart_time.replace(year=year, month=next_month))
        elif input == "c" or input == "C":
            self._update_charts(datetime.now())
        else:
            try:
                chart_time = datetime.strptime(input, "%Y-%m-%d")
                self._update_charts(chart_time)
            except (ValueError, TypeError):
                pass

    def _on_enter_chart(self, event):
        opacity = 0.7
        enhancer1 = ImageEnhance.Brightness(self.img1)
        dimmed_img1 = enhancer1.enhance(opacity)
        enhancer2 = ImageEnhance.Brightness(self.img2)
        dimmed_img2 = enhancer2.enhance(opacity)
        self.report1.configure(image=customtkinter.CTkImage(dimmed_img1, size=(300,215)))
        self.report2.configure(image=customtkinter.CTkImage(dimmed_img2, size=(300,215)))

    def _on_leave_chart(self, event):
        self.report1.configure(image=customtkinter.CTkImage(self.img1, size=(300,215)))
        self.report2.configure(image=customtkinter.CTkImage(self.img2, size=(300,215)))

    def _generate_charts(self):
        if self.plot_mode == "weekly":
            report1_img = self._generate_weekly_report1()
            report2_img = self._generate_weekly_report2()
        elif self.plot_mode == "monthly":
            report1_img = self._generate_monthly_report1()
            report2_img = self._generate_monthly_report2()
        return report1_img, report2_img

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_plot_mode_event(self, new_plot_mode: str):
        self.plot_mode = new_plot_mode.lower()
        self._update_charts(datetime.now())
    
    def _update_pomodoro_session_helper(self, session1_img, session2_img, session3_img, session4_img):
        tomato = customtkinter.CTkImage(Image.open(self._resource_path("resources\\tomato.png")))
        tomato_red_outline = customtkinter.CTkImage(Image.open(self._resource_path("resources\\tomato_red_outline.png")))
        tomato_red = customtkinter.CTkImage(Image.open(self._resource_path("resources\\tomato_red.png")))
        tomatoes = {0: tomato, 1: tomato_red_outline, 2: tomato_red}
        self.pomodoro_session1.configure(image = tomatoes[session1_img])
        self.pomodoro_session2.configure(image = tomatoes[session2_img])
        self.pomodoro_session3.configure(image = tomatoes[session3_img])
        self.pomodoro_session4.configure(image = tomatoes[session4_img])

    def _update_pomodoro_session(self):
        self.current_pomodoro_session = (self.current_pomodoro_session + 1) % 8
        match self.current_pomodoro_session:
            case 0: self._update_pomodoro_session_helper(1, 0, 0, 0)
            case 1: self._update_pomodoro_session_helper(2, 0, 0, 0)
            case 2: self._update_pomodoro_session_helper(2, 1, 0, 0)
            case 3: self._update_pomodoro_session_helper(2, 2, 0, 0)
            case 4: self._update_pomodoro_session_helper(2, 2, 1, 0)
            case 5: self._update_pomodoro_session_helper(2, 2, 2, 0)
            case 6: self._update_pomodoro_session_helper(2, 2, 2, 1)
            case 7: self._update_pomodoro_session_helper(2, 2, 2, 2)

    def _update_mode(self, playsound=True):
        self.mode = "break" if self.mode == "study" else "study"
        if self.mode == "study":
            self.time_remaining = STUDY_SESSION_MINS
            # after study/break session ends
            if playsound:
                winsound.PlaySound(self._resource_path("resources\\mixkit-bell-tick-tock-timer-1046.wav"), winsound.SND_ASYNC)
                self.timer_btn.configure(fg_color = ["#3a7ebf", "#1f538d"], hover_color = ["#325882", "#14375e"], text="next")
            # after using 'done' button
            else:
                self.timer_btn.configure(fg_color = ["#3a7ebf", "#1f538d"], hover_color = ["#325882", "#14375e"], text=self._get_formatted_time(self.time_remaining))
        elif self.mode == "break":
            self.time_remaining = BREAK_SESSION_MINS
            if playsound:
                winsound.PlaySound(self._resource_path("resources\\mixkit-marimba-ringtone-1359.wav"), winsound.SND_ASYNC)
                self.timer_btn.configure(fg_color = ["#479ca6", "#20484d"], hover_color = ["#20464a", "#102426"], text="next")
            else:
                self.timer_btn.configure(fg_color = ["#479ca6", "#20484d"], hover_color = ["#20464a", "#102426"], text=self._get_formatted_time(self.time_remaining))

    def _get_sleep_time(self):
        time_diff = (self.last_update_time - self.last_click_time).total_seconds()
        if time_diff % 1 == 0: return 1
        return time_diff - floor(time_diff)

    def _next(self):
        now = datetime.now()
        self.last_click_time = now
        self.last_update_time = now + timedelta(seconds=1)
        self.timer_btn.configure(text=self._get_formatted_time(self.time_remaining))
        winsound.PlaySound(None, winsound.SND_ASYNC)

    def click_timer(self):
        now = datetime.now()
        
        if self.timer_btn._text == "next":
            self._next()
            return
        
        self.pause = not self.pause
        if self.pause:
            if self.mode == "study":
                self._register_time_and_update_chart()
        else:
            time.sleep(self._get_sleep_time())
            self._update_timer()
            if self.mode == "study":
                self.last_start_time = now
        
        self.last_click_time = now


    def _register_time_and_update_chart(self):
        now = datetime.now()
        self.last_end_time = now
        self._register_time()
        # only update chart when not viewing historical data
        if (
            (self.chart_time.year == now.year) and
            ((self.plot_mode == "monthly" and self.chart_time.month == now.month) or
            (self.plot_mode == "weekly" and self._get_start_and_end_of_week(self.chart_time) == self._get_start_and_end_of_week(now)))
        ):
            self._update_charts(now)
        # except when during a study session spanning past midnight across 2 weeks/months
        elif (
            (self.last_start_time.day != self.last_end_time.day) and
            ((self.plot_mode == "monthly" and now - self.chart_time < timedelta(days=self._get_total_days_in_month(self.chart_time))) or
             (self.plot_mode == "weekly" and now - self.chart_time < timedelta(days=7)))
         ): 
            self._update_charts(now)

    def _register_time_helper(self, start_time_min, end_time_min, span_2_days, span_2_months):
        now = datetime.now()
        today = round(float(now.year) + float(now.month)/100 + float(now.day)/10000, 4)
        yesterday_now = now - timedelta(days=1)
        yesterday = round(float(yesterday_now.year) + float(yesterday_now.month)/100 + float(yesterday_now.day)/10000, 4)
        if span_2_days:
            if yesterday not in self.monthly_start_times: self.monthly_start_times = np.concatenate((self.monthly_start_times, [yesterday]))
            self.monthly_start_times = np.concatenate((self.monthly_start_times, [start_time_min]))
            if yesterday not in self.monthly_end_times: self.monthly_end_times = np.concatenate((self.monthly_end_times, [yesterday]))
            self.monthly_end_times = np.concatenate((self.monthly_end_times, [1440]))
            if span_2_months:
                self._save_data(yesterday_now)
                if end_time_min == 0:
                    self.monthly_start_times = np.array([])
                    self.monthly_end_times = np.array([])
                    return
                else:
                    self.monthly_start_times = np.array([today, 0])
                    self.monthly_end_times = np.array([today])
            else:
                if end_time_min == 0: return
                if today not in self.monthly_start_times: self.monthly_start_times = np.concatenate((self.monthly_start_times, [today]))
                self.monthly_start_times = np.concatenate((self.monthly_start_times, [0]))
        # same day
        else:
            if today not in self.monthly_start_times: self.monthly_start_times = np.concatenate((self.monthly_start_times, [today]))
            self.monthly_start_times = np.concatenate((self.monthly_start_times, [start_time_min]))

        if today not in self.monthly_end_times: self.monthly_end_times = np.concatenate((self.monthly_end_times, [today]))
        self.monthly_end_times = np.concatenate((self.monthly_end_times, [end_time_min]))
        self._save_data(now)

    def _register_time(self):
        # ignore study sessions < 1 min
        if self.last_end_time - self.last_start_time < timedelta(minutes=1): return

        midnight = self.last_start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        mins_since_midnight_for_start_time = round((self.last_start_time - midnight).total_seconds() / 60)
        # study session within 1 day 
        if self.last_end_time.day == self.last_start_time.day: 
            mins_since_midnight_for_end_time = round((self.last_end_time - midnight).total_seconds() / 60)
            self._register_time_helper(mins_since_midnight_for_start_time, mins_since_midnight_for_end_time, False, False)
        # study session spanning 2 days (crossing midnight)
        else:
            midnight2 = self.last_end_time.replace(hour=0, minute=0, second=0, microsecond=0)
            mins_since_midnight_for_end_time = round((self.last_end_time - midnight2).total_seconds() / 60)
            self._register_time_helper(mins_since_midnight_for_start_time, mins_since_midnight_for_end_time, True, self.last_end_time.month != self.last_start_time.month)

    def _update_charts(self, chart_time):
        self.chart_time = chart_time
        self.weekly_start_times_chart, self.weekly_end_times_chart, self.monthly_start_times_chart, self.monthly_end_times_chart = self._load_data(self.chart_time)
        self.img1, self.img2 = self._generate_charts()
        self.report1.configure(image=customtkinter.CTkImage(self.img1, size=(300,215)))
        self.report2.configure(image=customtkinter.CTkImage(self.img2, size=(300,215)))

    def _update_timer(self):
        now = datetime.now()
        if self.pause:
            return
        
        self.time_remaining -= 1
        if self.time_remaining <= 0:
            if self.mode == "study": 
                self._register_time_and_update_chart()
            self.pause = True
            self._update_mode()
            self._update_pomodoro_session()
            self.deiconify()
            return
            
        self.timer_btn.configure(text=self._get_formatted_time(self.time_remaining))
        self.last_update_time = now
        self.after(1000, self._update_timer)

    def _get_formatted_time(self, time: int):
        min = int(time / 60)
        sec = int(time % 60)
        return str(min).zfill(2) + ":" + str(sec).zfill(2)

    def reset(self):
        now = datetime.now()
        if self.mode == "study" and not self.pause:
            self._register_time_and_update_chart()
        self.last_click_time = now
        self.last_update_time = now + timedelta(seconds=1)
        self.mode = "study"
        self.timer_btn.configure(fg_color = ["#3a7ebf", "#1f538d"], hover_color = ["#325882", "#14375e"], text=self._get_formatted_time(self.time_remaining))
        self.pause = True
        self.current_pomodoro_session = 0
        self._update_pomodoro_session_helper(1, 0, 0, 0)
        self.time_remaining = STUDY_SESSION_MINS
        self.timer_btn.configure(text=self._get_formatted_time(self.time_remaining))

    def done(self):
        now = datetime.now()

        if self.timer_btn._text == "next":
            self._next()
            return
        
        if self.mode == "study" and not self.pause and hasattr(self, 'last_start_time'):
            self._register_time_and_update_chart()

        self.pause = True
        self._update_mode(playsound=False)
        self._update_pomodoro_session()
        self.last_click_time = now
        self.last_update_time = now + timedelta(seconds=1)

    def _get_all_dates_of_week(self, calendar_date):
        dates_of_week = []
        start_of_week = calendar_date - timedelta(days=calendar_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        current_date = start_of_week
        while current_date <= end_of_week:
            dates_of_week.append(float(current_date.strftime("%Y.%m%d")))
            current_date += timedelta(days=1)
        return dates_of_week
    
    def _process_loaded_data(self, data, calendar_date):
        start_dates = data[0]
        end_dates = data[1]
        dates_of_week = self._get_all_dates_of_week(calendar_date)
        found_month = False
        found_week = False
        new_month_idx = len(start_dates)
        week_start = len(start_dates)
        week_end = len(start_dates)

        for i, date in enumerate(start_dates):
            if date % 1 == 0:
                continue
            if calendar_date.month == floor((date % 1) * 100) and not found_month:
                new_month_idx = i
                found_month = True
            if date in dates_of_week and not found_week:
                week_start = i
                found_week = True
            if found_week and date not in dates_of_week:
                week_end = i
                break    
        
        return start_dates[week_start: week_end], end_dates[week_start: week_end], start_dates[new_month_idx:], end_dates[new_month_idx:]

    def _span_2_months_check(self, calendar_date):
        start_of_week = calendar_date - timedelta(days=calendar_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return start_of_week.month != end_of_week.month

    def _load_data(self, calendar_date):
        # get last month data as well if week spans 2 months
        if self._span_2_months_check(calendar_date):
            if calendar_date.month == 1:
                filename = str(calendar_date.year - 1) + '_12.csv'
            else:
                filename = str(calendar_date.year) + '_' + str(calendar_date.month - 1) + '.csv'
            filepath = os.path.join(self.data_folder, filename)
            try: 
                prev_month_data = np.genfromtxt(filepath, delimiter=',', dtype=float)
            except FileNotFoundError:
                pass

        filename = str(calendar_date.year) + '_' + str(calendar_date.month) + '.csv'
        filepath = os.path.join(self.data_folder, filename)
        try:
            data = np.genfromtxt(filepath, delimiter=',', dtype=float)
        except FileNotFoundError:
            # has data for last month but not this month
            if 'prev_month_data' in locals():
                return self._process_loaded_data(prev_month_data, calendar_date)
            # has no data at all
            return np.array([]), np.array([]), np.array([]), np.array([])

        if 'prev_month_data' in locals():
            data = np.concatenate((prev_month_data, data), axis=1)
        return self._process_loaded_data(data, calendar_date)
    
    def _save_data(self, calendar_date):
        if self.monthly_start_times.size == 0 or self.monthly_end_times.size == 0: return
        filename = str(calendar_date.year) + '_' + str(calendar_date.month) + '.csv'
        filepath = os.path.join(self.data_folder, filename)
        os.makedirs(self.data_folder, exist_ok=True)
        data = [self.monthly_start_times, self.monthly_end_times]
        with open(filepath, 'w') as f:
            for i in data:
                np.savetxt(f, [i], delimiter=',', fmt='%.4f')

    def _convert_calendar_date_to_weekday(self, calendar_date, date_format="%Y.%m%d"):
        if isinstance(calendar_date, datetime):
            date_obj = calendar_date
        else:
            date_obj = datetime.strptime("{:.4f}".format(calendar_date), date_format)
        return date_obj.weekday()
    
    def _get_start_and_end_of_week(self, calendar_date):
        month_dict = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
        weekday = self._convert_calendar_date_to_weekday(calendar_date)
        week_start = calendar_date - timedelta(days=weekday)
        week_end = week_start + timedelta(days=6)
        return f'{week_start.year} {month_dict[week_start.month]} {week_start.day} - {week_end.year} {month_dict[week_end.month]} {week_end.day}'

    def _generate_weekly_report1(self):
        weekdays = ['Sun', 'Sat', 'Fri', 'Thu', 'Wed', 'Tue', 'Mon']
        for i, time in enumerate(self.weekly_start_times_chart):
            if time % 1 != 0:
                day = self._convert_calendar_date_to_weekday(time)
                continue
            plt.hlines(y = 6 - day, xmin=time/60.0, xmax=self.weekly_end_times_chart[i]/60.0, color='#3a7ebf', linewidth=8)

        plt.title(self._get_start_and_end_of_week(self.chart_time))
        plt.xticks(range(24))
        plt.yticks(range(len(weekdays)), weekdays)
        plt.xlim(0, 24)
        plt.ylim(-0.5, 6.5)
        plt.subplots_adjust(left=0.07, right=0.93, top=0.93, bottom=0.07)

        buf = io.BytesIO()
        plt.savefig(buf)
        plt.close()
        buf.seek(0)
        return Image.open(buf)

    def _generate_weekly_report2(self):
        weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        working_times = []
        curr_sum = 0
        day_count = 6
        for i, time in enumerate(reversed(self.weekly_end_times_chart - self.weekly_start_times_chart)):
            # new day 
            if time == 0:
                day = self._convert_calendar_date_to_weekday(self.weekly_end_times_chart[len(self.weekly_end_times_chart) - i - 1])
                while day_count > day:
                    working_times.insert(0, 0)
                    day_count -= 1
                working_times.insert(0, curr_sum/60.0)
                curr_sum = 0
                day_count -= 1
            else:
                curr_sum += time
        while day_count >= 0: 
            working_times.insert(0, 0)
            day_count -= 1

        plt.title(self._get_start_and_end_of_week(self.chart_time))
        plt.bar(range(7), working_times, color='#3a7ebf')
        plt.xticks(range(7), weekdays)
        plt.yticks(range(15))
        plt.xlim(-0.5, 6.5)
        plt.ylim(0, 15)
        plt.subplots_adjust(left=0.07, right=0.93, top=0.93, bottom=0.07)
        
        buf = io.BytesIO()
        plt.savefig(buf)
        plt.close()
        buf.seek(0)
        return Image.open(buf)

    def _get_total_days_in_month(self, calendar_date):
        next_month = calendar_date.month % 12 + 1
        year = calendar_date.year + calendar_date.month // 12
        next_month_1st_day = datetime(year, next_month, 1)
        return (next_month_1st_day - timedelta(days=1)).day

    def _generate_monthly_report1(self):
        month_dict = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}
        total_days = self._get_total_days_in_month(self.chart_time)
        for i, time in enumerate(self.monthly_start_times_chart):
            if time % 1 != 0:
                day = round(((time * 100) % 1) * 100)
                continue
            plt.hlines(y = total_days - day + 1, xmin=time/60.0, xmax=self.monthly_end_times_chart[i]/60.0, color='#3a7ebf', linewidth=8)

        plt.title(f'{self.chart_time.year} {month_dict[self.chart_time.month]}')
        plt.xticks(range(24))
        plt.yticks(range(1, total_days + 1), range(total_days, 0, -1))
        plt.xlim(0, 24)
        plt.ylim(0.5, total_days + 0.5)
        plt.subplots_adjust(left=0.07, right=0.93, top=0.93, bottom=0.07)

        buf = io.BytesIO()
        plt.savefig(buf)
        plt.close()
        buf.seek(0)
        return Image.open(buf)

    def _generate_monthly_report2(self):
        month_dict = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}
        total_days = self._get_total_days_in_month(self.chart_time)
        working_times = []
        curr_sum = 0
        day_count = total_days
        for i, time in enumerate(reversed(self.monthly_end_times_chart -self.monthly_start_times_chart)):
            # new day
            if time == 0:
                day = round(((self.monthly_start_times_chart[len(self.monthly_start_times_chart) - i - 1] * 100) % 1) * 100)
                while day_count > day:
                    working_times.insert(0, 0)
                    day_count -= 1
                working_times.insert(0, curr_sum/60.0)
                curr_sum = 0
                day_count -= 1
            else:
                curr_sum += time

        while day_count > 0:
            working_times.insert(0, 0)
            day_count -= 1

        plt.title(f'{self.chart_time.year} {month_dict[self.chart_time.month]}')
        plt.bar(range(1, total_days + 1), working_times, color='#3a7ebf')
        plt.xticks(range(1, total_days + 1))
        plt.yticks(range(15))
        plt.xlim(0.5, total_days + 0.5)
        plt.ylim(0, 15)
        plt.subplots_adjust(left=0.07, right=0.93, top=0.93, bottom=0.07)
        
        buf = io.BytesIO()
        plt.savefig(buf)
        plt.close()
        buf.seek(0)
        return Image.open(buf)
    
    # to make pyinstaller's generated .exe not confused 
    def _resource_path(self, relative_path):
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    def on_close():
        if app.mode == "study" and not app.pause:
            app.last_end_time = datetime.now()
            app._register_time()
        app.destroy()
    
    app = App()
    app.protocol("WM_DELETE_WINDOW", on_close)
    app.mainloop()






