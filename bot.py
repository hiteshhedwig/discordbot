import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

# Your Google Doc ID
DOC_ID = 'your_google_doc_id_here'

@bot.event
async def on_ready():
    print(f'Bot is ready as {bot.user}')

@bot.command()
async def get_info(ctx, *, query):
    doc_content = get_doc_content(DOC_ID)
    response = generate_response(doc_content, query)
    await ctx.send(response)

def generate_response(doc_content, query):
    # Implement a simple search or processing of the doc_content
    # Here, we just check if the query is in the content and return a response
    if query.lower() in doc_content.lower():
        return f"I found something related to '{query}':\n\n{doc_content[:200]}..."  # Returning the first 200 characters as an example
    else:
        return "I couldn't find anything related to your query."

bot.run('your_discord_bot_token_here')
