import re

from app.models.user import User, UserStatus


IP_V6_REGEX = re.compile(r"\[([0-9a-fA-F:]+)\]:\d+\s+accepted")
IP_V4_REGEX = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
EMAIL_REGEX = re.compile(r"email:\s*([A-Za-z0-9._%+-]+)")

def parse_log_to_user(log)-> str:
    try:
        ip_v6_match = IP_V6_REGEX.search(log)
        ip_v4_match = IP_V4_REGEX.search(log)
        email_match = EMAIL_REGEX.search(log)

        if ip_v6_match:
            ip = ip_v6_match.group(1)
        elif ip_v4_match:
            ip = ip_v4_match.group(1)

        if email_match:
            email = email_match.group(1)
            email = re.sub(r"^\d+\.", "", email)

        if email:
            return User(
                name=email,
                ip=ip,
                status=UserStatus.ACTIVE,
                count=0
            )
        return None
    except :
        return None
    