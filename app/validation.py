import re
import unicodedata

NAME_RE = re.compile(r"^[\wÀ-ÖØ-öø-ÿ .'-]+$", re.UNICODE)
JOB_RE = re.compile(r"^[\wÀ-ÖØ-öø-ÿ /&().'-]+$", re.UNICODE)
PHONE_RE = re.compile(r"^[0-9 +().-]+$")


def clean_text(value: str, max_length: int) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    return " ".join(value.strip().split())[:max_length]


def validate_artisan_form(form) -> tuple[dict, dict]:
    name = clean_text(form.get("name", ""), 80)
    job = clean_text(form.get("job", ""), 60)
    neighborhood = clean_text(form.get("neighborhood", ""), 80)
    phone = clean_text(form.get("phone", ""), 32)
    errors = {}

    if not 2 <= len(name) <= 80 or not NAME_RE.fullmatch(name):
        errors["name"] = "Entre un nom valide (2 à 80 caractères)."
    if not 2 <= len(job) <= 60 or not JOB_RE.fullmatch(job):
        errors["job"] = "Entre un métier valide (2 à 60 caractères)."
    if not 2 <= len(neighborhood) <= 80 or not NAME_RE.fullmatch(neighborhood):
        errors["neighborhood"] = "Entre un quartier valide (2 à 80 caractères)."
    digits = re.sub(r"\D", "", phone)
    if not 8 <= len(digits) <= 15 or not PHONE_RE.fullmatch(phone):
        errors["phone"] = "Entre un numéro valide (8 à 15 chiffres)."

    return {
        "name": name,
        "job": job,
        "neighborhood": neighborhood,
        "phone": phone,
    }, errors
