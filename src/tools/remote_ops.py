import os
import asyncio
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import config
# This import now works perfectly because of the alias in dashboard.py
from src.ui.dashboard import db

# Initialize bridge logger for remote operations tracking
logger = logging.getLogger("remotion_bridge")

class RemoteCommander:
    """
    v7.1 ASSET COMMANDER (Eternal Loop Edition).
    Handles remote orchestration, smart asset management, and atomic task injection.
    Synchronized with the Async Hybrid Permission system.
    """
    _app: Application = None
    _permission_event = asyncio.Event()
    _last_permission_result = False

    @classmethod
    async def start_bot(cls):
        """Initializes the Telegram bot and registers advanced command handlers."""
        if not config.TELEGRAM_ENABLED or not config.TELEGRAM_TOKEN:
            return

        db.log("SERVER", "Booting Asset Commander Gateway...")
        
        try:
            cls._app = Application.builder().token(config.TELEGRAM_TOKEN).build()

            # Command Handlers
            cls._app.add_handler(CommandHandler("start", cls._cmd_start))
            cls._app.add_handler(CommandHandler("help", cls._cmd_help))
            cls._app.add_handler(CommandHandler("status", cls._cmd_status))
            cls._app.add_handler(CommandHandler("assets", cls._cmd_assets))
            cls._app.add_handler(CommandHandler("delete", cls._cmd_delete))
            
            cls._app.add_handler(CallbackQueryHandler(cls._handle_permission_callback))

            # Media Handlers for Smart Naming (Photos and Docs)
            cls._app.add_handler(MessageHandler(
                (filters.PHOTO | filters.Document.ALL) & ~filters.COMMAND, 
                cls._handle_media_upload
            ))

            # Text Prompt Handler (Eternal Loop Integration)
            cls._app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cls._handle_remote_prompt))

            # Initialize and start polling asynchronously
            await cls._app.initialize()
            await cls._app.start()
            await cls._app.updater.start_polling(drop_pending_updates=True)
            
            db.log("SUCCESS", "Remote Commander fully armed for Eternal Loop.")
            
            await cls._app.bot.send_message(
                chat_id=config.AUTHORIZED_CHAT_ID,
                text="🦁 *ASSET COMMANDER ONLINE*\nEternal Watcher is active. PC is waiting for instructions.",
                parse_mode="Markdown"
            )

        except Exception as e:
            db.log("ERROR", f"Telegram Gateway failure: {str(e)}")

    @staticmethod
    async def _cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the /start command."""
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        await update.message.reply_text(f"👋 Greetings HIRUNA!\nYour PC is linked. Use /help for remote features.")

    @staticmethod
    async def _cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Displays available remote commands."""
        help_msg = (
            "🚀 *REMOTE COMMANDER v7.1*\n\n"
            "💬 *Send Text* - Starts a new mission\n"
            "🛑 *Send 'STOP'* - Terminates the AI loop\n"
            "🖼️ *Image + Caption* - Saves asset with custom name\n"
            "📊 /assets - List project assets\n"
            "🗑️ /delete [name] - Remove an asset\n"
            "📡 /status - Check system radar"
        )
        await update.message.reply_markdown(help_msg)

    @staticmethod
    async def _cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Sends a mission control report to the phone."""
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        status_card = (
            "📡 *MISSION CONTROL RADAR*\n"
            "───────────────────\n"
            f"✅ *State:* Immortal Online\n"
            f"⚙️ *Mode:* {config.SELECTED_MODE}\n"
            f"📂 *Target:* `{os.path.basename(config.PROJECT_ROOT)}`"
        )
        await update.message.reply_markdown(status_card)

    @staticmethod
    async def _cmd_assets(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lists files in the project's public directory."""
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        try:
            files = os.listdir(config.PUBLIC_DIR)
            if not files:
                await update.message.reply_text("📂 Public folder is empty.")
                return
            list_msg = "📂 *PROJECT ASSETS*\n───────────────────\n"
            for f in files:
                emoji = "🖼️" if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg')) else "📄"
                size = os.path.getsize(os.path.join(config.PUBLIC_DIR, f)) / 1024
                list_msg += f"{emoji} `{f}` ({size:.1f} KB)\n"
            await update.message.reply_markdown(list_msg)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

    @staticmethod
    async def _cmd_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Prepares a deletion request with confirmation buttons."""
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        if not context.args:
            await update.message.reply_text("❓ Usage: /delete logo.png")
            return
        filename = context.args[0]
        file_path = os.path.join(config.PUBLIC_DIR, filename)
        if not os.path.exists(file_path):
            await update.message.reply_text(f"🚫 `{filename}` not found.")
            return
        keyboard = [[InlineKeyboardButton("🗑️ YES, DELETE", callback_data=f"del_yes:{filename}"),
                     InlineKeyboardButton("❌ NO, CANCEL", callback_data="del_no")]]
        await update.message.reply_text(f"🛡️ *CONFIRM DELETION*\nDelete `{filename}`?", 
                                      reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    @classmethod
    async def _handle_media_upload(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Downloads assets from Telegram to the public folder with smart naming."""
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        message = update.message
        caption = message.caption
        db.log("REMOTE", "Syncing asset from phone...")
        try:
            if message.photo:
                media_file = await message.photo[-1].get_file()
                filename = config.sanitize_filename(caption) if caption and '.' in caption else f"asset_{datetime.now().strftime('%H%M%S')}.jpg"
            else:
                media_file = await message.document.get_file()
                filename = config.sanitize_filename(caption) if caption else message.document.file_name

            os.makedirs(config.PUBLIC_DIR, exist_ok=True)
            file_path = os.path.join(config.PUBLIC_DIR, filename)
            await media_file.download_to_drive(file_path)
            db.log("SUCCESS", f"Remote asset synced: {filename}")
            
            # Update AI task context with new asset info
            with open(config.REMOTE_TASK_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n\n📎 [ASSET UPDATE]: New asset '{filename}' added. Reference it via staticFile('{filename}').")
            
            await update.message.reply_text(f"📥 *ASSET SYNCED ✅*\nFile: `{filename}`")
        except Exception as e:
            db.log("ERROR", f"Asset sync failure: {e}")
            await update.message.reply_text(f"❌ *SYNC ERROR:* {e}")

    @classmethod
    async def _handle_remote_prompt(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Captures text prompts and injects them into the mission loop."""
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        prompt = update.message.text
        
        # Check for Kill-Switch instruction
        if prompt.upper() in ["STOP", "EXIT", "STOP_WORK"]:
            db.log("SERVER", "Remote shutdown signal received.")
            payload = "STOP_WORK"
        else:
            db.log("REMOTE", f"New mission captured: {prompt[:30]}...")
            payload = prompt

        try:
            os.makedirs(os.path.dirname(config.REMOTE_TASK_FILE), exist_ok=True)
            with open(config.REMOTE_TASK_FILE, "w", encoding="utf-8") as f:
                f.write(payload)
            
            status = "🛑 *TERMINATION SIGNAL SENT*" if payload == "STOP_WORK" else "⚡ *MISSION SYNCED ✅*"
            await update.message.reply_text(status, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ *SYNC ERROR:* {e}")

    @classmethod
    async def send_notification(cls, message: str):
        """Pushes real-time terminal notifications to the phone."""
        if cls._app and config.TELEGRAM_ENABLED:
            try: await cls._app.bot.send_message(chat_id=config.AUTHORIZED_CHAT_ID, text=message)
            except: pass

    @classmethod
    async def ask_hybrid_permission(cls, tool_name: str, target: str) -> bool:
        """
        Remote/Local Permission Gate. 
        Blocks the server loop until authorized via phone or terminal.
        """
        if not cls._app or not config.TELEGRAM_ENABLED:
            return await db.ask_permission(tool_name, target)

        db.log("GUARD", f"Awaiting remote authorization for '{tool_name}'...", style="bold magenta")
        keyboard = [[InlineKeyboardButton("✅ APPROVE", callback_data="perm_yes"), InlineKeyboardButton("❌ DENY", callback_data="perm_no")]]
        
        # Reset event state for current request
        cls._permission_event.clear()
        
        msg = f"⚠️ *AUTHORIZATION REQUIRED*\n\nAI wants to: `{tool_name}`\nTarget: `{target}`"
        await cls._app.bot.send_message(chat_id=config.AUTHORIZED_CHAT_ID, text=msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
        # Async Wait for interaction
        await cls._permission_event.wait()
        return cls._last_permission_result

    @classmethod
    async def _handle_permission_callback(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processes interaction feedback from the phone."""
        query = update.callback_query
        await query.answer()
        data = query.data

        # 1. Handle Deletion Confirmation logic
        if data.startswith("del_"):
            if data.startswith("del_yes:"):
                filename = data.split(":")[1]
                try:
                    os.remove(os.path.join(config.PUBLIC_DIR, filename))
                    await query.edit_message_text(text=f"🗑️ *DELETED:* `{filename}` successfully removed.")
                    db.log("CLEAN", f"Remote cleanup: {filename}")
                except Exception as e:
                    await query.edit_message_text(text=f"❌ *ERROR:* {e}")
            else:
                await query.edit_message_text(text="❌ Deletion cancelled.")
            return

        # 2. Handle Tool Approval logic
        if data == "perm_yes":
            cls._last_permission_result = True
            await query.edit_message_text(text="✅ *PERMISSION GRANTED* (Executing on PC...)")
            db.log("SUCCESS", "Action approved remotely.")
        else:
            cls._last_permission_result = False
            await query.edit_message_text(text="❌ *PERMISSION DENIED* (Aborted locally.)")
            db.log("ERROR", "Action rejected remotely.")
        
        # Release the waiting server thread
        cls._permission_event.set()