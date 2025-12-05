import discord
from discord import app_commands
from discord.ext import tasks
import os
import gspread
from dotenv import load_dotenv
from datetime import datetime
import yfinance as yf

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

        self.check_price_loop.start()
        print("loop started")
    
    @tasks.loop(minutes=60)
    async def check_price_loop(self):
        if not self.is_ready():
            return
        try:
            alert_ws = sh.get_worksheet(1)
            alerts = alert_ws.get_all_values()

            if len(alerts) <= 1:
                return
            
            rows_to_delete = []

            for i, row in enumerate(alerts[1:], start=2):
                if len(row) < 4:
                    continue

                user_name,code,target_price, channel_id = row

                ticker = code
                if code.isdigit(): ticker = f"{code}.T"

                try:
                    stock = yf.Ticker(ticker)
                    current_price = stock.fast_info['last_price']
                    target = float(target_price)

                    if current_price >= target:

                        channel = self.get_channel(int(channel_id))
                        
                        if channel:
                            await channel.send(f"{code} {target}")
                            print(f"{code}{target}")
                        
                        rows_to_delete.append(i)

                except Exception as e:
                    print(f"Error {code}:{e}")
            
            for row_num in sorted(rows_to_delete, reverse=True):
                alert_ws.delete_rows(row_num)
        
        except Exception as e:
            print(f"Error{e}")
        
                    
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

        date_str = datetime.now().strftime('%Y/%m/%d %H:%M')
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

    date_str = datetime.now().strftime('%Y/%m/%d %H:%M')
    user_name = interaction.user.name

    #write to spreadsheet
    try:
        ws.append_row([date_str,name,price,amount,"sell"])

        await interaction.followup.send(f"done",ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"Error: {e}",ephemeral=True)

#/set_alert
@client.tree.command(name="set_alert", description="通知設定")
@app_commands.describe(code="銘柄", target="価格")
async def set_alert(interaction: discord.Interaction, code:str, target:float):
    await interaction.response.defer(ephemeral=True)

    try:
        alert_ws = sh.get_worksheet(1)

        alert_ws.append_row([interaction.user.name, code, target, str(interaction.channel_id)])

        await interaction.followup.send("done")
    except Exception as e:
        await interaction.followup.send(f"Error{e}")

# start bot
client.run(discord_token)

        
        