import os
from pyrogram import Client, filters
from config import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Dictionary to store file_name: file_id pairs
files = {}

# Start command
@Client.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Hi! I'm your Python bot. Here's what you can do:\n"
                        "- Upload a Python (.py) or text (.txt) file to store it.\n"
                        "- Use inline buttons to run or delete the file.\n"
                        "- Send a `requirements.txt` file to install dependencies automatically.\n"
                        "- Use `/sudo <command>` to manually run system commands.\n"
                        "What would you like to do?")

# Handle file uploads
@Client.on_message(filters.document)
async def handle_document(client, message):
    if message.document.file_name.endswith(('.py', '.txt', 'requirements.txt')):
        file_id = message.document.file_id
        file_name = message.document.file_name
        files[file_name] = file_id
        file_path = os.path.join(os.getcwd(), file_name)
        await message.download(file_name=file_path)
        
        # Create inline buttons
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Run", callback_data=f"run_{file_name}")],
            [InlineKeyboardButton("Delete", callback_data=f"delete_{file_name}")]
        ])
        
        await message.reply(f"File '{file_name}' received and saved. You now have {len(files)} file(s).", reply_markup=keyboard)
        
        # Automatically install requirements if it's a requirements.txt file
        if file_name.endswith('requirements.txt'):
            await install_requirements(file_path)
            await message.reply(f"Dependencies installed from '{file_name}'. Now, you can run your Python script.")
    else:
        await message.reply("Please upload a valid '.py', '.txt', or 'requirements.txt' file.")

# Install requirements from requirements.txt
async def install_requirements(file_path):
    os.system(f"pip install -r {file_path}")

# Handle button callbacks
@Client.on_callback_query()
async def handle_button(client, callback_query):
    data = callback_query.data
    file_action, file_name = data.split("_", 1)
    file_path = os.path.join(os.getcwd(), file_name)
    
    if file_action == "run":
        if os.path.exists(file_path):
            output = os.popen(f"python {file_path}").read()
            await callback_query.message.reply(f"Output:\n{output}")
        else:
            await callback_query.message.reply("The file was not found.")
    
    elif file_action == "delete":
        if os.path.exists(file_path):
            os.remove(file_path)
            files.pop(file_name, None)
            await callback_query.message.reply(f"File '{file_name}' deleted.")
            await callback_query.message.delete()  # Remove the inline buttons message
        else:
            await callback_query.message.reply("The file was not found.")

# List files
@Client.on_message(filters.command("myfiles"))
async def list_files(client, message):
    if files:
        file_list = "\n".join([f"{name}: {files[name]}" for name in files])
        await message.reply(f"My Python Files:\n{file_list}")
    else:
        await message.reply("No files uploaded.")

# Manually run system commands
@Client.on_message(filters.command("sudo"))
async def sudo_command(client, message):
    if message.from_user.id == ADMIN:  # Replace YOUR_ADMIN_USER_ID with your Telegram user ID
        command = " ".join(message.text.split()[1:])  # Get the command from the message
        if command:
            os.system(command)
            await message.reply(f"Command executed: `{command}`")
        else:
            await message.reply("No command provided.")
    else:
        await message.reply("You do not have permission to use this command.")

# Ensure to replace YOUR_ADMIN_USER_ID with the ID of the user who should have access to the sudo command.
