import os
import asyncio
import logging
import uuid
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import config
from src.ui.dashboard import db

logger = logging.getLogger("remotion_bridge")

class RemoteCommander:
    """
    v8.0 ASSET COMMANDER (Enhanced).
    Handles remote orchestration, smart asset management, atomic task injection,
    and hybrid permission system with per-request futures and timeout.
    """
    _app: Application = None
    _pending_perm_requests = {}  # {request_id: asyncio.Future}

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
            cls._app.add_handler(CommandHandler("show_public", cls._cmd_show_public))
            cls._app.add_handler(CommandHandler("show_out", cls._cmd_show_out))
            cls._app.add_handler(CommandHandler("render", cls._cmd_render))
            
            cls._app.add_handler(CallbackQueryHandler(cls._handle_callback))  # unified callback handler

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
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        await update.message.reply_text(f"👋 Greetings HIRUNA!\nYour PC is linked. Use /help for remote features.")

    @staticmethod
    async def _cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_msg = (
            "🚀 *REMOTE COMMANDER v8.0*\n\n"
            "💬 *Send Text* - Starts a new mission\n"
            "🛑 *Send 'STOP'* - Terminates the AI loop\n"
            "🖼️ *Image + Caption* - Saves asset with custom name\n"
            "📊 /assets - Choose folder (public/out) and list files\n"
            "📷 /show_public <filename> - View asset from public folder\n"
            "🎬 /show_out <filename> - View rendered video from out folder\n"
            "🎥 /render [composition] - Trigger video rendering (optional composition ID)\n"
            "🗑️ /delete [name] - Remove asset from public folder\n"
            "📡 /status - Check system radar"
        )
        await update.message.reply_markdown(help_msg)

    @staticmethod
    async def _cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        """Send folder selection inline keyboard."""
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        keyboard = [
            [InlineKeyboardButton("📁 PUBLIC FOLDER", callback_data="assets_public"),
             InlineKeyboardButton("📁 OUT FOLDER", callback_data="assets_out")]
        ]
        await update.message.reply_text(
            "📂 *SELECT FOLDER*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    @staticmethod
    async def _cmd_show_public(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a file from public folder."""
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        if not context.args:
            await update.message.reply_text("❓ Usage: /show_public logo.png")
            return
        filename = ' '.join(context.args)  # allow spaces in filename
        file_path = os.path.join(config.PUBLIC_DIR, filename)
        if not os.path.exists(file_path):
            await update.message.reply_text(f"🚫 `{filename}` not found in public folder.")
            return
        try:
            # Send as photo if it's an image, otherwise as document
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                with open(file_path, 'rb') as f:
                    await update.message.reply_photo(f, caption=f"📷 *{filename}*")
            else:
                with open(file_path, 'rb') as f:
                    await update.message.reply_document(f, caption=f"📄 *{filename}*")
        except Exception as e:
            await update.message.reply_text(f"❌ Error sending file: {e}")

    @staticmethod
    async def _cmd_show_out(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a rendered video from out folder."""
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        if not context.args:
            await update.message.reply_text("❓ Usage: /show_out video.mp4")
            return
        filename = ' '.join(context.args)
        file_path = os.path.join(config.OUT_DIR, filename)
        if not os.path.exists(file_path):
            await update.message.reply_text(f"🚫 `{filename}` not found in out folder.")
            return
        if not filename.lower().endswith('.mp4'):
            await update.message.reply_text(f"⚠️ Only MP4 videos are supported for preview.")
            return
        try:
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            if file_size > 50:
                await update.message.reply_text(f"⚠️ Video is {file_size:.1f} MB. Telegram limit is 50 MB. Sending as document.")
                with open(file_path, 'rb') as f:
                    await update.message.reply_document(f, caption=f"🎬 *{filename}* ({file_size:.1f} MB)")
            else:
                with open(file_path, 'rb') as f:
                    await update.message.reply_video(f, caption=f"🎬 *{filename}*")
        except Exception as e:
            await update.message.reply_text(f"❌ Error sending video: {e}")

    @staticmethod
    async def _cmd_render(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Trigger video rendering by writing to remote_task.md."""
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        composition = context.args[0] if context.args else "VideoComposition"
        task_content = f"RENDER_VIDEO:{composition}"
        try:
            os.makedirs(os.path.dirname(config.REMOTE_TASK_FILE), exist_ok=True)
            with open(config.REMOTE_TASK_FILE, "w", encoding="utf-8") as f:
                f.write(task_content)
            db.log("REMOTE", f"Render requested for composition: {composition}")
            await update.message.reply_text(
                f"🎬 *RENDER TRIGGERED*\n\nComposition: `{composition}`\n\nAI will start rendering soon. Use `/status` to check progress.",
                parse_mode="Markdown"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ *SYNC ERROR:* {e}")

    @staticmethod
    async def _cmd_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Prepares a deletion request with confirmation buttons."""
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        if not context.args:
            await update.message.reply_text("❓ Usage: /delete logo.png")
            return
        filename = ' '.join(context.args)
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
            try: 
                await cls._app.bot.send_message(chat_id=config.AUTHORIZED_CHAT_ID, text=message)
            except Exception:
                pass

    @classmethod
    async def ask_hybrid_permission(cls, tool_name: str, target: str) -> bool:
        """
        Remote/Local Permission Gate with per-request timeout.
        """
        if not cls._app or not config.TELEGRAM_ENABLED:
            return await db.ask_permission(tool_name, target)

        request_id = str(uuid.uuid4())
        future = asyncio.Future()
        cls._pending_perm_requests[request_id] = future

        db.log("GUARD", f"Awaiting remote authorization for '{tool_name}'...", style="bold magenta")
        keyboard = [[InlineKeyboardButton("✅ APPROVE", callback_data=f"perm_yes:{request_id}"),
                     InlineKeyboardButton("❌ DENY", callback_data=f"perm_no:{request_id}")]]
        
        msg = f"⚠️ *AUTHORIZATION REQUIRED*\n\nAI wants to: `{tool_name}`\nTarget: `{target}`"
        try:
            await cls._app.bot.send_message(
                chat_id=config.AUTHORIZED_CHAT_ID,
                text=msg,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        except Exception as e:
            db.log("ERROR", f"Failed to send permission request: {e}")
            del cls._pending_perm_requests[request_id]
            return False

        try:
            # Wait for response with timeout
            result = await asyncio.wait_for(future, timeout=config.PERMISSION_TIMEOUT)
            return result
        except asyncio.TimeoutError:
            db.log("ERROR", f"Permission request for {tool_name} timed out after {config.PERMISSION_TIMEOUT}s")
            return False
        finally:
            # Clean up
            cls._pending_perm_requests.pop(request_id, None)

    @classmethod
    async def _handle_callback(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Unified callback handler for all inline keyboards."""
        query = update.callback_query
        await query.answer()
        data = query.data

        # 1. Asset folder selection (assets_public / assets_out)
        if data in ("assets_public", "assets_out"):
            folder_path = config.PUBLIC_DIR if data == "assets_public" else config.OUT_DIR
            folder_name = "public" if data == "assets_public" else "out"
            try:
                files = os.listdir(folder_path)
                if not files:
                    await query.edit_message_text(f"📂 *{folder_name.upper()} FOLDER* is empty.", parse_mode="Markdown")
                    return
                list_msg = f"📂 *{folder_name.upper()} FOLDER*\n───────────────────\n"
                for f in files:
                    if data == "assets_public":
                        emoji = "🖼️" if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg')) else "📄"
                    else:
                        emoji = "🎬" if f.lower().endswith('.mp4') else "📄"
                    size = os.path.getsize(os.path.join(folder_path, f)) / 1024
                    list_msg += f"{emoji} `{f}` ({size:.1f} KB)\n"
                await query.edit_message_text(list_msg, parse_mode="Markdown")
            except Exception as e:
                await query.edit_message_text(f"❌ Error: {e}")
            return

        # 2. Deletion confirmation
        if data.startswith("del_"):
            if data.startswith("del_yes:"):
                filename = data.split(":", 1)[1]
                try:
                    os.remove(os.path.join(config.PUBLIC_DIR, filename))
                    await query.edit_message_text(text=f"🗑️ *DELETED:* `{filename}` successfully removed.", parse_mode="Markdown")
                    db.log("CLEAN", f"Remote cleanup: {filename}")
                except Exception as e:
                    await query.edit_message_text(text=f"❌ *ERROR:* {e}", parse_mode="Markdown")
            else:
                await query.edit_message_text(text="❌ Deletion cancelled.", parse_mode="Markdown")
            return

        # 3. Permission approval
        if data.startswith("perm_yes:") or data.startswith("perm_no:"):
            try:
                _, request_id = data.split(":", 1)
                future = cls._pending_perm_requests.get(request_id)
                if future and not future.done():
                    if data.startswith("perm_yes:"):
                        future.set_result(True)
                        await query.edit_message_text(text="✅ *PERMISSION GRANTED* (Executing on PC...)", parse_mode="Markdown")
                        db.log("SUCCESS", "Action approved remotely.")
                    else:
                        future.set_result(False)
                        await query.edit_message_text(text="❌ *PERMISSION DENIED* (Aborted locally.)", parse_mode="Markdown")
                        db.log("ERROR", "Action rejected remotely.")
                else:
                    await query.edit_message_text(text="⚠️ This request has already expired or been processed.", parse_mode="Markdown")
            except Exception as e:
                await query.edit_message_text(text=f"❌ Error processing permission: {e}", parse_mode="Markdown")
            return