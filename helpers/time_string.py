from django.utils.translation import gettext_lazy as _


def seconds_to_text(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    parts = []
    if hours:
        parts.append(f"{hours:.2f} { _('hour') if hours in [0, 1] else _('hours') }")
    if minutes:
        parts.append(f"{minutes:.2f} { _('minute') if minutes in [0, 1] else _('minutes') }")
    if secs or not parts:
        parts.append(f"{secs:.2f} { _('second') if secs in [0, 1] else _('seconds') }")

    return ', '.join(parts[:2])



if __name__ == '__main__':
    def _(t):
        return t
    print(seconds_to_text(3670))
    print(seconds_to_text(7670))
    print(seconds_to_text(70))
    print(seconds_to_text(30))
