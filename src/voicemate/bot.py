"""Telegram bot wiring: voice in, MiMo reason, voice out."""

from __future__ import annotations

import tempfile
from pathlib import Path

import structlog
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .config import Settings
from .llm import ChatMessage, MimoReasoningClient
from .memory import ConversationMemory
from .stt import SpeechToText, build_stt
from .tts import MimoTTSClient

log = structlog.get_logger(__name__)


class VoiceMateBot:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._stt: SpeechToText = build_stt(
            settings.stt_provider,
            openai_api_key=settings.openai_api_key,
            openai_model=settings.openai_stt_model,
        )
        self._llm = MimoReasoningClient(
            api_key=settings.mimo_api_key,
            base_url=settings.mimo_base_url,
            model=settings.mimo_reasoning_model,
        )
        self._tts = MimoTTSClient(
            api_key=settings.mimo_api_key,
            base_url=settings.mimo_base_url,
            model=settings.mimo_tts_model,
            voice=settings.mimo_tts_voice,
        )
        self._memory = ConversationMemory(char_budget=settings.memory_budget_chars)

    # ---------------------------- handlers ---------------------------- #

    async def cmd_start(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._authorized(update):
            return
        await update.message.reply_text(
            "Halo! Gw VoiceMate ID. Kirim voice note Bahasa Indonesia, "
            "nanti gw jawab pake suara juga.\n\n"
            "/reset untuk hapus memori percakapan."
        )

    async def cmd_reset(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._authorized(update):
            return
        self._memory.reset(update.effective_user.id)
        await update.message.reply_text("Memori percakapan udah gw reset. ✨")

    async def on_voice(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._authorized(update):
            return
        msg = update.message
        user_id = update.effective_user.id

        await msg.chat.send_action(ChatAction.RECORD_VOICE)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            in_path = tmp / "in.ogg"
            out_path = tmp / "out.mp3"

            voice_file = await msg.voice.get_file()
            await voice_file.download_to_drive(custom_path=in_path)

            try:
                user_text = await self._stt.transcribe(in_path)
            except Exception:
                log.exception("stt.failed", user_id=user_id)
                await msg.reply_text("Maaf, gagal proses voice note-nya. Coba ulang ya.")
                return

            if not user_text:
                await msg.reply_text("Hmm, suaranya ga kedengeran jelas. Coba ulang?")
                return

            log.info("voice.in", user_id=user_id, chars=len(user_text))

            self._memory.append(user_id, ChatMessage(role="user", content=user_text))
            messages = [
                ChatMessage(role="system", content=self._settings.persona),
                *self._memory.history(user_id),
            ]

            try:
                reply_text = await self._llm.reply(messages)
            except Exception:
                log.exception("llm.failed", user_id=user_id)
                await msg.reply_text("Maaf, model lagi error. Coba lagi sebentar.")
                return

            if not reply_text:
                await msg.reply_text("Hmm, gw belum kepikiran jawaban. Coba tanya lagi?")
                return

            self._memory.append(user_id, ChatMessage(role="assistant", content=reply_text))

            # Send text first so the user can read while audio renders.
            await msg.reply_text(reply_text)

            try:
                await self._tts.synthesize(reply_text, out_path)
                await msg.reply_voice(voice=out_path.read_bytes())
            except Exception:
                log.exception("tts.failed", user_id=user_id)
                # Text reply already sent; don't fail the turn.

    async def on_text(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._authorized(update):
            return
        await update.message.reply_text(
            "Kirim voice note Bahasa Indonesia ya. Gw bisa jawab balik pake suara juga. 🎙️"
        )

    # ---------------------------- internals ---------------------------- #

    def _authorized(self, update: Update) -> bool:
        allow = self._settings.allowed_user_ids
        if not allow:
            return True
        uid = update.effective_user.id if update.effective_user else None
        return uid in allow

    # ---------------------------- bootstrap ---------------------------- #

    def build_application(self) -> Application:
        app = Application.builder().token(self._settings.telegram_bot_token).build()
        app.add_handler(CommandHandler("start", self.cmd_start))
        app.add_handler(CommandHandler("reset", self.cmd_reset))
        app.add_handler(MessageHandler(filters.VOICE, self.on_voice))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.on_text))
        return app
