import discord
from discord.ext import commands
import sqlite3 as sqlite
from datetime import datetime

class ReSetupView(discord.ui.View):
    def __init__(self):
        super().__init__()
        
    @discord.ui.button(label="Evet!", style=discord.ButtonStyle.green)
    async def correct(self, button, interaction):
        conn = sqlite.connect('bot_database.db')
        cursor = conn.cursor()
        upload = "INSERT OR REPLACE INTO logs (guild_id, name, channel_id) VALUES (?, ?, ?)"

        guild = interaction.guild
        role = guild.default_role
        overwrites = {
            role: discord.PermissionOverwrite(view_channel=False)
        }

        log_category = await guild.create_category("Logs", overwrites=overwrites)
        log_members = await guild.create_text_channel("member-logs", category=log_category, overwrites=overwrites)
        log_message = await guild.create_text_channel("message-logs", category=log_category, overwrites=overwrites)
        log_role = await guild.create_text_channel("role-logs", category=log_category, overwrites=overwrites)
        log_channel = await guild.create_text_channel("channel-logs", category=log_category, overwrites=overwrites)
        
        cursor.execute(upload, (guild.id, 'log_members', log_members.id))
        cursor.execute(upload, (guild.id, 'log_message', log_message.id))
        cursor.execute(upload, (guild.id, 'log_role', log_role.id))
        cursor.execute(upload, (guild.id, 'log_channel', log_channel.id))
        conn.commit()

        embed = discord.Embed(
            title="Yeniden Kurulum Tamamlandı!",
            colour=0x3eac5a          
        )
        embed.set_author(
            name="PatModaration",
            icon_url="https://i.imgur.com/MVXNngu.jpg"
        )
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Hayır!", style=discord.ButtonStyle.red)
    async def wrong(self, button, interaction):
        embed = discord.Embed(
            title="İşlem İptal Edildi!",
            colour=0x932525          
        )
        embed.set_author(
            name="PatModaration",
            icon_url="https://i.imgur.com/MVXNngu.jpg"
        )
        await interaction.response.edit_message(embed=embed, view=None)

def check_setup_exists(cursor, guild_id):
    cursor.execute('SELECT EXISTS(SELECT 1 FROM logs WHERE name = "setup" AND guild_id = ?)', (guild_id,))
    result = cursor.fetchone()
    return result[0] == 1

class log_system(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.setup_database()

    def setup_database(self):
        self.conn = sqlite.connect('bot_database.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id TEXT NOT NULL,
            name TEXT NOT NULL,
            channel_id TEXT,
            UNIQUE(guild_id, name)
        )
        ''')
        self.conn.commit()

    icon = "https://i.imgur.com/MVXNngu.jpg"

    @commands.slash_command(name="log_setup", description="Loglar için Kurulum Yap!")
    async def log_setup(self, ctx):
        guild = ctx.guild
        cursor = self.conn.cursor()

        if check_setup_exists(cursor, guild.id):
            embed = discord.Embed(
                title="Kurulum Tekrar Yapılsın mı?",
                colour=0xf1ff29       
            )
            embed.set_author(
                name="PatModaration",
                icon_url=self.icon
            )
            await ctx.respond(embed=embed, ephemeral=True, view=ReSetupView())
        else:
            add = "INSERT OR REPLACE INTO logs (guild_id, name, channel_id) VALUES (?, ?, ?)"
            role = guild.default_role
            overwrites = {
                role: discord.PermissionOverwrite(view_channel=False)
            }
            log_category = await guild.create_category("Logs", overwrites=overwrites)
            log_members = await guild.create_text_channel("member-logs", category=log_category, overwrites=overwrites)
            log_message = await guild.create_text_channel("message-logs", category=log_category, overwrites=overwrites)
            log_role = await guild.create_text_channel("role-logs", category=log_category, overwrites=overwrites)
            log_channel = await guild.create_text_channel("channel-logs", category=log_category, overwrites=overwrites)

            cursor.execute(add, (guild.id, 'setup', None))
            cursor.execute(add, (guild.id, 'log_members', log_members.id))
            cursor.execute(add, (guild.id, 'log_message', log_message.id))
            cursor.execute(add, (guild.id, 'log_role', log_role.id))
            cursor.execute(add, (guild.id, 'log_channel', log_channel.id))
            self.conn.commit()

            embed = discord.Embed(
                title="Kurulum Tamamlandı!",
                colour=0x3eac5a          
            )
            embed.set_author(
                name="PatModaration",
                icon_url=self.icon
            )
            await ctx.respond(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if check_setup_exists(self.cursor, member.guild.id):
            guild = member.guild
            channel_id = self.cursor.execute('SELECT channel_id FROM logs WHERE name = "log_members" AND guild_id = ?', (guild.id,)).fetchone()
            if channel_id:
                channel = guild.get_channel(int(channel_id[0]))
                embed = discord.Embed(
                    title=f"**{member.display_name}** Sunucuya Katıldı",
                    description=f"Kullanıcı: {member.mention}\nKullanıcı ID: {member.id}\nHesabı oluşturma tarihi: {member.created_at}",
                    colour=0xf1ff29,
                    timestamp=datetime.now()          
                )
                embed.set_author(
                    name=member.name,
                    icon_url=member.avatar
                )
                embed.set_footer(text=member.id)
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if check_setup_exists(self.cursor, member.guild.id):
            guild = member.guild
            channel_id = self.cursor.execute('SELECT channel_id FROM logs WHERE name = "log_members" AND guild_id = ?', (guild.id,)).fetchone()
            if channel_id:
                channel = guild.get_channel(int(channel_id[0]))
                embed = discord.Embed(
                    title=f"**{member.display_name}** Sunucudan Ayrıldı",
                    description=f"Kullanıcı: {member.mention}\nKullanıcı ID: {member.id}", 
                    colour=0xf1ff29,
                    timestamp=datetime.now()          
                )
                embed.set_author(
                    name=member.name,
                    icon_url=member.avatar
                )
                embed.set_footer(text=member.id)
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.guild and check_setup_exists(self.cursor, after.guild.id):
            guild = after.guild
            channel_id = self.cursor.execute('SELECT channel_id FROM logs WHERE name = "log_message" AND guild_id = ?', (guild.id,)).fetchone()
            if channel_id:
                channel = guild.get_channel(int(channel_id[0]))
                embed = discord.Embed(
                    title=f"**{after.author.display_name}** Mesaj Editledi",
                    description=f"Ping: {after.author.mention}\nÖnceki: {before.content}\nSonraki: {after.content}",
                    colour=0xf1ff29,
                    timestamp=datetime.now()          
                )
                embed.set_author(
                    name=after.author.name,
                    icon_url=after.author.avatar
                )
                embed.set_footer(text=after.id)
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild and check_setup_exists(self.cursor, message.guild.id):
            guild = message.guild
            channel_id = self.cursor.execute('SELECT channel_id FROM logs WHERE name = "log_message" AND guild_id = ?', (guild.id,)).fetchone()
            if channel_id:
                channel = guild.get_channel(int(channel_id[0]))
                embed = discord.Embed(
                    title=f"**{message.author.display_name}** Kullanıcısının Mesajı Sildi",
                    description=f"Mesaj Sahibi: {message.author.mention}\nSilinen mesaj: {message.content}",
                    colour=0xf1ff29,
                    timestamp=datetime.now()          
                )
                embed.set_author(
                    name=message.author.name,
                    icon_url=message.author.avatar
                )
                embed.set_footer(text=message.id)
                await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(log_system(bot))
