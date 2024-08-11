from pyrogram import Client, filters
import os

# Bot token from BotFather
API_ID = "10811400"
API_HASH = "191bf5ae7a6c39771e7b13cf4ffd1279"
BOT_TOKEN = "7412278588:AAHmk19iP3uK79OglBISjicbl70TD6i9wEc"

app = Client("python_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# In-memory file storage
files = {}

# Handle /start command
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Hi! I'm your Python bot. Here's what you can do:\n"
                        "- Use 'My Python Files' to Run your files.\n"
                        "- Use 'Convert Text to .py' to convert text snippets to Python files.\n"
                        "To install libraries, simply send me a message like 'Install numpy'.\n"
                        "To execute a Python file, upload it, and then choose 'Run' from the options.\n"
                        "Please note that you can upload and manage up to 3 '.txt' or '.py' files.\n"
                        "What would you like to do?")



# Handle file uploads
@app.on_message(filters.document)
async def handle_document(client, message):
    if message.document.file_name.endswith(('.py', '.txt')):
        file_id = message.document.file_id
        file_name = message.document.file_name
        files[file_name] = file_id
        await message.reply(f"File '{file_name}' uploaded and saved with file ID: {file_id}. Use the file name to get the file ID.")

# Fetch file ID by file name
@app.on_message(filters.command("getfileid"))
async def get_file_id(client, message):
    file_name = message.text.split(" ", 1)[1]
    file_id = files.get(file_name)
    if file_id:
        await message.reply(f"The file ID for '{file_name}' is: {file_id}")
    else:
        await message.reply("Invalid file name or file not found.")



# Convert text to .py file
@app.on_message(filters.text & filters.command("convert"))
async def convert_text(client, message):
    text = message.text
    file_name = "converted_file.py"
    with open(file_name, 'w') as file:
        file.write(text)
    await message.reply(f"Text converted to '{file_name}'. Use 'Run' to execute it.")

# Handle custom commands
@app.on_message(filters.command("install"))
async def install_package(client, message):
    package_name = message.text.split(" ", 1)[1]
    os.system(f"pip install {package_name}")
    await message.reply(f"Package '{package_name}' installed.")

@app.on_message(filters.command("run"))
async def run_file(client, message):
    file_id = message.text.split(" ", 1)[1]
    file_name = files.get(file_id)
    if file_name:
        output = os.popen(f"python {file_name}").read()
        await message.reply(f"Output:\n{output}")
    else:
        await message.reply("Invalid file ID.")

@app.on_message(filters.command("delete"))
async def delete_file(client, message):
    file_id = message.text.split(" ", 1)[1]
    file_name = files.pop(file_id, None)
    if file_name:
        os.remove(file_name)
        await message.reply(f"File '{file_name}' deleted.")
    else:
        await message.reply("Invalid file ID.")

@app.on_message(filters.command("myfiles"))
async def list_files(client, message):
    if files:
        file_list = "\n".join([f"{file_id}: {name}" for file_id, name in files.items()])
        await message.reply(f"My Python Files:\n{file_list}")
    else:
        await message.reply("No files uploaded.")

# Run the bot
app.run()
