import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, redirect, render_template, request, url_for, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import CSRFProtect
from sqlalchemy import or_, text

from config import Config
from .models import Artisan, db
from .validation import validate_artisan_form

csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=["120 per minute"])


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.testing = testing
    cfg = Config.from_env(testing=testing)
    app.config.update(
        SECRET_KEY=cfg.secret_key,
        SQLALCHEMY_DATABASE_URI=cfg.database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=cfg.max_content_length,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "1") == "1" and not testing,
        WTF_CSRF_TIME_LIMIT=3600,
        JSON_SORT_KEYS=False,
        RATELIMIT_STORAGE_URI=os.getenv("RATELIMIT_STORAGE_URI", "memory://"),
    )

    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    @app.after_request
    def add_security_headers(response):
        response.headers.update({
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; base-uri 'self'; form-action 'self'; frame-ancestors 'none'",
        })
        if not testing:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    @app.route("/", methods=["GET"])
    @limiter.limit("60 per minute")
    def index():
        query = " ".join(request.args.get("q", "", type=str).split())[:80]
        category = " ".join(request.args.get("category", "Tous", type=str).split())[:60]
        artisans_query = Artisan.query
        if query:
            pattern = f"%{query}%"
            artisans_query = artisans_query.filter(or_(Artisan.name.ilike(pattern), Artisan.job.ilike(pattern), Artisan.neighborhood.ilike(pattern)))
        if category and category != "Tous":
            artisans_query = artisans_query.filter(Artisan.job.ilike(f"%{category}%"))
        artisans = artisans_query.order_by(Artisan.created_at.desc()).limit(500).all()
        categories = [row[0] for row in db.session.query(Artisan.job).distinct().order_by(Artisan.job).limit(50).all()]
        return render_template("index.html", artisans=artisans, categories=categories, query=query, category=category)

    @app.post("/artisans")
    @limiter.limit("5 per hour")
    def create_artisan():
        if request.form.get("website", "").strip():
            flash("Inscription envoyée.", "success")
            return redirect(url_for("index"))
        payload, errors = validate_artisan_form(request.form)
        if errors:
            for message in errors.values():
                flash(message, "error")
            return redirect(url_for("index"))
        artisan = Artisan(**payload)
        db.session.add(artisan)
        db.session.commit()
        app.logger.info("artisan_created id=%s ip=%s", artisan.id, get_remote_address())
        flash("Bravo ! Ton métier est maintenant visible dans l'annuaire.", "success")
        return redirect(url_for("index"))

    @app.get("/health/live")
    def health_live():
        return jsonify(status="alive")

    @app.get("/health/ready")
    def health_ready():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify(status="ready", checks={"database": True})
        except Exception:
            app.logger.exception("readiness_check_failed")
            return jsonify(status="not_ready", checks={"database": False}), 503

    @app.errorhandler(413)
    def request_too_large(_error):
        return render_template("error.html", message="La requête est trop volumineuse."), 413

    @app.errorhandler(429)
    def too_many_requests(_error):
        return render_template("error.html", message="Trop de tentatives. Réessaie dans quelques minutes."), 429

    @app.errorhandler(500)
    def internal_error(_error):
        db.session.rollback()
        return render_template("error.html", message="Le service rencontre un souci temporaire."), 500

    configure_logging(app)
    with app.app_context():
        db.create_all()
    return app


def configure_logging(app: Flask):
    if app.testing:
        return
    handler = RotatingFileHandler("anyama-proxi.log", maxBytes=1_000_000, backupCount=3)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
