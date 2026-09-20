import io
import sys
import typing
import discord
from discord import app_commands
from discord.ext import commands

from config import DISCORD_BOT_TOKEN, UPI_ID, PAYEE_NAME, COMMAND_PREFIX
from qr_generator import generate_upi_qr

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

class PaymentActionView(discord.ui.View):
    """Interactive Discord buttons for copy actions (Discord disallows non-http link schemes)."""
    def __init__(self, upi_url: str, upi_id: str, amount: float):
        super().__init__(timeout=None)
        self.upi_url = upi_url
        self.upi_id = upi_id
        self.amount = amount

    @discord.ui.button(label='Copy UPI ID', style=discord.ButtonStyle.secondary, emoji='📋')
    async def copy_upi(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f'**Payee:** {PAYEE_NAME}\n**UPI ID:** `{self.upi_id}`\n**Amount:** `₹{self.amount:,.2f}`\n\n*(Copy and paste into GPay, PhonePe, Paytm, etc.)*',
            ephemeral=True
        )

    @discord.ui.button(label='UPI Pay Link', style=discord.ButtonStyle.primary, emoji='📱')
    async def copy_link(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f'**UPI Payment Deep Link:**\n```{self.upi_url}```\n*(Copy this URI to trigger payment directly on mobile devices)*',
            ephemeral=True
        )

def create_payment_response(amount: float, note: str = 'Payment'):
    qr_buf, upi_url = generate_upi_qr(amount, note)
    file = discord.File(fp=qr_buf, filename='payment_qr.png')

    embed = discord.Embed(
        title='💳 Payment QR',
        description=f'Amount should be paid - **₹{amount:,.2f}**\n\nScan this QR code using **Google Pay**, **PhonePe**, **Paytm**, or any UPI app.',
        color=0xFEE75C,  # Gold/amber accent matching reference
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name='Payee', value=PAYEE_NAME, inline=True)
    embed.add_field(name='UPI ID', value=f'`{UPI_ID}`', inline=True)
    if note and note != 'Payment':
        embed.add_field(name='Note', value=note, inline=False)

    embed.set_image(url='attachment://payment_qr.png')
    embed.set_footer(text='Secure UPI Payment | Click buttons below for details')

    view = PaymentActionView(upi_url=upi_url, upi_id=UPI_ID, amount=amount)
    return embed, file, view

class QRModal(discord.ui.Modal, title='Generate Payment QR'):
    """Modal popup dialog when a user runs /qr without specifying an amount."""
    amount_input = discord.ui.TextInput(
        label='Enter Amount (in ₹ INR)',
        placeholder='e.g. 500 or 3500.00',
        required=True,
        min_length=1,
        max_length=12
    )
    note_input = discord.ui.TextInput(
        label='Payment Note / Reason (Optional)',
        placeholder='Payment',
        default='Payment',
        required=False,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        clean_amount = self.amount_input.value.strip().replace('₹', '').replace(',', '')
        try:
            amount = float(clean_amount)
            if amount <= 0:
                await interaction.response.send_message(
                    '❌ Amount must be greater than 0.',
                    ephemeral=True
                )
                return
        except ValueError:
            await interaction.response.send_message(
                '❌ Invalid amount. Please enter a valid number (e.g. 500 or 3500).',
                ephemeral=True
            )
            return

        note = self.note_input.value.strip() or 'Payment'
        embed, file, view = create_payment_response(amount, note)
        await interaction.response.send_message(embed=embed, file=file, view=view)

async def handle_qr_command(
    interaction: discord.Interaction,
    amount: typing.Optional[float] = None,
    note: str = 'Payment'
):
    if amount is None:
        # Opens an interactive pop-up form in Discord
        await interaction.response.send_modal(QRModal())
    else:
        if amount <= 0:
            await interaction.response.send_message(
                '❌ Amount must be greater than zero.',
                ephemeral=True
            )
            return
        embed, file, view = create_payment_response(amount, note)
        await interaction.response.send_message(embed=embed, file=file, view=view)

@bot.event
async def on_ready():
    print('=' * 50, flush=True)
    print(f'Logged in as: {bot.user.name} (ID: {bot.user.id})', flush=True)
    print(f'Payee UPI ID: {UPI_ID}', flush=True)
    print(f'Payee Name  : {PAYEE_NAME}', flush=True)
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} slash command(s).', flush=True)
    except Exception as e:
        print(f'Failed to sync slash commands: {e}', flush=True)
    print('Bot is ready to accept commands (/qr, /pay, !qr, !pay)!', flush=True)
    print('=' * 50, flush=True)

@bot.tree.command(name='qr', description='Generate a UPI payment QR code')
@app_commands.describe(
    amount='Amount in INR (leave empty to open prompt modal)',
    note='Optional payment note or reason'
)
async def slash_qr(
    interaction: discord.Interaction,
    amount: typing.Optional[float] = None,
    note: str = 'Payment'
):
    await handle_qr_command(interaction, amount=amount, note=note)

@bot.tree.command(name='pay', description='Generate a UPI payment QR code')
@app_commands.describe(
    amount='Amount in INR (leave empty to open prompt modal)',
    note='Optional payment note or reason'
)
async def slash_pay(
    interaction: discord.Interaction,
    amount: typing.Optional[float] = None,
    note: str = 'Payment'
):
    await handle_qr_command(interaction, amount=amount, note=note)

@bot.command(name='qr', aliases=['pay'])
async def prefix_qr(ctx: commands.Context, amount: float, *, note: str = 'Payment'):
    if amount <= 0:
        await ctx.reply('❌ Amount must be greater than zero.')
        return

    embed, file, view = create_payment_response(amount, note)
    await ctx.reply(embed=embed, file=file, view=view)

@prefix_qr.error
async def prefix_qr_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f'⚠️ Usage: `{COMMAND_PREFIX}qr <amount> [optional note]`\nExample: `{COMMAND_PREFIX}qr 3500`')
    elif isinstance(error, commands.BadArgument):
        await ctx.reply('❌ Invalid amount. Please enter a valid number (e.g. 500 or 3500.50).')
    else:
        await ctx.reply(f'An error occurred: {error}')

def main():
    if not DISCORD_BOT_TOKEN or DISCORD_BOT_TOKEN == 'YOUR_DISCORD_BOT_TOKEN_HERE':
        print('\n' + '=' * 60, flush=True)
        print('ERROR: DISCORD_BOT_TOKEN is not set!', flush=True)
        print('Please open .env and add your Discord bot token:', flush=True)
        print('DISCORD_BOT_TOKEN=your_token_here', flush=True)
        print('=' * 60 + '\n', flush=True)
        sys.exit(1)

    bot.run(DISCORD_BOT_TOKEN)

if __name__ == '__main__':
    main()
