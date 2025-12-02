import discord
from discord import app_commands
import os
import gspread
from dotenv import load_dotenv
from datetime import datetime

# import settings
load_dotenv()
spreadsheet_key = os.getenv('spreadsheet_key')
discord_token = os.getenv('discord_token')

guild_id = os.getenv('guild_id')
my_guild = discord.Object(id=int(guild_id))

# make client
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self):
        self.tree.copy_global_to(guild=my_guild)
        await self.tree.sync(guild=my_guild)

client = MyClient()

# set up spreadsheet
try:
    gc = gspread.service_account(filename='service_account.json')
    sh = gc.open_by_key(spreadsheet_key)
    ws = sh.get_worksheet(0)
except Exception as e:
    print(f'Error: {e}')

# ready events
@client.event
async def on_ready():
    print("ready")

# def commands

 #bkabu
@client.tree.command(name="bkabu", description="buy kabu")
@app_commands.describe(name="銘柄名", price="価格", amount="数量")
async def bkabu(interaction: discord.Interaction, name: str, price: float, amount: int):
        
        await interaction.response.defer(ephemeral=True)

        date_str = datetime.now(hours=+9).strftime('%Y/%m/%d %H:%M')
        user_name = interaction.user.name

        # write to spreadsheet
        try:
            ws.append_row([date_str, name, price,amount,"buy"])

            await interaction.followup.send(f"done", ephemeral=True)
        
        except Exception as e:
            await interaction.followup.send(f"Error: {e}",ephemeral=True)

 #skabu
@client.tree.command(name="skabu", description="sell kabu")
@app_commands.describe(name="銘柄名", price="価格", amount="数量")
async def skabu(interaction: discord.Interaction, name:str, price: float, amount: int):

    await interaction.response.defer(ephemeral=True)

    date_str = datetime.now(hours=+9).strftime('%Y/%m/%d %H:%M')
    user_name = interaction.user.name

    #write to spreadsheet
    try:
        ws.append_row([date_str,name,price,amount,"sell"])

        await interaction.followup.send(f"done",ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"Error: {e}",ephemeral=True)

# start bot
client.run(discord_token)

        
        