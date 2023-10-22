from django.db import models

from datetime import time, date, datetime

from accounts.models import User, UserProfile
from accounts.utils import send_notification


# Vendor
class Vendor(models.Model):
    user = models.OneToOneField(
        User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(
        UserProfile, related_name='user_profile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50, unique=True)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name

    def is_open(self):
        # check current day's opening hours
        today_date = date.today()
        today = today_date.isoweekday()
        current_opening_hours = OpeningHour.objects.filter(
            vendor=self, day=today)
        now = datetime.now()
        current_time = now.strftime('%H:%M:%S')
        is_open = None

        # check time open now
        for i in current_opening_hours:
            if not i.is_closed:
                start = str(datetime.strptime(i.from_hour, "%H:%M %p").time())
                end = str(datetime.strptime(i.to_hour, '%H:%M %p').time())

                if current_time > start and current_time < end:
                    is_open = True
                    break
                else:
                    is_open = False
            else:
                is_open = False

        return is_open

    def save(self, *args, **kwargs):
        if self.pk is not None:
            # get vendor
            orig = Vendor.objects.get(pk=self.pk)

            # check vendor approved
            if orig.is_approved != self.is_approved:
                mail_template = 'accounts/emails/admin_approval_email.html'
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved,
                    'to_email': self.user.email,
                }

                # if true
                if self.is_approved == True:
                    # Send notification email
                    mail_subject = 'Congratulations! Your restaurant has been approved.'
                    send_notification(mail_subject, mail_template, context)
                else:
                    # Send notification email
                    mail_subject = "We're sorry! you are not eligible for publishing your food menu on our marketplace."
                    send_notification(mail_subject, mail_template, context)

        return super(Vendor, self).save(*args, **kwargs)


DAYS = [
    (1, ('Monday')),
    (2, ('Tuesday')),
    (3, ('Wednesday')),
    (4, ('Thursday')),
    (5, ('Friday')),
    (6, ('Saturday')),
    (7, ('Sunday')),
]

HOURS_OF_DAY = [(time(h, m).strftime('%H:%M %p'), time(h, m).strftime('%H:%M %p'))
                for h in range(0, 24) for m in (0, 30)]


class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(
        choices=HOURS_OF_DAY, max_length=10, blank=True)
    to_hour = models.CharField(choices=HOURS_OF_DAY, max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day', '-from_hour')
        unique_together = ('vendor', 'day', 'from_hour', 'to_hour')

    def __str__(self):
        return self.get_day_display()
