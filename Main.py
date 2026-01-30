import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask, request
import threading
import requests
from urllib.parse import quote
import os

# ================== CONFIG ==================
TOKEN = os.getenv("TOKEN")  # Railway
CLIENT_ID = "1466754048723124413"
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

GUILD_ID = 1463692878684356761
CARGO_MEMBRO_ID = 1463719459029123136
OWNER_ID = 1463692878684356761

REDIRECT_URI = os.getenv("REDIRECT_URI")

ENCODED_REDIRECT = quote(REDIRECT_URI, safe="")

OAUTH_URL = (
    "https://discord.com/oauth2/authorize"
    f"?client_id={CLIENT_ID}"
    "&response_type=code"
    "&scope=identify"
    f"&redirect_uri={ENCODED_REDIRECT}"
)

# ================== BOT ==================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ================== FLASK ==================
app = Flask(__name__)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "❌ Código inválido"

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify"
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    r = requests.post(
        "https://discord.com/api/oauth2/token",
        data=data,
        headers=headers
    )

    if r.status_code != 200:
        return "❌ Erro ao autenticar"

    return "✅ Verificação concluída! Pode voltar ao Discord."

def run_flask():
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# ================== VIEW ==================
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            discord.ui.Button(
                label="✅ Verificar",
                style=discord.ButtonStyle.link,
                url=OAUTH_URL
            )
        )

# ================== SLASH COMMAND ==================
@tree.command(
    name="void",
    description="Envia a verificação",
    guild=discord.Object(id=GUILD_ID)
)
async def void(interaction: discord.Interaction):

    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "❌ Você não pode usar este comando.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="🔐 Verificação",
        description="Clique no botão abaixo para verificar sua conta.",
        color=0x5865F2
    )

    await interaction.response.send_message(
        embed=embed,
        view=VerifyView()
    )

# ================== READY ==================
@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"🤖 Bot online como {bot.user}")

# ================== START ==================
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(TOKEN)
  
