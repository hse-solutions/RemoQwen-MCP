import os
import asyncio
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import config
from src.ui.dashboard import Dashboard as db

# Initialize internal logging
logger = logging.getLogger("remotion_bridge")

class RemoteCommander:
    """
    v7.0 REMOTE COMMANDER: Ultimate Gateway with Asset Ingestion.
    Features: Silent Task Sync, Hybrid Permissions, and Remote Public Asset Sync.
    """
    _app: Application = None
    _permission_event = asyncio.Event()
    _last_permission_result = False

    @classmethod
    async def start_bot(cls):
        """Initializes the Telegram bot and registers media sniffers."""
        if not config.TELEGRAM_ENABLED or not config.TELEGRAM_TOKEN:
            return

        db.log("SERVER", "Booting Remote Commander with Media Support...")
        
        try:
            cls._app = Application.builder().token(config.TELEGRAM_TOKEN).build()

            # Command Handlers
            cls._app.add_handler(CommandHandler("start", cls._cmd_start))
            cls._app.add_handler(CommandHandler("help", cls._cmd_help))
            cls._app.add_handler(CommandHandler("status", cls._cmd_status))
            cls._app.add_handler(CallbackQueryHandler(cls._handle_permission_callback))

            # NEW: Media Handlers (Photos and Documents)
            cls._app.add_handler(MessageHandler(
                (filters.PHOTO | filters.Document.ALL) & ~filters.COMMAND, 
                cls._handle_media_upload
            ))

            # Existing Text Prompt Handler
            cls._app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cls._handle_remote_prompt))

            await cls._app.initialize()
            await cls._app.start()
            await cls._app.updater.start_polling(drop_pending_updates=True)
            
            db.log("SUCCESS", "Remote Gateway is fully armed and synced.")
            
            await cls._app.bot.send_message(
                chat_id=config.AUTHORIZED_CHAT_ID,
                text="🦁 *SENTINEL LION ONLINE*\nI can now receive images and logos directly from your phone.",
                parse_mode="Markdown"
            )

        except Exception as e:
            db.log("ERROR", f"Gateway failure: {str(e)}")

    @staticmethod
    async def _cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        await update.message.reply_text(f"👋 Boss, I'm ready!\nSend me text for a mission or an image for your public folder.")

    @staticmethod
    async def _cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_msg = "🚀 *REMOTE MANUAL*\n\n💬 *Just Text* - Injects a task\n🖼️ *Send Image* - Saves to public folder\n📊 /status - Real-time radar"
        await update.message.reply_markdown(help_msg)

    @staticmethod
    async def _cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        status_card = (
            "📡 *MISSION CONTROL RADAR*\n"
            "───────────────────\n"
            f"✅ *State:* Immortal Online\n"
            f"⚙️ *Mode:* {config.SELECTED_MODE}\n"
            f"📍 *Project:* `{os.path.basename(config.PROJECT_ROOT)}`"
        )
        await update.message.reply_markdown(status_card)

    @classmethod
    async def _handle_media_upload(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        ATOMIC ASSET SYNC: Captures images/documents and saves to public folder.
        Informs the AI of the new asset automatically.
        """
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        
        message = update.message
        db.log("REMOTE", "Receiving media asset from phone...")

        try:
            # 1. Determine file details
            if message.photo:
                # Get the highest resolution version
                media_file = await message.photo[-1].get_file()
                filename = f"telegram_asset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            else:
                # Handle as a document (keeps original name)
                media_file = await message.document.get_file()
                filename = message.document.file_name

            # 2. Secure target path in public/ folder
            os.makedirs(config.PUBLIC_DIR, exist_ok=True)
            file_path = os.path.join(config.PUBLIC_DIR, filename)

            # 3. Download directly to project
            await media_file.download_to_drive(file_path)
            db.log("SUCCESS", f"Remote asset synced: {filename}")

            # 4. Notify AI by updating the current task file
            with open(config.REMOTE_TASK_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n\n📎 [ASSET UPDATE]: New asset '{filename}' added to public folder. You can use it via staticFile('{filename}').")

            await update.message.reply_text(f"📥 *ASSET SYNCED ✅*\nFile: `{filename}`\nAvailable for AI immediately.")

        except Exception as e:
            db.log("ERROR", f"Asset sync failed: {str(e)}")
            await update.message.reply_text(f"❌ *SYNC ERROR:* {e}")

    @classmethod
    async def _handle_remote_prompt(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Silent Task Sync (Preserved from previous version)"""
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        prompt = update.message.text
        db.log("REMOTE", f"Capturing remote instruction: {prompt[:30]}...")

        try:
            os.makedirs(os.path.dirname(config.REMOTE_TASK_FILE), exist_ok=True)
            with open(config.REMOTE_TASK_FILE, "w", encoding="utf-8") as f:
                f.write(f"# 🚨 REMOTE MISSION RECEIVED\n\n{prompt}\n\n---\n*Source: Telegram Remote Commander*")
            
            db.log("SUCCESS", "Remote task synchronized with AI brain.")
            await update.message.reply_text("⚡ *TASK SYNCED ✅*\nQwen is being notified.")
        except Exception as e:
            db.log("ERROR", f"Silent sync failed: {str(e)}")
            await update.message.reply_text(f"❌ *SYNC ERROR:* {e}")

    @classmethod
    async def send_notification(cls, message: str):
        if cls._app and config.TELEGRAM_ENABLED:
            try: await cls._app.bot.send_message(chat_id=config.AUTHORIZED_CHAT_ID, text=message)
            except: pass

    @classmethod
    async def ask_hybrid_permission(cls, tool_name: str, target: str) -> bool:
        if not cls._app or not config.TELEGRAM_ENABLED:
            return await db.ask_permission(tool_name, target)

        db.log("GUARD", f"Awaiting remote authorization for '{tool_name}'...", style="bold magenta")
        keyboard = [[InlineKeyboardButton("✅ APPROVE", callback_data="perm_yes"), InlineKeyboardButton("❌ DENY", callback_data="perm_no")]]
        cls._permission_event.clear()
        msg = f"⚠️ *AUTHORIZATION REQUIRED*\n\nAI wants to: `{tool_name}`\nTarget: `{target}`"
        await cls._app.bot.send_message(chat_id=config.AUTHORIZED_CHAT_ID, text=msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        await cls._permission_event.wait()
        return cls._last_permission_result

    @classmethod
    async def _handle_permission_callback(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        if query.data == "perm_yes":
            cls._last_permission_result = True
            await query.edit_message_text(text="✅ *PERMISSION GRANTED*")
            db.log("SUCCESS", "Remote approval received.")
        else:
            cls._last_permission_result = False
            await query.edit_message_text(text="❌ *PERMISSION DENIED*")
            db.log("ERROR", "Remote rejection received.")
        cls._permission_event.set()