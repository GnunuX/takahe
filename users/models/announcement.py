import markdown_it
import urlman
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe


class Announcement(models.Model):
    """
    A server-wide announcement that users all see and can dismiss.
    """

    text = models.TextField(
        help_text="The text of your announcement.\nAccepts Markdown for formatting."
    )

    published = models.BooleanField(
        default=False,
        help_text="If this announcement will appear on the site.\nIt must still be between start and end times, if provided.",
    )
    start = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the announcement will start appearing.\nLeave blank to have it begin as soon as it is published.\nFormat: <tt>2023-01-01</tt> or <tt>2023-01-01 12:30:00</tt>",
    )
    end = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the announcement will stop appearing.\nLeave blank to have it display indefinitely.\nFormat: <tt>2023-01-01</tt> or <tt>2023-01-01 12:30:00</tt>",
    )

    include_unauthenticated = models.BooleanField(default=False)

    # Note that this is against User, not Identity - it's one of the few places
    # where we want it to be per login.
    seen = models.ManyToManyField("users.User", blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class urls(urlman.Urls):
        dismiss = "/announcements/{self.pk}/dismiss/"
        admin_root = "/admin/announcements/"
        admin_edit = "{admin_root}{self.pk}/"
        admin_delete = "{admin_edit}delete/"
        admin_publish = "{admin_root}{self.pk}/publish/"
        admin_unpublish = "{admin_root}{self.pk}/unpublish/"

    @property
    def html(self) -> str:
        return mark_safe(markdown_it.MarkdownIt().render(self.text))

    @property
    def visible(self) -> bool:
        return self.published and self.after_start and self.before_end

    @property
    def after_start(self) -> bool:
        return timezone.now() >= self.start if self.start else True

    @property
    def before_end(self) -> bool:
        return timezone.now() <= self.end if self.end else True
