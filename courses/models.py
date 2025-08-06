from django.db import models
from django.utils.crypto import get_random_string
from django.utils import timezone
import datetime


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class TimeTable(models.Model):
    """Weekly recurring schedule (e.g., every Mon 10:00 for 120 mins)."""
    MON, TUE, WED, THU, FRI, SAT, SUN = range(7)
    DAY_CHOICES = [
        (MON, "Monday"), (TUE, "Tuesday"), (WED, "Wednesday"),
        (THU, "Thursday"), (FRI, "Friday"), (SAT, "Saturday"), (SUN, "Sunday"),
    ]

    course   = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="timetables")
    lecturer = models.ForeignKey("users.Lecturer", on_delete=models.CASCADE, related_name="timetables")

    day_of_week      = models.IntegerField(choices=DAY_CHOICES)
    start_time       = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=60)  # typically 60 or 120
    location         = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["course__code", "day_of_week", "start_time"]
        unique_together = ("course", "lecturer", "day_of_week", "start_time")

    def __str__(self):
        return f"{self.course.code} - {self.get_day_of_week_display()} {self.start_time} ({self.duration_minutes}m)"


class ClassSession(models.Model):
    """
    One concrete class meeting (timetable-derived or fixed/ad-hoc).
    Attendance is tied to this record.
    """
    course    = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sessions")
    timetable = models.ForeignKey(TimeTable, on_delete=models.SET_NULL, null=True, blank=True, related_name="sessions")
    lecturer  = models.ForeignKey("users.Lecturer", on_delete=models.CASCADE, related_name="sessions")

    # This meeting’s date/time
    session_date     = models.DateField()
    start_time       = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    location         = models.CharField(max_length=120, blank=True)

    # Fixed/ad-hoc flag
    is_adhoc = models.BooleanField(default=False)

    # QR double-check controls (lecturer can activate in class)
    require_qr_verification = models.BooleanField(default=False)
    qr_active = models.BooleanField(default=False)
    session_qr_token = models.CharField(max_length=64, blank=True, null=True, unique=True)

    # Cancellation
    is_cancelled = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-session_date", "-start_time"]
        indexes = [
            models.Index(fields=["session_date", "start_time"]),
            models.Index(fields=["course", "session_date"]),
            models.Index(fields=["lecturer", "session_date"]),
        ]
        unique_together = ("course", "lecturer", "session_date", "start_time")

    def __str__(self):
        return f"{self.course.code} @ {self.session_date} {self.start_time:%H:%M} by {self.lecturer}"

    # ----- Helpers you’ll use in DRF views/services -----
    def ensure_session_qr_token(self):
        if not self.session_qr_token:
            self.session_qr_token = get_random_string(40)

    def start_datetime(self) -> datetime.datetime:
        return datetime.datetime.combine(
            self.session_date, self.start_time, tzinfo=timezone.get_current_timezone()
        )

    def window_open_datetime(self) -> datetime.datetime:
        """Attendance opens 15 minutes before the start time."""
        return self.start_datetime() - datetime.timedelta(minutes=15)

    def window_close_datetime(self) -> datetime.datetime:
        """Attendance closes 30 minutes after the start time."""
        return self.start_datetime() + datetime.timedelta(minutes=30)

    def is_within_attendance_window(self, now: datetime.datetime | None = None) -> bool:
        if self.is_cancelled:
            return False
        now = now or timezone.now()
        return self.window_open_datetime() <= now <= self.window_close_datetime()
