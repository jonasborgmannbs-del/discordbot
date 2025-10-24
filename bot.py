also so : import discord
from discord.ext import commands
from discord import ui, ButtonStyle
import asyncio
import aiohttp
import datetime
import json
import random
import time
from typing import Optional

# Bot-Einstellungen
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='?', intents=intents, help_command=None)

# ========== KONFIGURATION ==========
# Channel IDs
PRODUCTS_CHANNEL = 1429188299980935329
VERIFY_CHANNEL = 1429188271728099488
ARE_WE_LEGIT_CHANNEL = 1429188331475964086
VOUCH_CHANNEL = 1429188339302400000
TICKET_CHANNEL = 1429188345216499813
WELCOME_CHANNEL = 1429188264941850866
TOS_REDIRECT_CHANNEL = 1429616201004351549
TOS_CHANNEL = 1429188292812734494
LOG_CHANNEL = 1429188345216499813

# Rollen IDs - AKTUALISIERT MIT NEUER ROLLEN-ID
VERIFIED_ROLE = 1429972270549307482  # NEUE ROLLEN-ID
ADMIN_ROLE = 1429493502357536819  # NUR DIESE ROLLE KANN MOD-BEFEHLE NUTZEN
MOD_ROLE = 1429188189448437850
MEMBER_ROLE = 1429972270549307482  # NEUE ROLLEN-ID

# Ticket Kategorien
CLAIMING_CATEGORY = 1429189773171626178
SUPPORT_CATEGORY = 1429189672998928468
PURCHASE_CATEGORY = 1429189583228108810

TICKET_CATEGORIES = [CLAIMING_CATEGORY, SUPPORT_CATEGORY, PURCHASE_CATEGORY]

# Crypto Wallets
LTC_WALLET = "LcRYGM4pskZkSZiSCwKyYnEvZWGXK58Fx8"
BTC_WALLET = "bc1ql3haw93l54uetxdvd8epgz9tzcn52kwn0xh99c"
ETH_WALLET = "0xE51a27D9ED2dA2c0870327B594399A8554155895"

# Special User
SPECIAL_USER_ID = 1278417250445033555

# Blacklist
blacklisted_words = []

# Giveaways
active_giveaways = {}

# ========== BOT EVENTS ==========
@bot.event
async def on_ready():
    print(f'🤖 {bot.user} ist online!')
    print(f'📊 Verbunden mit {len(bot.guilds)} Servern')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="STAR JM Services"))

@bot.event
async def on_member_join(member):
    """Automatische Willkommensnachricht wenn jemand joined"""
    channel = bot.get_channel(WELCOME_CHANNEL)
    if channel:
        embed = discord.Embed(
            description=f"**WELCOME TO STAR JM**\n\nSup {member.mention}!\n\nWelcome to Star JM - your destination for the best prices on services and more!",
            color=0x00008B
        )
        
        embed.add_field(
            name="🎯 What we offer:",
            value=(
                f"• Browse our products in <#{PRODUCTS_CHANNEL}>\n"
                f"• Verify in <#{VERIFY_CHANNEL}> to access chat\n"
                f"• Participate in giveaways and events\n"
                f"• Get premium services at unbeatable prices"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎉 We're excited to have you here!",
            value="",
            inline=False
        )
        
        embed.set_footer(text="Star JM • Quality Services & Best Prices")
        await channel.send(embed=embed)
        
        # Gib dem neuen Member eine Basis-Rolle mit Fehlerbehandlung
        role = member.guild.get_role(MEMBER_ROLE)
        if role:
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                print("❌ Bot hat keine Berechtigung um Rollen zu vergeben!")

@bot.event
async def on_command(ctx):
    # Lösche jeden Befehl sofort nach Ausführung
    try:
        await ctx.message.delete()
    except:
        pass

@bot.event
async def on_message(message):
    # Blacklist Filter
    if not message.author.bot:
        for word in blacklisted_words:
            if word.lower() in message.content.lower():
                await message.delete()
                warning = await message.channel.send(f"{message.author.mention} you are not allowed to say that!", delete_after=5)
                return
        
    await bot.process_commands(message)

# ========== SPECIAL USER CHECK ==========
def is_special_user():
    def predicate(ctx):
        return ctx.author.id == SPECIAL_USER_ID
    return commands.check(predicate)

# ========== WILLKOMMENS-SYSTEM ==========
@bot.command()
@commands.has_role(ADMIN_ROLE)  # NUR ADMIN
async def welcome(ctx):
    """Sendet eine Willkommensnachricht (für manuelle Nutzung)"""
    embed = discord.Embed(
        description=f"**WELCOME TO STAR JM**\n\nSup {ctx.author.mention}!\n\nWelcome to Star JM - your destination for the best prices on services and more!",
        color=0x00008B
    )
    
    embed.add_field(
        name="🎯 What we offer:",
        value=(
            f"• Browse our products in <#{PRODUCTS_CHANNEL}>\n"
            f"• Verify in <#{VERIFY_CHANNEL}> to access chat\n"
            f"• Participate in giveaways and events\n"
            f"• Get premium services at unbeatable prices"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🎉 We're excited to have you here!",
        value="",
        inline=False
    )
    
    embed.set_footer(text="Star JM • Quality Services & Best Prices")
    await ctx.send(embed=embed)

# ========== VERIFY-SYSTEM MIT BUTTON ==========
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Verify Account", style=ButtonStyle.green, emoji="✅", custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(VERIFIED_ROLE)
        if role and role not in interaction.user.roles:
            try:
                await interaction.user.add_roles(role)
                
                embed = discord.Embed(
                    title="✅ Verification Successful",
                    description="Your account has been verified! You now have access to all channels.",
                    color=0x00ff00
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("❌ Bot has no permission to assign roles! Please contact admin.", ephemeral=True)
        else:
            await interaction.response.send_message("You are already verified!", ephemeral=True)

@bot.command()
async def verify(ctx):
    """VERIFIZIERUNG - FÜR ALLE VERFÜGBAR"""
    embed = discord.Embed(
        title="🔐 ACCOUNT VERIFICATION",
        description="Click the button below to verify your account!\nBy verifying you get access to:",
        color=0x00008B
    )
    
    embed.add_field(
        name="🎁 Benefits:",
        value=(
            "• Community chat channels\n"
            "• Giveaways and special events\n" 
            "• Product announcements\n"
            "• Exclusive offers\n\n"
            "**Verification is instant and free!**"
        ),
        inline=False
    )
    
    embed.set_footer(text="Star JM Secure & Trusted Community")
    
    view = VerifyView()
    await ctx.send(embed=embed, view=view)

# ========== VOUCH-SYSTEM MIT FEHLERBEHANDLUNG ==========
@bot.command()
@commands.has_role(ADMIN_ROLE)  # NUR ADMIN
async def vouch(ctx, *, service=None):
    """Vouch command mit Service-Argument"""
    if service is None:
        await ctx.send("❌ Please specify a service. Example: `?vouch spotify`", delete_after=5)
        return
    
    embed = discord.Embed(
        title="📝 VOUCH INSTRUCTIONS",
        color=0x00008B
    )
    
    embed.add_field(
        name="Please complete these steps to vouch:",
        value=(
            f"1. Leave a vouch in <#{ARE_WE_LEGIT_CHANNEL}>\n"
            f"2. React in <#{ARE_WE_LEGIT_CHANNEL}>"
        ),
        inline=False
    )
    
    vouch_message = f"+vouch @jbtb0003 for {service}"
    
    embed.add_field(
        name="Copy and paste this message in the vouch channel:",
        value=f"```{vouch_message}```",
        inline=False
    )
    
    await ctx.send(embed=embed)

# ========== GIVEAWAY SYSTEM ==========
class GiveawayView(discord.ui.View):
    def __init__(self, end_timestamp, prize):
        super().__init__(timeout=None)
        self.end_timestamp = end_timestamp
        self.prize = prize
        self.participants = set()
    
    @discord.ui.button(label="Enter Giveaway", style=ButtonStyle.green, emoji="🎉", custom_id="enter_giveaway")
    async def enter_giveaway(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.participants:
            await interaction.response.send_message("❌ You have already entered this giveaway!", ephemeral=True)
        else:
            self.participants.add(interaction.user.id)
            await interaction.response.send_message("✅ You have entered the giveaway!", ephemeral=True)

@bot.command()
@commands.has_role(ADMIN_ROLE)
async def giveaway(ctx, duration: str, *, prize):
    """
    Startet ein Giveaway
    Verwendung: ?giveaway 1h Discord Nitro
    """
    # Parse duration
    time_units = {
        's': 1, 'm': 60, 'h': 3600, 'd': 86400,
        'sec': 1, 'min': 60, 'hour': 3600, 'day': 86400
    }
    
    duration_lower = duration.lower()
    unit = duration_lower[-1]
    if unit not in time_units:
        unit = duration_lower[-3:] if len(duration_lower) >= 3 else unit
    
    try:
        number = int(duration_lower.rstrip('smhdsecminhourday'))
        total_seconds = number * time_units.get(unit, 60)
    except:
        await ctx.send("❌ Invalid duration format. Use: 1h, 30m, 2d etc.")
        return
    
    # KORREKTE Zeitberechnung mit time()
    end_timestamp = int(time.time() + total_seconds)
    
    # Create embed
    embed = discord.Embed(
        title="🎉 GIVEAWAY 🎉",
        description=f"**Prize:** {prize}\n\nClick the button below to enter!",
        color=0xffd700
    )
    
    # Korrekte Zeit-Anzeige
    embed.add_field(
        name="Time Remaining:",
        value=f"Ends: <t:{end_timestamp}:R>",
        inline=False
    )
    
    embed.set_footer(text="Good luck!")
    
    # Create view and send message
    view = GiveawayView(end_timestamp, prize)
    message = await ctx.send(embed=embed, view=view)
    
    # Store giveaway info
    active_giveaways[message.id] = {
        'end_timestamp': end_timestamp,
        'prize': prize,
        'participants': view.participants,
        'channel_id': ctx.channel.id,
        'message_id': message.id
    }
    
    # Schedule ending
    bot.loop.create_task(schedule_giveaway_end(message.id, total_seconds))

async def schedule_giveaway_end(message_id, delay):
    """Schedule giveaway end with proper error handling"""
    await asyncio.sleep(delay)
    await end_giveaway(message_id)

async def end_giveaway(message_id):
    """Beendet das Giveaway und wählt einen Gewinner"""
    if message_id not in active_giveaways:
        return
    
    giveaway = active_giveaways[message_id]
    channel = bot.get_channel(giveaway['channel_id'])
    
    if not channel:
        return
    
    try:
        message = await channel.fetch_message(message_id)
        participants = list(giveaway['participants'])
        
        if participants:
            winner_id = random.choice(participants)
            winner = await bot.fetch_user(winner_id)
            
            # Update the giveaway message
            embed = message.embeds[0]
            embed.color = 0x00ff00
            embed.clear_fields()
            embed.add_field(
                name="Prize:",
                value=giveaway['prize'],
                inline=False
            )
            embed.add_field(
                name="🎊 Winner:",
                value=f"Congratulations {winner.mention}! You won **{giveaway['prize']}**!",
                inline=False
            )
            embed.set_footer(text="Giveaway ended")
            
            await message.edit(embed=embed, view=None)
            await channel.send(f"🎉 Congratulations {winner.mention}! You won **{giveaway['prize']}**!")
        else:
            embed = message.embeds[0]
            embed.color = 0xff0000
            embed.clear_fields()
            embed.add_field(
                name="Prize:",
                value=giveaway['prize'],
                inline=False
            )
            embed.add_field(
                name="❌ Giveaway Ended",
                value="No one entered the giveaway!",
                inline=False
            )
            embed.set_footer(text="Giveaway ended - no participants")
            await message.edit(embed=embed, view=None)
        
        # Remove from active giveaways
        del active_giveaways[message_id]
        
    except Exception as e:
        print(f"Error ending giveaway: {e}")

# ========== CRYPTO & PAYPAL PAYMENT SYSTEM ==========
class CryptoPriceAPI:
    @staticmethod
    async def get_crypto_price(crypto):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=eur') as response:
                    data = await response.json()
                    
                    prices = {
                        'bitcoin': data.get('bitcoin', {}).get('eur', 45000),
                        'ethereum': data.get('ethereum', {}).get('eur', 3000),
                        'litecoin': data.get('litecoin', {}).get('eur', 81.40)
                    }
                    return prices.get(crypto, 0)
        except:
            fallback_prices = {
                'bitcoin': 45000,
                'ethereum': 3000,
                'litecoin': 81.40
            }
            return fallback_prices.get(crypto, 0)

@bot.command()
@commands.has_role(ADMIN_ROLE)  # NUR ADMIN
async def btc(ctx, amount: float):
    price = await CryptoPriceAPI.get_crypto_price('bitcoin')
    btc_amount = amount / price
    
    embed = discord.Embed(
        title="💰 Bitcoin Payment",
        color=0x00008B
    )
    
    embed.add_field(
        name="💵 Amount:",
        value=f"{amount:.2f} €",
        inline=False
    )
    
    embed.add_field(
        name="📊 Current BTC Price:",
        value=f"{price:.2f} €",
        inline=True
    )
    
    embed.add_field(
        name="🔢 Crypto Amount:",
        value=f"```{btc_amount:.6f} BTC```",
        inline=False
    )
    
    embed.add_field(
        name=f"📤 Send exactly {btc_amount:.6f} BTC to:",
        value=f"```{BTC_WALLET}```",
        inline=False
    )
    
    embed.set_footer(text="✅ Make sure to send the exact amount!")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_role(ADMIN_ROLE)  # NUR ADMIN
async def eth(ctx, amount: float):
    price = await CryptoPriceAPI.get_crypto_price('ethereum')
    eth_amount = amount / price
    
    embed = discord.Embed(
        title="💰 Ethereum Payment",
        color=0x00008B
    )
    
    embed.add_field(
        name="💵 Amount:",
        value=f"{amount:.2f} €",
        inline=False
    )
    
    embed.add_field(
        name="📊 Current ETH Price:",
        value=f"{price:.2f} €", 
        inline=True
    )
    
    embed.add_field(
        name="🔢 Crypto Amount:",
        value=f"```{eth_amount:.6f} ETH```",
        inline=False
    )
    
    embed.add_field(
        name=f"📤 Send exactly {eth_amount:.6f} ETH to:",
        value=f"```{ETH_WALLET}```",
        inline=False
    )
    
    embed.set_footer(text="✅ Make sure to send the exact amount!")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_role(ADMIN_ROLE)  # NUR ADMIN
async def ltc(ctx, amount: float):
    price = await CryptoPriceAPI.get_crypto_price('litecoin')
    ltc_amount = amount / price
    
    embed = discord.Embed(
        title="💰 Litecoin Payment",
        color=0x00008B
    )
    
    embed.add_field(
        name="💵 Amount:",
        value=f"{amount:.2f} €",
        inline=False
    )
    
    embed.add_field(
        name="📊 Current LTC Price:",
        value=f"{price:.2f} €",
        inline=True
    )
    
    embed.add_field(
        name="🔢 Crypto Amount:",
        value=f"```{ltc_amount:.6f} LTC```",
        inline=False
    )
    
    embed.add_field(
        name=f"📤 Send exactly {ltc_amount:.6f} LTC to:",
        value=f"```{LTC_WALLET}```",
        inline=False
    )
    
    embed.set_footer(text="✅ Make sure to send the exact amount!")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_role(ADMIN_ROLE)  # NUR ADMIN
async def paypal(ctx, amount: float):
    """PayPal Payment Command"""
    embed = discord.Embed(
        title="💰 PayPal Payment",
        color=0x003087  # PayPal Blau
    )
    
    embed.add_field(
        name="💵 Amount:",
        value=f"{amount:.2f} €",
        inline=False
    )
    
    embed.add_field(
        name="🔗 PayPal.Me Link:",
        value=f"```https://paypal.me/Tpnisyrup```",
        inline=False
    )
    
    embed.add_field(
        name="📋 Important Instructions:",
        value=(
            "• Send as **Friends & Family**\n"
            "• Do NOT mention anything in the notes\n"
            "• Send the exact amount\n"
            "• After payment, provide screenshot in ticket"
        ),
        inline=False
    )
    
    embed.set_footer(text="✅ Make sure to send as Friends & Family!")
    await ctx.send(embed=embed)

# ========== TICKET-SYSTEM ==========
class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Support", style=ButtonStyle.blurple, emoji="🛠️", custom_id="support_ticket")
    async def support_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "support")
    
    @discord.ui.button(label="Purchase", style=ButtonStyle.green, emoji="💰", custom_id="purchase_ticket")
    async def purchase_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "purchase")
    
    @discord.ui.button(label="Claim", style=ButtonStyle.red, emoji="🎁", custom_id="claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "claim")
    
    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        # Überprüfe ob User bereits ein offenes Ticket hat
        for channel in interaction.guild.channels:
            if channel.category_id in TICKET_CATEGORIES and str(interaction.user.name) in channel.name:
                embed = discord.Embed(
                    title="❌ Ticket Already Exists",
                    description="You already have an open ticket!",
                    color=0xff0000
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Wähle die richtige Kategorie
        category_id = {
            "support": SUPPORT_CATEGORY,
            "purchase": PURCHASE_CATEGORY, 
            "claim": CLAIMING_CATEGORY
        }.get(ticket_type, SUPPORT_CATEGORY)
        
        category = bot.get_channel(category_id)
        
        # Zähle existierende Tickets für Nummer
        ticket_count = len([ch for ch in category.channels if ch.category_id == category_id])
        
        # Erstelle Ticket Channel
        ticket_channel = await category.create_text_channel(
            name=f"{ticket_type}-{ticket_count + 1}-{interaction.user.name}",
            topic=f"Ticket von {interaction.user.display_name} | Type: {ticket_type} | ID: {interaction.user.id}"
        )
        
        # Setze Berechtigungen
        await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await ticket_channel.set_permissions(interaction.guild.default_role, read_messages=False)
        
        # Sende Bestätigung
        embed = discord.Embed(
            title="🎫 Ticket Created",
            description=f"Your {ticket_type} ticket has been created: {ticket_channel.mention}",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Sende Ticket-Willkommensnachricht basierend auf Typ
        await self.send_ticket_welcome(ticket_channel, interaction.user, ticket_type, ticket_count + 1)

    async def send_ticket_welcome(self, channel, user, ticket_type, ticket_number):
        if ticket_type == "purchase":
            embed = discord.Embed(
                title=f"🛒 Purchase Ticket #{ticket_number}",
                description=f"Hello **{user.display_name}**!\nWhat would you like to purchase? Please specify:",
                color=0x00008B
            )
            
            embed.add_field(
                name="📋 Required Information:",
                value=(
                    "• **Product/Service:** \n"
                    "• **Payment Method:** (LTC/BTC/ETH/PayPal)\n" 
                    "• **Amount:** (in €)\n\n"
                    "We will calculate the exact amount for your chosen payment method."
                ),
                inline=False
            )
            
        elif ticket_type == "support":
            embed = discord.Embed(
                title=f"🛠️ Support Ticket #{ticket_number}",
                description=f"Hello **{user.display_name}**!\nPlease describe your issue in detail:",
                color=0x00008B
            )
            embed.add_field(
                name="⚠️ Important:",
                value="**Do not ping us or you will receive a timeout or ban.**",
                inline=False
            )
            
        elif ticket_type == "claim":
            embed = discord.Embed(
                title=f"🎁 Claim Ticket #{ticket_number}",
                description=f"Hello **{user.display_name}**!",
                color=0x00008B
            )
            embed.add_field(
                name="📄 Please provide:",
                value="**Please send your invoice id, proof and proof payment so you can get your products as soon as possible.**",
                inline=False
            )
        
        embed.add_field(
            name="📊 Ticket Info:",
            value=(
                f"**Created by:** {user.display_name}\n"
                f"**Type:** {ticket_type}\n"
                f"**Status:** ✅ Waiting"
            ),
            inline=False
        )
        
        view = TicketCloseView()
        await channel.send(embed=embed, view=view)

class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Close Ticket", style=ButtonStyle.red, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Closing ticket in 5 seconds...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

@bot.command()
@commands.has_role(ADMIN_ROLE)  # NUR ADMIN
async def panel(ctx):
    embed = discord.Embed(
        title="🎫 Ticket System",
        description="Choose the type of ticket you want to create:",
        color=0x00008B
    )
    
    embed.add_field(
        name="🛠️ Support",
        value="For general support",
        inline=True
    )
    
    embed.add_field(
        name="💰 Purchase", 
        value="For purchase advice and orders",
        inline=True
    )
    
    embed.add_field(
        name="🎁 Claim",
        value="To receive purchased items", 
        inline=True
    )
    
    view = TicketPanelView()
    await ctx.send(embed=embed, view=view)

# ========== TICKET COMMANDS ==========
@bot.command()
async def close(ctx):
    """Schließt das aktuelle Ticket - FÜR ALLE VERFÜGBAR IN TICKETS"""
    if ctx.channel.category_id in TICKET_CATEGORIES:
        await ctx.send("Closing ticket in 5 seconds...")
        await asyncio.sleep(5)
        await ctx.channel.delete()
    else:
        await ctx.send("❌ This command can only be used in tickets.", delete_after=5)

@bot.command()
@commands.has_role(ADMIN_ROLE)  # NUR ADMIN
async def rename(ctx, *, new_name):
    """Benennt das aktuelle Ticket um"""
    if ctx.channel.category_id in TICKET_CATEGORIES:
        await ctx.channel.edit(name=new_name)
        embed = discord.Embed(
            title="✅ Ticket Renamed",
            description=f"Ticket renamed to: {new_name}",
            color=0x00ff00
        )
        await ctx.send(embed=embed, delete_after=5)
    else:
        await ctx.send("❌ This command can only be used in tickets.", delete_after=5)

# ========== TOS SYSTEM ==========
class TOSView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Yes, I accept", style=ButtonStyle.green, custom_id="accept_tos")
    async def accept_tos(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(VERIFIED_ROLE)
        if role and role not in interaction.user.roles:
            try:
                await interaction.user.add_roles(role)
            except discord.Forbidden:
                await interaction.response.send_message("❌ Bot has no permission to assign roles!", ephemeral=True)
                return
        
        # Sende Bestätigung für ALLE sichtbar
        embed = discord.Embed(
            title="✅ TOS Accepted",
            description="Thank you for accepting our Terms of Service!",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed)
        
        # Sende Nachricht in TOS Channel
        redirect_channel = bot.get_channel(TOS_REDIRECT_CHANNEL)
        if redirect_channel:
            await redirect_channel.send(f"**{interaction.user.display_name}** accepted the TOS")
    
    @discord.ui.button(label="No, I decline", style=ButtonStyle.red, custom_id="decline_tos")
    async def decline_tos(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="❌ TOS Declined",
            description="You must accept the TOS to use our services.",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="What are the TOS?", style=ButtonStyle.blurple, custom_id="what_tos")
    async def what_tos(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📋 TOS Information",
            description=f"Please read our Terms of Service in <#{TOS_CHANNEL}>.",
            color=0x0099ff
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command()
async def tos(ctx):
    """TOS - FÜR ALLE VERFÜGBAR"""
    embed = discord.Embed(
        title="📋 Terms of Service",
        description="To continue the purchase you need to accept our TOS.\n\nPlease read our TOS in the TOS channel and confirm below:",
        color=0x00008B
    )
    
    view = TOSView()
    await ctx.send(embed=embed, view=view)

# ========== MODERATIONS-BEFEHLE ==========
@bot.command()
@commands.has_role(ADMIN_ROLE)  # NUR ADMIN
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    """Bannt einen User vom Server"""
    try:
        await member.ban(reason=f"{ctx.author}: {reason}")
        embed = discord.Embed(
            title="🔨 User Banned",
            description=f"**{member.display_name}** was banned by **{ctx.author.display_name}**",
            color=0xff0000
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        await ctx.send(embed=embed, delete_after=10)
    except Exception as e:
        await ctx.send(f"❌ Error: {e}", delete_after=5)

@bot.command()
@commands.has_role(ADMIN_ROLE)  # NUR ADMIN
async def unban(ctx, user_id: int, *, reason="No reason provided"):
    """Entbannt einen User mit dessen User-ID"""
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user, reason=f"{ctx.author}: {reason}")
        embed = discord.Embed(
            title="🔓 User Unbanned", 
            description=f"**{user.name}** was unbanned by **{ctx.author.display_name}**",
            color=0x00ff00
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        await ctx.send(embed=embed, delete_after=10)
    except Exception as e:
        await ctx.send(f"❌ Error: {e}", delete_after=5)

@bot.command()
@commands.has_role(ADMIN_ROLE)  # NUR ADMIN
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    """Kickt einen User vom Server"""
    try:
        await member.kick(reason=f"{ctx.author}: {reason}")
        embed = discord.Embed(
            title="👢 User Kicked",
            description=f"**{member.display_name}** was kicked by **{ctx.author.display_name}**",
            color=0xff9900
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        await ctx.send(embed=embed, delete_after=10)
    except Exception as e:
        await ctx.send(f"❌ Error: {e}", delete_after=5)

@bot.command()
@commands.has_role(ADMIN_ROLE)  # NUR ADMIN
async def mute(ctx, member: discord.Member, minutes: int = 60, *, reason="No reason provided"):
    """Stummschaltet einen User für eine bestimmte Zeit"""
    try:
        # Timeout setzen
        until = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
        await member.timeout(until, reason=f"{ctx.author}: {reason}")
        
        embed = discord.Embed(
            title="🔇 User Muted",
            description=f"**{member.display_name}** was muted for {minutes} minutes by **{ctx.author.display_name}**",
            color=0xffff00
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        await ctx.send(embed=embed, delete_after=10)
    except Exception as e:
        await ctx.send(f"❌ Error: {e}", delete_after=5)

@bot.command()
@commands.has_role(ADMIN_ROLE)  # NUR ADMIN
async def clear(ctx, amount: int = 5):
    """Löscht eine bestimmte Anzahl an Nachrichten"""
    if amount > 100:
        amount = 100
    deleted = await ctx.channel.purge(limit=amount + 1)
    embed = discord.Embed(
        title="🧹 Messages Cleared",
        description=f"Deleted {len(deleted) - 1} messages",
        color=0x00ff00
    )
    await ctx.send(embed=embed, delete_after=5)

@bot.command()
@commands.has_role(ADMIN_ROLE)  # NUR ADMIN
async def nick(ctx, member: discord.Member, *, new_nickname):
    """Ändert den Nickname eines Users"""
    try:
        old_nick = member.display_name
        await member.edit(nick=new_nickname)
        embed = discord.Embed(
            title="📝 Nickname Changed",
            description=f"Changed **{member.display_name}**'s nickname",
            color=0x00ff00
        )
        embed.add_field(name="From", value=old_nick, inline=True)
        embed.add_field(name="To", value=new_nickname, inline=True)
        await ctx.send(embed=embed, delete_after=10)
    except Exception as e:
        await ctx.send(f"❌ Error: {e}", delete_after=5)

# ========== BLACKLIST SYSTEM ==========
@bot.command()
@commands.has_role(ADMIN_ROLE)  # NUR ADMIN
async def blacklist(ctx, *, word):
    """Fügt ein Wort zur Blacklist hinzu"""
    if word.lower() not in blacklisted_words:
        blacklisted_words.append(word.lower())
        embed = discord.Embed(
            title="✅ Word Blacklisted",
            description=f"`{word}` has been added to the blacklist.",
            color=0x00ff00
        )
        await ctx.send(embed=embed, delete_after=5)
    else:
        await ctx.send("❌ Word is already blacklisted.", delete_after=5)

@bot.command()
@commands.has_role(ADMIN_ROLE)  # NUR ADMIN
async def unblacklist(ctx, *, word):
    """Entfernt ein Wort von der Blacklist"""
    if word.lower() in blacklisted_words:
        blacklisted_words.remove(word.lower())
        embed = discord.Embed(
            title="✅ Word Removed",
            description=f"`{word}` has been removed from the blacklist.",
            color=0x00ff00
        )
        await ctx.send(embed=embed, delete_after=5)
    else:
        await ctx.send("❌ Word is not in blacklist.", delete_after=5)

# ========== HELP COMMAND ==========
@bot.command()
async def help(ctx):
    """Zeigt alle verfügbaren Befehle - FÜR ALLE VERFÜGBAR"""
    embed = discord.Embed(
        title="🛠️ STAR JM Bot Commands",
        description="**All commands use `?` prefix and are auto-deleted**\n\n**How to use each command:**",
        color=0x00008B
    )
    
    embed.add_field(
        name="🔐 **VERIFICATION** (For Everyone)",
        value=(
            "`?verify` - **Verify your account to access all channels**\n"
            "`?tos` - **Accept Terms of Service**\n"
            "`?help` - **Shows this help message**"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🎫 **TICKETS**",
        value=(
            "`?close` - **Closes current ticket** (Only works in tickets)\n"
            "`?panel` - **Creates ticket selection panel** (Admin only)\n"
            "`?rename [new_name]` - **Renames current ticket** (Admin only)"
        ),
        inline=False
    )
    
    embed.add_field(
        name="💰 **PAYMENT COMMANDS** (Admin Only)",
        value=(
            "`?btc [amount]` - **Bitcoin payment info**\n*Example: `?btc 50`*\n"
            "`?eth [amount]` - **Ethereum payment info**\n*Example: `?eth 30`*\n"
            "`?ltc [amount]` - **Litecoin payment info**\n*Example: `?ltc 25`*\n"
            "`?paypal [amount]` - **PayPal payment info**\n*Example: `?paypal 50`*\n"
            "`?vouch [service]` - **Vouch instructions**\n*Example: `?vouch spotify`*"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🛡️ **MODERATION** (Admin Only)",
        value=(
            "`?ban @user [reason]` - **Bans a user**\n"
            "`?unban [user_id]` - **Unbans a user**\n"
            "`?kick @user [reason]` - **Kicks a user**\n"
            "`?mute @user [minutes] [reason]` - **Mutes a user**\n"
            "`?clear [amount]` - **Deletes messages**\n"
            "`?nick @user [new_nick]` - **Changes nickname**\n"
            "`?blacklist [word]` - **Adds word to blacklist**\n"
            "`?unblacklist [word]` - **Removes word from blacklist**"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🎉 **GIVEAWAY** (Admin Only)",
        value=(
            "`?giveaway [time] [prize]` - **Starts a giveaway**\n"
            "*Example: `?giveaway 1h Discord Nitro`*"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📢 **UTILITY** (Admin Only)",
        value=(
            "`?welcome` - **Sends welcome message**\n"
        ),
        inline=False
    )
    
    embed.set_footer(text="STAR JM • Quality Services & Best Prices")
    
    # Sende für alle sichtbar (nicht ephemeral)
    await ctx.send(embed=embed)

# ========== SPECIAL USER COMMANDS ==========
@bot.command()
@is_special_user()
async def special(ctx):
    embed = discord.Embed(
        title="🌟 Special User Access",
        description="You have full access to all bot functions!",
        color=0xff00ff
    )
    await ctx.send(embed=embed, delete_after=10)

# ========== ERROR HANDLING ==========
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.", delete_after=5)
    elif isinstance(error, commands.MissingRole):
        await ctx.send("❌ You don't have the required role for this command.", delete_after=5)
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("❌ You don't have access to this command.", delete_after=5)
    else:
        print(f"Error: {error}")

# ========== BOT START ==========
if __name__ == "__main__":
    # Token aus Environment Variable lesen (für Railway)
    import os
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    if TOKEN:
        print("🚀 Starting STAR JM Bot on Railway...")
        print("🔔 24/7 Online System aktiviert!")
        bot.run(TOKEN)
    else:
        print("❌ ERROR: DISCORD_TOKEN not found!")
        print("💡 Bitte setze DISCORD_TOKEN in Railway Environment Variables!")