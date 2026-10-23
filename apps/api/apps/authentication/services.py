import hashlib
import hmac
import secrets
import redis
from django.conf import settings
from utils import send_async_mail

from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)


def blacklist_user_refresh_tokens(user):
    outstanding_tokens = OutstandingToken.objects.filter(user=user)

    for outstanding_token in outstanding_tokens:
        BlacklistedToken.objects.get_or_create(
            token=outstanding_token
        )


OTP_TTL = 300
OTP_RESEND_DELAY = 60
OTP_MAX_ATTEMPTS = 5


# اتصال به همان Redis تعریف‌شده در CACHES
redis_client = redis.Redis.from_url(
    settings.CACHES["default"]["LOCATION"],
    decode_responses=True,
)


def _email_digest(email):
    normalized_email = email.strip().lower()
    return hashlib.sha256(normalized_email.encode("utf-8")).hexdigest()


def _otp_cache_key(email):
    return f"auth:otp:{_email_digest(email)}"


def _cooldown_cache_key(email):
    return f"auth:otp:cooldown:{_email_digest(email)}"


def _otp_hash(code):
    """
    HMAC prevents a leaked OTP hash from being directly
    verified through a simple offline six-digit search,
    provided SECRET_KEY remains secret.
    """
    key = settings.SECRET_KEY.encode("utf-8")
    message = code.encode("utf-8")

    return hmac.new(key, message, hashlib.sha256).hexdigest()


def request_email_otp(email):
    email = email.strip().lower()

    otp_key = _otp_cache_key(email)
    cooldown_key = _cooldown_cache_key(email)

    # Atomic cooldown creation: only one request wins.
    cooldown_created = redis_client.set(
        cooldown_key,
        "1",
        nx=True,
        ex=OTP_RESEND_DELAY,
    )

    if not cooldown_created:
        return False

    code = f"{secrets.randbelow(1_000_000):06d}"

    try:
        # Store the hash and attempt counter in a Redis hash.
        # EXPIRE sets the fixed lifetime of the OTP.
        with redis_client.pipeline(transaction=True) as pipe:
            pipe.hset(
                otp_key,
                mapping={
                    "code_hash": _otp_hash(code),
                    "attempts": 0,
                },
            )
            pipe.expire(otp_key, OTP_TTL)
            pipe.execute()

        send_async_mail(
            subject="کد تأیید ورود به Bookito",
            message=(
                f"کد تأیید شما: {code}\n"
                "این کد تا ۵ دقیقه معتبر است. "
                "اگر این درخواست متعلق به شما نیست، "
                "آن را نادیده بگیرید."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

    except Exception:
        # Cleanup is best-effort; Redis itself could be unavailable.
        try:
            redis_client.delete(otp_key, cooldown_key)
        except redis.RedisError:
            pass

        raise

    return True


_VERIFY_OTP_SCRIPT = redis_client.register_script(
    """
    local key = KEYS[1]
    local submitted_hash = ARGV[1]
    local max_attempts = tonumber(ARGV[2])

    if redis.call('EXISTS', key) == 0 then
        return 0
    end

    local attempts = tonumber(
        redis.call('HGET', key, 'attempts') or '0'
    )

    if attempts >= max_attempts then
        redis.call('DEL', key)
        return 0
    end

    local stored_hash = redis.call('HGET', key, 'code_hash')

    if stored_hash == submitted_hash then
        redis.call('DEL', key)
        return 1
    end

    attempts = redis.call('HINCRBY', key, 'attempts', 1)

    if attempts >= max_attempts then
        redis.call('DEL', key)
    end

    return 0
    """
)


def verify_email_otp(email, code):
    email = email.strip().lower()

    result = _VERIFY_OTP_SCRIPT(
        keys=[_otp_cache_key(email)],
        args=[
            _otp_hash(code),
            OTP_MAX_ATTEMPTS,
        ],
    )

    return result == 1