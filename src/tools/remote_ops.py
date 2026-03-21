import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import config
from src.ui.dashboard import Dashboard as db

# Initialize bridge logger
logger = logging.getLogger("remotion_bridge")

class RemoteCommander:
    """
    v7.0 REMOTE GATEWAY: The Heart of the Remote Commander.
    Handles Telegram orchestration, hybrid permissions, and path-safe task injection.
    """
    _app: Application = None
    _permission_event = asyncio.Event()
    _last_permission_result = False

    @classmethod
    async def start_bot(cls):
        """Initializes and starts the Telegram Bot polling within the existing server loop."""
        if not config.TELEGRAM_ENABLED or not config.TELEGRAM_TOKEN:
            return

        db.log("SERVER", "Booting Telegram Remote Gateway...")
        
        try:
            # Build the Telegram Application instance
            cls._app = Application.builder().token(config.TELEGRAM_TOKEN).build()

            # Register Command and Action Handlers
            cls._app.add_handler(CommandHandler("start", cls._cmd_start))
            cls._app.add_handler(CommandHandler("help", cls._cmd_help))
            cls._app.add_handler(CommandHandler("status", cls._cmd_status))
            cls._app.add_handler(CallbackQueryHandler(cls._handle_permission_callback))
            cls._app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cls._handle_remote_prompt))

            # Startup Sequence: Initialize -> Start -> Start Polling
            await cls._app.initialize()
            await cls._app.start()
            await cls._app.updater.start_polling(drop_pending_updates=True)
            
            db.log("SUCCESS", "Remote Commander linked and encrypted.")
            
            # Send initial confirmation to the phone
            await cls._app.bot.send_message(
                chat_id=config.AUTHORIZED_CHAT_ID,
                text="🦁 *SENTINEL LION ONLINE*\nRemote Commander is active. Use /status to check terminal.",
                parse_mode="Markdown"
            )

        except Exception as e:
            db.log("ERROR", f"Telegram Gateway failure: {str(e)}")

    @staticmethod
    async def _cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        await update.message.reply_text(
            f"👋 Welcome Boss!\n\nI am your RemoQwen-MCP v7.0 Engineer.\n"
            f"Current Mode: {config.SELECTED_MODE}\n\nUse /help for commands."
        )

    @staticmethod
    async def _cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = "🚀 *REMOTE COMMANDER HELP*\n\n💬 *Send text* - Start video task\n📊 /status - Terminal snapshot\n🛡️ /help - This manual"
        await update.message.reply_markdown(help_text)

    @staticmethod
    async def _cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        status_card = (
            "📡 *MISSION CONTROL RADAR*\n"
            "───────────────────\n"
            f"✅ *State:* Immortal Online\n"
            f"⚙️ *Mode:* {config.SELECTED_MODE}\n"
            f"📍 *Project:* `{os.path.basename(config.PROJECT_ROOT)}`"
        )
        await update.message.reply_markdown(status_card)

    @classmethod
    async def _handle_remote_prompt(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Captures prompts and safely injects them into the project src folder."""
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        
        prompt = update.message.text
        db.log("REMOTE", f"New instruction from phone: {prompt[:30]}...")

        try:
            # 🛡️ THE FIX: Automatically ensure 'src' folder exists in the project root
            os.makedirs(os.path.dirname(config.REMOTE_TASK_FILE), exist_ok=True)
            
            with open(config.REMOTE_TASK_FILE, "w", encoding="utf-8") as f:
                f.write(f"# REMOTE TASK RECEIVED\n\n{prompt}")
            await update.message.reply_text("⚡ Task synchronized. AI brain notified.")
        except Exception as e:
            db.log("ERROR", f"Remote sync failed: {str(e)}")
            await update.message.reply_text(f"❌ Failed to sync: {e}")

    @classmethod
    async def send_notification(cls, message: str):
        """Pushes real-time terminal activity logs to the user's phone."""
        if cls._app and config.TELEGRAM_ENABLED:
            try:
                await cls._app.bot.send_message(chat_id=config.AUTHORIZED_CHAT_ID, text=message)
            except: pass

    @classmethod
    async def ask_hybrid_permission(cls, tool_name: str, target: str) -> bool:
        """
        THE HYBRID GATE: Waits for phone approval if Telegram is ON, 
        else asks on terminal.
        """
        # Fallback to local terminal if Telegram mode is off or not configured
        if not cls._app or not config.TELEGRAM_ENABLED:
            return await db.ask_permission(tool_name, target)

        db.log("GUARD", f"Pending remote authorization for '{tool_name}' on phone...", style="bold magenta")
        
        keyboard = [[
            InlineKeyboardButton("✅ APPROVE", callback_data="perm_yes"),
            InlineKeyboardButton("❌ DENY", callback_data="perm_no")
        ]]
        
        cls._permission_event.clear()
        
        msg = f"⚠️ *AUTHORIZATION REQUIRED*\n\nAI wants to: `{tool_name}`\nTarget: `{target}`"
        await cls._app.bot.send_message(
            chat_id=config.AUTHORIZED_CHAT_ID, 
            text=msg, 
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        
        # Block and wait for the signal from the phone
        await cls._permission_event.wait()
        return cls._last_permission_result

    @classmethod
    async def _handle_permission_callback(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles button interactions from Telegram and unblocks the server wait."""
        query = update.callback_query
        await query.answer()
        
        if query.data == "perm_yes":
            cls._last_permission_result = True
            await query.edit_message_text(text="✅ *PERMISSION GRANTED* (Executing...)")
            db.log("SUCCESS", "Action approved via Telegram.")
        else:
            cls._last_permission_result = False
            await query.edit_message_text(text="❌ *PERMISSION DENIED* (Aborted.)")
            db.log("ERROR", "Action rejected via Telegram.")
        
        # Signal the waiting tool to continue
        cls._permission_event.set()