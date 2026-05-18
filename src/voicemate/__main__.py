"""Entry point: ``uv run voicemate-bot``."""

from __future__ import annotations

import logging

import structlog

from .bot import VoiceMateBot
from .config import load_settings


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, level.upper(), logging.INFO),
    )
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
    )


def main() -> None:
    settings = load_settings()
    _configure_logging(settings.log_level)

    log = structlog.get_logger("voicemate")
    log.info(
        "voicemate.start",
        reasoning_model=settings.mimo_reasoning_model,
        tts_model=settings.mimo_tts_model,
        stt_provider=settings.stt_provider,
    )

    bot = VoiceMateBot(settings)
    app = bot.build_application()
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
