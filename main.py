import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks
from discord import ui
import pymysql
import mysql.connector as mysql
import time
import enum
import datetime
import pytz
import random
from discord.interactions import Interaction
from discord import Member

con = pymysql.connect(
    host="db-mfl-01.sparkedhost.us",
    port=3306,
    user="u109224_Krhr5CV2M2",
    passwd="LzwM5tsReqzPH^1I1+@@XA2A",
    database="s109224_Bot",
)

cur = con.cursor()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@tasks.loop(seconds=30.0)
async def connection():
    global con
    global cur
    con = pymysql.connect(
        host="db-mfl-01.sparkedhost.us",
        port=3306,
        user="u109224_Krhr5CV2M2",
        passwd="LzwM5tsReqzPH^1I1+@@XA2A",
        database="s109224_Bot",
    )

    cur = con.cursor()


@tasks.loop(hours=24)
async def monday_avg():
    day = datetime.datetime.today().weekday()
    print(day)
    if day == 4:
        channel = bot.get_channel(1210101994216497223)
        cur.execute(
            "SELECT Employee, GROUP_CONCAT(Hours) FROM Shifts GROUP BY Employee"
        )
        result = cur.fetchall()
        if result is None:
            await channel.send(
                f"""- - - END OF WEEK INFO:
                NO EMPLOYEE DATA"""
            )

        for i in result:
            totalHours = 0
            hours = i[-1].split(",")
            for x in hours:
                totalHours += float(x)
            await channel.send(
                f"""- - - END OF WEEK INFO:
            Employee Name: {i[0]}
            Times Clocked-In: {len(hours)}
            Time worked (week): {totalHours} hours
            EMPLOYEE SUMMARY"""
            )

        cur.execute("DELETE FROM Shifts")
        con.commit()


@tasks.loop(minutes=1.0)
async def auto_stream_start():
    global ISLIVE
    channel = bot.get_channel(1112906850090893362)
    guild = bot.get_guild(1112902755426783394)
    role = guild.get_role(1114393370744340621)
    cur.execute("SELECT Live FROM Live_Info ORDER BY Entry DESC LIMIT 1")
    liveStatus = cur.fetchone()[0]
    cur.execute("SELECT Title FROM Live_Info ORDER BY Entry DESC LIMIT 1")
    title = cur.fetchone()[0]
    cur.execute("SELECT Game FROM Live_Info ORDER BY Entry DESC LIMIT 1")
    gameName = cur.fetchone()[0]
    cur.execute("SELECT Noti FROM Live_Info ORDER BY Entry DESC LIMIT 1")
    ISLIVE = cur.fetchone()[0]

    if liveStatus == "True" and ISLIVE == "False":
        message = await channel.send(
            embed=EmbedSections.twitch_noti(EmbedSections(), title, gameName.upper())
        )
        with open("notiID.txt", "r+") as file:
            file.truncate(0)
            file.writelines(str(message.id))
        await channel.send(role.mention)
        cur.execute(f"UPDATE Live_Info SET Noti = '{True}' WHERE Title = '{title}'")
        con.commit()

    elif liveStatus == "True" and ISLIVE == "True":
        with open("notiID.txt", "r+") as file:
            id = file.readline()
            message = await channel.fetch_message(int(id))
        await message.edit(
            embed=EmbedSections.twitch_noti(EmbedSections(), title, gameName.upper())
        )
    else:
        pass


@tasks.loop(hours=12)
async def leaderboard_check():
    cur.execute(
        f"SELECT TwitchID, DiscordID, Gambled FROM Gambling ORDER BY Gambled DESC LIMIT 1"
    )
    topGambler = cur.fetchone()
    cur.execute(
        f"SELECT TwitchID, DiscordID, AmountGambled FROM Gambling ORDER BY AmountGambled DESC LIMIT 1"
    )
    bigSpender = cur.fetchone()
    cur.execute(
        f"SELECT TwitchID, DiscordID, AmountWon FROM Gambling ORDER BY AmountWon DESC LIMIT 1"
    )
    bigWinner = cur.fetchone()
    cur.execute(
        f"SELECT TwitchID, DiscordID, AmountLost FROM Gambling ORDER BY AmountLost DESC LIMIT 1"
    )
    bigLoser = cur.fetchone()
    guild = bot.get_guild(1112902755426783394)

    # ------------------Top gambler Role---------------------------
    if topGambler[1] == 0:
        cur.execute(f"SELECT DiscordID FROM Economy WHERE TwitchID = {topGambler[0]}")
        id = cur.fetchone()
        for member in bot.get_all_members():
            if member.id == id[0]:
                await member.add_roles(guild.get_role(1264375359080763433))

    else:
        for member in bot.get_all_members():
            if member.id == topGambler[1]:
                await member.add_roles(guild.get_role(1264375359080763433))

    # ------------------Big spender Role--------------------------
    if bigSpender[1] == 0:
        cur.execute(f"SELECT DiscordID FROM Economy WHERE TwitchID = {bigSpender[0]}")
        id = cur.fetchone()
        for member in bot.get_all_members():
            if member.id == id[0]:
                await member.add_roles(guild.get_role(1264375729320366193))

    else:
        for member in bot.get_all_members():
            if member.id == bigSpender[1]:
                await member.add_roles(guild.get_role(1264375729320366193))

    # ------------------Winner Role-------------------------------
    if bigWinner[1] == 0:
        cur.execute(f"SELECT DiscordID FROM Economy WHERE TwitchID = {bigWinner[0]}")
        id = cur.fetchone()
        for member in bot.get_all_members():
            if member.id == id[0]:
                await member.add_roles(guild.get_role(1264375977346072598))

    else:
        for member in bot.get_all_members():
            if member.id == bigWinner[1]:
                await member.add_roles(guild.get_role(1264375977346072598))

    # ------------------Loser Role--------------------------------
    if bigLoser[1] == 0:
        cur.execute(f"SELECT DiscordID FROM Economy WHERE TwitchID = {bigLoser[0]}")
        id = cur.fetchone()
        for member in bot.get_all_members():
            if member.id == id[0]:
                await member.add_roles(guild.get_role(1264376546311934024))

    else:
        for member in bot.get_all_members():
            if member.id == bigLoser[1]:
                await member.add_roles(guild.get_role(1264376546311934024))


@tasks.loop(minutes=1.0)
async def auto_stream_end():
    channel = bot.get_channel(1112906850090893362)
    guild = bot.get_guild(1112902755426783394)
    role = guild.get_role(1114393370744340621)
    cur.execute("SELECT Live FROM Live_Info ORDER BY Entry DESC LIMIT 1")
    liveStatus = cur.fetchone()[0]
    cur.execute("SELECT Noti FROM Live_Info ORDER BY Entry DESC LIMIT 1")
    ISLIVE = cur.fetchone()[0]

    if liveStatus == "False" and ISLIVE == "True":
        await channel.purge(limit=10)
        cur.execute(f"UPDATE Live_Info SET Noti = '{False}' WHERE Noti = 'True'")
        con.commit()


@bot.event
async def on_ready():
    print("Bot is up")
    connection.start()
    auto_stream_start.start()
    auto_stream_end.start()
    monday_avg.start()
    leaderboard_check.start()
    print("connected to: ", con.get_server_info())
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)


@bot.event
async def on_message(message):
    cur.execute("SELECT Live FROM Live_Info ORDER BY Entry DESC LIMIT 1")
    liveStatus = cur.fetchone()[0]
    if liveStatus == "False":
        if (
            message.channel.id == 1112902756022358039
            or message.channel.id == 1190462505097633792
        ):
            cur.execute(
                f"SELECT DiscordID FROM Economy WHERE DiscordID = '{message.author.id}'"
            )
            id = cur.fetchone()

            if id:
                cur.execute(
                    f"UPDATE Economy SET Potatoes = Potatoes + {1} WHERE DiscordID = {message.author.id}"
                )
            else:
                pass
    else:
        pass


def contains_link(content):
    return any(
        word.startswith(("http://", "https://", "www.")) for word in content.split()
    )


#       ACTUAL BOT        #
# -------------------------#
class Variables:
    alternate = False  # Button alternate functions. (Off by default)
    notiamount = 0


class EmbedSections:
    twitchNotiImg = random.choice(
        [
            "https://cdn.discordapp.com/attachments/1112902756022358039/1120788781268750437/20230620_145403.jpg",
            "https://i.pinimg.com/originals/da/99/60/da99605920778b7b85b4fbb96cbacb78.gif",
            "https://cdn.discordapp.com/attachments/716739197922312235/1228744898417791016/image.png?ex=662d28dc&is=661ab3dc&hm=ffc623e58a8a474b8c8c7207c71db4e209e3f14863a3bbbd633acc426843ac0d&",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNmFiY2ZlZjUxMmJiYmU0Yzc1ZTY4NGNhNTBkODQ2MDhhODcwODczMyZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/SMoMrhoSQvPBXhxqzj/giphy.gif",
        ]
    )

    def title_card():
        embed = discord.Embed(title="Tatox3 Menu", color=0x6FFF7B)
        embed.set_image(
            url="https://media.giphy.com/media/pYy1pETzRveSzWQmEz/giphy.gif"
        )
        return embed

    def help_body(name, avatar_url):
        embed = discord.Embed(color=0x6FFF7B)
        embed.set_author(name=f"\n{name}", icon_url=avatar_url)
        embed.add_field(
            name="🟣 Subscriber roles 🟣",
            value="To get access to your twitch roles if you are subscribed please ensure you have the twitch connection enabled in your personal account settings and we do the rest.",
            inline=False,
        )
        embed.add_field(
            name="🟣 Twitch Live Notifications 🟣",
            value=f"To get notified when Tatox3 goes live on twitch head over to #live-notifications in order to get the notification role",
        )
        embed.add_field(
            name="🚧 More helpful tips to be added soon...🚧\nIf you have any suggestions notify any of the admins",
            value="",
            inline=False,
        )
        embed.set_footer(
            text="If you require further assistance, click on the option you are confused about using the buttons below."
        )
        return embed

    def twitch_body(name, avatar_url):
        embed = discord.Embed(color=0x6FFF7B)
        embed.set_author(name=f"\n{name}", icon_url=avatar_url)
        embed.set_image(
            url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMjZjZTZiZWQxOGY5YWE0NzIwOThkZDM0YjQxZDJhOTUwN2ZmZjU1ZiZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/gli9wNZ5gt2gy9m2Zg/giphy.gif"
        )
        embed.add_field(
            name="Further assistance:",
            value="Below you can find a gif of where you should be looking in your settings to enable your twitch connection.",
            inline=False,
        )
        embed.add_field(
            name="",
            value="1. Go to your settings\n2. Click on the 'Connections' tab\n3. Click on the twitch Icon\n4. Authorize the connection through twitch",
        )
        embed.set_footer(
            text="If you do not find it useful you can contact a moderator or admin."
        )
        return embed

    def twitch_noti_body(name, avatar_url, channel):
        embed = discord.Embed(color=0x6FFF7B)
        embed.set_author(name=f"\n{name}", icon_url=avatar_url)
        embed.add_field(name="Further assistance:", value="", inline=False)
        embed.add_field(
            name="",
            value=f"1. Go to {channel.mention} at the top of the discord\n2. Click on the reaction for which you want to get notified for!",
        )
        embed.set_footer(
            text="If you do not find it useful you can contact a moderator or admin."
        )
        return embed

    def twitch_noti(self, title, game):
        channel = bot.get_channel(1112906850090893362)
        guild = bot.get_guild(1112902755426783394)
        embed = discord.Embed(
            title=f"{title}",
            description=f"TATOX3 IS LIVE ON TWITCH PLAYING {game} COME JOIN!",
            url="https://www.twitch.tv/tatox3_",
            color=0x6441A5,
        )
        embed.set_image(url=self.twitchNotiImg)
        return embed

    def leaderboard_body(result):
        count = 1
        embed = discord.Embed(title="POTATO LEADERBOARD", color=0x6FFF7B)
        embed.set_thumbnail(
            url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdWZvbXVvYmdjNW92ZTNua2EwZWRobnV1N2VqMHBlemM2aWk3eWVjcCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/24vTxomgaewVz5ZwPx/giphy.gif"
        )
        embed.add_field(
            name=f"LEADER: {result[1][0]} -> {result[1][1]} potatoes",
            value=f"· • —–—– ٠ ✤ ٠ —–—– • ·",
        )
        for _ in range(len(result) - 2):
            count += 1
            embed.add_field(
                name=f"#{count} {result[count][0]}: {result[count][1]}",
                value="",
                inline=False,
            )
        embed.set_footer(text="Chat in Henry's twitch chat to earn more")
        return embed


class MenuButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="1", style=discord.ButtonStyle.green)
    async def One(self, interaction: discord.Interaction, button: discord.Button):
        self.Two.disabled = True
        try:
            if Variables.alternate == False:
                button.label = "Back"
                await interaction.response.edit_message(
                    embeds=[
                        EmbedSections.title_card(),
                        EmbedSections.twitch_body(
                            interaction.user.name, interaction.user.avatar.url
                        ),
                    ],
                    view=self,
                )
                Variables.alternate = True
            else:
                await interaction.response.edit_message(
                    embeds=[
                        EmbedSections.title_card(),
                        EmbedSections.help_body(
                            interaction.user.name, interaction.user.avatar.url
                        ),
                    ],
                    view=MenuButtons(),
                )
                Variables.alternate = False
        except Exception as e:
            print(e)

    @discord.ui.button(label="2", style=discord.ButtonStyle.green)
    async def Two(self, interaction: discord.Interaction, button: discord.Button):
        self.One.disabled = True
        try:
            if Variables.alternate == False:
                button.label = "Back"
                await interaction.response.edit_message(
                    embeds=[
                        EmbedSections.title_card(),
                        EmbedSections.twitch_noti_body(
                            interaction.user.name,
                            interaction.user.avatar.url,
                            channel=bot.get_channel(1114394449657745488),
                        ),
                    ],
                    view=self,
                )
                Variables.alternate = True
            else:
                await interaction.response.edit_message(
                    embeds=[
                        EmbedSections.title_card(),
                        EmbedSections.help_body(
                            interaction.user.name, interaction.user.avatar.url
                        ),
                    ],
                    view=MenuButtons(),
                )
                Variables.alternate = False
        except Exception as e:
            print(e)

    @discord.ui.button(label="Exit", style=discord.ButtonStyle.danger)
    async def Exit(self, interaction: discord.Interaction, Button: discord.Button):
        await interaction.response.edit_message(
            view=None, content="Exited.", embed=None
        )


class ClearModal(ui.Modal, title="Clear Command"):
    amount = ui.TextInput(
        label="How much do you want to delete?",
        style=discord.TextStyle.short,
        required=True,
    )
    member = ui.TextInput(
        label="Member name (Optional)",
        style=discord.TextStyle.short,
        required=False,
        default=None,
    )
    reason = ui.TextInput(
        label="Reason (Optional)",
        style=discord.TextStyle.paragraph,
        required=False,
        default=None,
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            if self.member.value == "":
                await interaction.channel.purge(
                    oldest_first=True,
                    limit=int(self.amount.value) - 1,
                    reason=self.reason.value,
                )
                await interaction.response.send_message(
                    f"Chat was cleared by: {interaction.user.mention} ({int(self.amount.value)} messages cleared!)",
                    delete_after=30,
                )
            else:
                await interaction.channel.purge(
                    oldest_first=True,
                    limit=int(self.amount.value),
                    reason=self.reason.value,
                    check=lambda m: m.author.name == self.member.value,
                )
                await interaction.response.send_message(
                    f"{self.member.value}'s chat was cleared by: {interaction.user.mention} ({int(self.amount.value)} messages cleared!)",
                    delete_after=30,
                )
        except Exception as e:
            print(e)
            await interaction.response.send_message(
                "Hmmm... Something went wrong! Please make sure you put a valid integer as an amount.",
                ephemeral=True,
                delete_after=10,
            )


class UnlinkModal(ui.Modal, title="Unlink Command"):
    memberid = ui.TextInput(
        label="Insert the members ID", style=discord.TextStyle.short, required=True
    )
    twitchname = ui.TextInput(
        label="twitch name to unlink from (Optional)",
        style=discord.TextStyle.short,
        required=False,
        default="None",
    )
    reason = ui.TextInput(
        label="Reason (Optional)",
        style=discord.TextStyle.paragraph,
        required=False,
        default="None",
    )

    async def on_submit(self, interaction: discord.Interaction):
        member = bot.get_user(int(self.memberid.value))
        channel = bot.get_channel(1119398653468082270)
        try:
            if self.twitchname.value == "None":
                cur.execute(
                    f"UPDATE Economy SET DiscordID = {0} WHERE DiscordID = {int(self.memberid.value)}"
                )
                con.commit()
                await interaction.response.send_message(
                    f"Successfully unlinked {member.mention} @ all accounts"
                )
                await channel.send(
                    f"""- - - LINK INFO:
                    Discord Name: {member.display_name}
                    Twitch Name: ALL
                    Discord ID: {self.memberid.value}
                    Reason: {self.reason.value}
                    UNLINK SUCCESSFUL"""
                )
            else:
                cur.execute(
                    f"UPDATE Economy SET DiscordiD = {0} WHERE TwitchName = '{str(self.twitchname.value)}'"
                )
                con.commit()

                await interaction.response.send_message(
                    f"Successfully unlinked {member.mention} @ {self.twitchname.value}"
                )
                await channel.send(
                    f"""- - - LINK INFO:
                    Discord Name: {member.display_name}
                    Twitch Name: {self.twitchname.value}
                    Discord ID: {self.memberid.value}
                    Reason: {self.reason.value}
                    UNLINK SUCCESSFUL"""
                )
        except Exception as e:
            print(e)
            await interaction.response.send_message(
                "Hmmm... Something went wrong! Please contact floridaman!",
                ephemeral=True,
                delete_after=10,
            )


@bot.event
async def on_member_join(person):
    await person.add_roles(person.guild.get_role(1112902914160197724))


@bot.event
async def on_raw_reaction_add(payload):
    message = await bot.get_channel(payload.channel_id).fetch_message(
        payload.message_id
    )
    global member
    member = payload.member
    guild = bot.get_guild(1112902755426783394)
    twitch_role = guild.get_role(1114393370744340621)
    music_role = guild.get_role(1114396915400986734)
    if message.id == 1114942064321376256:
        if str(payload.emoji) == "🟣":
            await payload.member.add_roles(twitch_role)
        if str(payload.emoji) == "🎶":
            await payload.member.add_roles(music_role)


@bot.event
async def on_raw_reaction_remove(payload):
    message = await bot.get_channel(payload.channel_id).fetch_message(
        payload.message_id
    )
    guild = bot.get_guild(1112902755426783394)
    twitch_role = guild.get_role(1114393370744340621)
    music_role = guild.get_role(1114396915400986734)
    if message.id == 1114942064321376256:
        if str(payload.emoji) == "🟣":
            await member.remove_roles(twitch_role)
        if str(payload.emoji) == "🎶":
            await member.remove_roles(music_role)


@bot.tree.command(name="discord-help")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(
        embeds=[
            EmbedSections.title_card(),
            EmbedSections.help_body(interaction.user.name, interaction.user.avatar.url),
        ],
        view=MenuButtons(),
        ephemeral=True,
        delete_after=120,
    )


@bot.tree.command(name="fban")
@app_commands.default_permissions(administrator=True)
async def bannedfake(interaction: discord.Interaction, member: discord.Member):
    channel = bot.get_channel(1112902756022358039)

    await channel.send(
        f"{member.mention} has been banned by {interaction.user.mention}"
    )


@bot.tree.command(name="pings")
@app_commands.default_permissions(administrator=True)
async def pinggp(interaction: discord.Interaction):
    channel = bot.get_channel(1112902756022358039)
    user = bot.get_user(353925334426583043)

    message = await channel.send(f"{user.mention} wake up gp")
    await message.delete()


@bot.tree.command(name="clear")
@app_commands.default_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction):
    await interaction.response.send_modal(ClearModal())


@bot.tree.command(
    name="link",
    description="Link the discord bot to your twitch account **CASE SENSITIVE**",
)
async def link(interaction: discord.Interaction, twitchname: str = None):
    channel = bot.get_channel(1119398653468082270)
    if twitchname is None:
        await interaction.response.send_message(
            "Please specify your twitch username..."
        )
    else:
        cur.execute(f"SELECT TwitchName FROM Economy WHERE TwitchName = '{twitchname}'")
        result = cur.fetchone()
        cur.execute(f"SELECT DiscordID FROM Economy WHERE TwitchName = '{twitchname}'")
        discord_result = cur.fetchone()
        cur.execute(
            f"SELECT DiscordID FROM Economy WHERE DiscordID = '{interaction.user.id}'"
        )
        discord_id = cur.fetchone()
        if discord_id is not None:
            await interaction.response.send_message(
                f"Looks like you are already linked to an account. Please contact floridaman if you wish to change this...",
                ephemeral=True,
            )
        else:
            try:
                print(discord_result)
                if int(discord_result[0]) != 0:
                    await interaction.response.send_message(
                        f"This twitch name has already been registered to a user with the ID {discord_result[0]}",
                        ephemeral=True,
                    )
                if result is None:
                    pass
                if int(discord_result[0]) == 0:
                    cur.execute(
                        f"UPDATE Economy SET DiscordID = {interaction.user.id} WHERE TwitchName = '{twitchname}'"
                    )
                    con.commit()
                    await interaction.response.send_message(
                        f"{twitchname} and {interaction.user.name} have been linked succesfully!"
                    )
                    await channel.send(
                        f"""- - - LINK INFO:
                    Discord Name: {interaction.user.name}
                    Twitch Name: {twitchname}
                    Discord ID: {interaction.user.id}
                    LINK SUCCESSFUL"""
                    )
                # FUcking make it an embed pls
            except Exception as e:
                print(e)
                await interaction.response.send_message(
                    "Please enter a valid twitch username, make sure you have sent at least 1 message in twitch chat",
                    ephemeral=True,
                )


@bot.tree.command(
    name="unlink",
    description="Used to unlink accounts from discord, will unlink accounts.",
)
@app_commands.default_permissions(administrator=True)
async def unlink(interaction: discord.Interaction):
    await interaction.response.send_modal(UnlinkModal())


@bot.tree.command(name="balance", description="Gets the balance of twitch potatoes")
async def bal(interaction: discord.Interaction):
    user_id = interaction.user.id
    cur.execute(f"SELECT Potatoes FROM Economy WHERE DiscordID = '{user_id}'")
    result = cur.fetchone()
    try:
        if result is None:
            pass
        else:
            await interaction.response.send_message(
                f"Your current potato balance is {result[0]}", ephemeral=True
            )
    except:
        await interaction.response.send_message(
            "Please use /link (twitch username) to link this bot to your twitch account and access your potatoes!"
        )


@bot.tree.command(name="manage", description="Reserved for admins")
async def manage_potatoes(
    interaction: discord.Interaction, member: discord.Member, amount: int
):
    memberID = member.id
    if int(amount):
        cur.execute(
            f"UPDATE Economy SET Potatoes = Potatoes + {amount} WHERE DiscordID = {memberID}"
        )
        con.commit()
    else:
        await interaction.response.send_message("Something went wrong, try again.")

    if amount < 0:
        await interaction.response.send_message(
            f"Took {amount} potatoes from {member.mention}"
        )
    else:
        await interaction.response.send_message(
            f"Gave {amount} potatoes to {member.mention}"
        )


@bot.tree.command(
    name="activity",
    description="Used to see all recent chatting activity this month! (Resets the first of every month)",
)
async def recent_activity(interaction: discord.Interaction):
    channel = bot.get_channel(interaction.channel.id)
    cur.execute(f"SELECT TwitchName, Potatoes FROM Activity ORDER BY Potatoes DESC")
    result = cur.fetchall()
    result = list(result)
    pages = -(len(result) // -25)
    currentPage = 1
    while currentPage <= pages:
        if currentPage == 1:
            embed = discord.Embed(title=f"Recent Activity this month", color=0x6FFF7B)
            embed.set_thumbnail(
                url="https://i.ytimg.com/vi/7gqFCBgolFU/maxresdefault.jpg"
            )
        else:
            embed = discord.Embed(color=0x6FFF7B)

        if len(result) >= 25:

            for _ in range(25):
                embed.add_field(
                    name=f"{result[0][0]}: {result[0][1]} messages",
                    value="",
                    inline=False,
                )
                result.pop(0)

        else:
            for _ in range(len(result)):
                embed.add_field(
                    name=f"{result[0][0]}: {result[0][1]} messages",
                    value="",
                    inline=False,
                )
                result.pop(0)

        embed.set_footer(
            text=f"This command will reset on the first of every month (later in the day).\nPage {currentPage}"
        )
        await channel.send(embed=embed)
        currentPage += 1


@bot.tree.command(
    name="leaderboard",
    description="Displays the top 5 potato owners in Henry's stream!",
)
async def leaderboard(interaction: discord.Interaction):
    cur.execute(
        f"SELECT TwitchName, Potatoes FROM Economy ORDER BY Potatoes DESC LIMIT 6"
    )
    result = cur.fetchall()
    await interaction.response.send_message(
        embed=EmbedSections.leaderboard_body(result=result)
    )


@bot.tree.command(
    name="rank", description="Shows your ranking on the potato leaderboard"
)
async def rank(interaction: discord.Interaction):
    count = 0
    cur.execute(f"SELECT DiscordID, Potatoes FROM Economy ORDER BY Potatoes DESC")
    result = cur.fetchall()
    try:
        for i in result:
            if i[0] == interaction.user.id:
                await interaction.response.send_message(
                    f"{interaction.user.mention} you are rank #{count} on the potato leaderboard with {i[1]} potatoes"
                )
            count += 1
    except:
        await interaction.response.send_message(
            "Please use /link (twitch username) to link this bot to your twitch account and access your potatoes!"
        )


# -----------------


class Clockinout(str, enum.Enum):
    In = "in"
    Out = "out"


@bot.tree.command(name="clock", description="Command used to log hours")
async def clock(interaction: discord.Interaction, in_out: Clockinout):
    channel = bot.get_channel(1210101994216497223)
    tz = pytz.timezone("EST")
    time = datetime.datetime.now(tz)
    cur.execute(
        f"SELECT ClockIn, ClockOut FROM Shifts WHERE Employee = '{interaction.user.name}' ORDER BY ClockIn DESC"
    )
    result = cur.fetchone()
    bTime = str(time)[0:-13]

    if in_out.value == "in":
        if result is None:
            cur.execute(
                f"INSERT INTO Shifts (Employee, ClockIn, ClockOut, Hours) VALUES ('{interaction.user.name}', '{bTime}', 'NONE', {0})"
            )
            con.commit()
            await interaction.response.send_message(
                f"You have successfully been clocked in!", ephemeral=True
            )
            await channel.send(
                f"""- - - SHIFT INFO:
            Employee Name: {interaction.user.name}
            Clock-in: {bTime}
            EMPLOYEE CLOCK-IN"""
            )

        if str(result[1]).lower() == "none":
            await interaction.response.send_message(
                "ERROR: Clock-in Failed. Seems like you already have an active timer! If this is incorrect please let floridaman or tatox3 know...",
                ephemeral=True,
            )
        else:
            cur.execute(
                f"INSERT INTO Shifts (Employee, ClockIn, ClockOut, Hours) VALUES ('{interaction.user.name}', '{bTime}', 'NONE', {0})"
            )
            con.commit()
            await interaction.response.send_message(
                f"You have successfully been clocked in!", ephemeral=True
            )
            await channel.send(
                f"""- - - SHIFT INFO:
            Employee Name: {interaction.user.name}
            Clock-in: {bTime}
            EMPLOYEE CLOCK-IN"""
            )
    else:
        if str(result[1]).lower() != "none":
            await interaction.response.send_message(
                "ERROR: Seems like you haven't clocked in! If this is incorrect please let floridaman or tatox3 know...",
                ephemeral=True,
            )
        else:
            CIdate = datetime.datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
            COdate = datetime.datetime.strptime(bTime, "%Y-%m-%d %H:%M:%S")
            duration = COdate - CIdate
            duration_in_s = duration.total_seconds()
            hours = round(duration_in_s / 3600, 2)
            cur.execute(
                f"UPDATE Shifts SET ClockOut = '{bTime}' WHERE ClockIn = '{result[0]}'"
            )
            con.commit()
            cur.execute(
                f"UPDATE Shifts SET Hours = '{hours}' WHERE ClockIn = '{result[0]}'"
            )
            con.commit()
            await interaction.response.send_message(
                f"You have successfully been clocked out, thank you for your work!",
                ephemeral=True,
            )
            await channel.send(
                f"""- - - SHIFT INFO:
            Employee Name: {interaction.user.name}
            Clock-out: {bTime}
            Time worked: {hours} hours
            EMPLOYEE CLOCK-OUT"""
            )


class StopButton(discord.ui.Button):
    def __init__(self, amount, author):
        super().__init__(style=discord.ButtonStyle.danger, label="Stop")
        self.characters = []
        self.amount = amount
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        character = self.characters[2]

        if character == "🟥":
            await interaction.response.send_message(
                f"{interaction.user.mention} YOU WIN {int(self.amount * 2)} potatoes!. You landed on: {character}"
            )
            cur.execute(
                f"UPDATE Gambling SET AmountWon = AmountWon + {self.amount} WHERE DiscordID = {interaction.user.id}"
            )
            con.commit()
            cur.execute(
                f"UPDATE Economy SET Potatoes = Potatoes + {int(self.amount * 2)} WHERE DiscordID = {interaction.user.id}"
            )
            con.commit()
        else:
            await interaction.response.send_message(
                f"{interaction.user.mention} YOU LOSE!. You landed on: {character}"
            )
            cur.execute(
                f"UPDATE Gambling SET AmountWon = AmountLost + {self.amount} WHERE DiscordID = {interaction.user.id}"
            )
            con.commit()


@bot.tree.command(
    name="skillcheck", description="Land on the red square before it does 2 loops."
)
@app_commands.default_permissions(administrator=True)
async def skillCheck(interaction: discord.Interaction, amount: int):
    cur.execute(f"SELECT Potatoes FROM Economy WHERE DiscordID = {interaction.user.id}")
    potatoes = cur.fetchone()
    cur.execute(
        f"SELECT DiscordID FROM Gambling WHERE DiscordID = {interaction.user.id}"
    )
    existance = cur.fetchone()
    try:
        if existance is None:
            cur.execute(
                f"INSERT INTO Gambling (TwitchID, DiscordID, Gambled, AmountGambled, AmountWon, AmountLost) VALUES ({0}, {interaction.user.id}, {0}, {0}, {0}, {0})"
            )
        if int(potatoes[0]) >= amount and amount > 0:
            cur.execute(
                f"UPDATE Economy SET Potatoes = Potatoes - {amount} WHERE DiscordID = {interaction.user.id}"
            )
            con.commit()
            cur.execute(
                f"UPDATE Gambling SET Gambled = Gambled + {1}, AmountGambled = AmountGambled + {amount} WHERE DiscordID = {interaction.user.id}"
            )
            con.commit()
        else:
            await interaction.response.send_message(
                f"{interaction.user.mention} It seems you might have less than {amount} potatoes or you did not put a valid bet."
            )
            return
    except Exception as e:
        print(e.with_traceback())
        await interaction.response.send_message(
            f"{interaction.user.mention} something went wrong! Please contact @floridaman0484"
        )
        return
    allCharacters = []
    red_added = False
    while len(allCharacters) <= 8:
        if red_added:
            allCharacters.append("🟩")
        else:
            color = random.choices(["🟩", "🟥"], weights=[4, 2], k=1)[0]
            allCharacters.append(color)
            if color == "🟥":
                red_added = True
    embed = discord.Embed(
        title="Skill Check",
        color=0xCCAC00,
    )
    embed.set_footer(text="Click 'STOP' when the red square is on the > < to win.")
    embed.set_thumbnail(url=interaction.user.avatar.url)

    button = StopButton(amount, interaction.user.id)
    view = discord.ui.View()
    view.add_item(button)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    for i in range(2 * len(allCharacters)):
        if button.disabled == True:
            await interaction.edit_original_response(
                content="Embed Timeout", embed=None, view=None
            )
            break

        selected_characters = allCharacters[
            i % len(allCharacters) : i % len(allCharacters) + 7
        ]
        if len(selected_characters) < 7:
            selected_characters += allCharacters[0 : 7 - len(selected_characters)]
        embed.clear_fields()

        for j, character in enumerate(selected_characters):
            if j == 3:
                embed.add_field(name=f"\> {character} <", value="", inline=False)
            else:
                embed.add_field(name=f"{character}", value="", inline=False)

        button.characters = selected_characters

        await interaction.edit_original_response(embed=embed, view=view)
        time.sleep(0.2)

    if not button.disabled:
        await interaction.edit_original_response(
            content=f"{interaction.user.mention} You Lost! Timer Expired!",
            embed=None,
            view=None,
        )


class Deck:
    suits = ["♣", "♦", "♥", "♠"]
    faces = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

    def __init__(self) -> None:
        self.usedCards = []


class Player:
    def __init__(self, deck) -> None:
        used = False
        self.startDeck = []
        self.value = 0

        for _ in range(2):
            card = (random.choice(seq=Deck.faces), random.choice(seq=Deck.suits))
            if card in self.startDeck:
                used = True
                while used is True:
                    card = (
                        random.choice(seq=Deck.faces),
                        random.choice(seq=Deck.suits),
                    )
                    if card not in self.startDeck:
                        self.startDeck.append(card)
                        deck.usedCards.append(card)
                        used = False
            else:
                self.startDeck.append(card)
                deck.usedCards.append(card)

    def handValue(self):
        self.value = 0
        face = set(["J", "Q", "K"])
        for i in self.startDeck:
            if i[0] in face:
                self.value += 10
            elif i[0] == "A":
                pass
            else:
                self.value += int(i[0])

        for i in self.startDeck:
            if i[0] == "A":
                if self.value + 11 <= 21:
                    self.value += 11
                else:
                    self.value += 1


class Dealer:
    def __init__(self, deck) -> None:
        used = False
        self.startDeck = []
        self.value = 0

        for _ in range(2):
            card = (random.choice(seq=Deck.faces), random.choice(seq=Deck.suits))
            if card in self.startDeck or card in deck.usedCards:
                used = True
                while used is True:
                    card = (
                        random.choice(seq=Deck.faces),
                        random.choice(seq=Deck.suits),
                    )
                    if card not in self.startDeck and card not in deck.usedCards:
                        self.startDeck.append(card)
                        deck.usedCards.append(card)
                        used = False
            else:
                self.startDeck.append(card)
                deck.usedCards.append(card)

    def handValue(self):
        self.value = 0
        face = set(["J", "Q", "K"])
        for i in self.startDeck:
            if i[0] in face:
                self.value += 10
            elif i[0] == "A":
                pass
            else:
                self.value += int(i[0])
        for i in self.startDeck:
            if i[0] == "A":
                if self.value + 11 <= 21:
                    self.value += 11
                else:
                    self.value += 1


class ControlButtons(discord.ui.View):
    def __init__(
        self, player: Player, dealer: Dealer, amount: int, author: int, deck=None
    ):
        self.author = author
        self.player = player
        self.dealer = dealer
        self.amount = amount
        self.deck = deck
        super().__init__(timeout=None)

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.author:
            used = False
            card = (random.choice(seq=Deck.faces), random.choice(seq=Deck.suits))
            if card not in self.deck.usedCards:
                self.player.startDeck.append(card)
                self.deck.usedCards.append(card)
            else:
                used = True
                while used is True:
                    card = (
                        random.choice(seq=Deck.faces),
                        random.choice(seq=Deck.suits),
                    )
                    if card not in self.deck.usedCards:
                        self.player.startDeck.append(card)
                        self.deck.usedCards.append(card)
                        used = False
            self.player.handValue()
            value = ""
            for i in range(len(self.player.startDeck) - 1):
                value += f"{self.player.startDeck[i][0]}{self.player.startDeck[i][1]}, "
            value += f"{self.player.startDeck[-1][0]}{self.player.startDeck[-1][1]}"

            embed = discord.Embed(title="Blackjack!", color=0xCCAC00)
            embed.add_field(
                name=f"Dealer's Hand:",
                value=f"{self.dealer.startDeck[0][0]}{self.dealer.startDeck[0][1]}, Hidden",
                inline=False,
            )
            embed.add_field(
                name=f"Player's Hand (value: {self.player.value}):",
                value=value,
                inline=False,
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            embed.set_footer(text="Get as close to 21, but dont go over!")

            if self.player.value > 21:
                embed.color = 0xFF0000
                embed.title = "You Busted! (Lost)"
                embed.description = f"You lost {self.amount} potatoes"

                embed.clear_fields()
                embed.add_field(
                    name=f"Dealer's Hand:",
                    value=f"{self.dealer.startDeck[0][0]}{self.dealer.startDeck[0][1]}, {self.dealer.startDeck[1][0]}{self.dealer.startDeck[1][1]} ",
                    inline=False,
                )
                embed.add_field(
                    name=f"Player's Hand (value: {self.player.value}):",
                    value=value,
                    inline=False,
                )

                button.disabled = True
                self.stand.disabled = True
                cur.execute(
                    f"UPDATE Gambling SET AmountLost = AmountLost + {int(self.amount)} WHERE DiscordID = {interaction.user.id}"
                )
                con.commit()

            if self.player.value == 21:
                button.disabled = True

            await interaction.response.edit_message(embed=embed, view=self)
        else:
            pass

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.danger)
    async def stand(
        self,
        interaction: discord.Interaction,
        button: discord.Button,
        embed=None,
    ):
        if interaction.user.id == self.author:

            used = False
            if embed is None:
                embed = discord.Embed(title="Blackjack!", color=0xCCAC00)
            while True:
                card = (random.choice(seq=Deck.faces), random.choice(seq=Deck.suits))
                if self.dealer.value < 17:
                    if card not in self.deck.usedCards:
                        self.dealer.startDeck.append(card)
                        self.deck.usedCards.append(card)
                    else:
                        used = True
                        while used is True:
                            card = (
                                random.choice(seq=Deck.faces),
                                random.choice(seq=Deck.suits),
                            )
                            if card not in self.deck.usedCards:
                                self.dealer.startDeck.append(card)
                                self.deck.usedCards.append(card)
                                used = False
                self.dealer.handValue()
                dealerValue = ""
                for i in range(len(self.dealer.startDeck) - 1):
                    dealerValue += (
                        f"{self.dealer.startDeck[i][0]}{self.dealer.startDeck[i][1]}, "
                    )
                dealerValue += (
                    f"{self.dealer.startDeck[-1][0]}{self.dealer.startDeck[-1][1]}"
                )

                playerValue = ""
                for i in range(len(self.player.startDeck) - 1):
                    playerValue += (
                        f"{self.player.startDeck[i][0]}{self.player.startDeck[i][1]}, "
                    )
                playerValue += (
                    f"{self.player.startDeck[-1][0]}{self.player.startDeck[-1][1]}"
                )

                embed.add_field(
                    name=f"Dealer's Hand (value: {self.dealer.value}):",
                    value=dealerValue,
                    inline=False,
                )
                embed.add_field(
                    name=f"Player's Hand (value: {self.player.value}):",
                    value=playerValue,
                    inline=False,
                )
                embed.set_thumbnail(url=interaction.user.avatar.url)
                embed.set_footer(text="Get as close to 21, but dont go over!")

                if self.dealer.value >= 17:
                    break
                embed.clear_fields()

            if self.dealer.value > 21 or self.player.value > self.dealer.value:
                embed.title = "You win!"
                if self.player.value == 21:
                    embed.description = f"You win {self.amount * 2.5} potatoes"
                    cur.execute(
                        f"UPDATE Gambling SET AmountWon = AmountWon + {int(self.amount * 1.5)} WHERE DiscordID = {interaction.user.id}"
                    )
                    con.commit()
                    cur.execute(
                        f"UPDATE Economy SET Potatoes = Potatoes + {int(self.amount * 2.5)} WHERE DiscordID = {interaction.user.id}"
                    )
                    con.commit()
                else:
                    embed.description = f"You win {self.amount * 2} potatoes"
                    cur.execute(
                        f"UPDATE Gambling SET AmountWon = AmountWon + {int(self.amount * 1.5)} WHERE DiscordID = {interaction.user.id}"
                    )
                    con.commit()
                    cur.execute(
                        f"UPDATE Economy SET Potatoes = Potatoes + {int(self.amount * 2)} WHERE DiscordID = {interaction.user.id}"
                    )
                    con.commit()

            elif self.player.value == self.dealer.value:
                embed.title = "You Draw!"
                embed.description = f"{self.amount} potatoes have been refunded"
                embed.color = 0x808080
                cur.execute(
                    f"UPDATE Economy SET Potatoes = Potatoes + {self.amount} WHERE DiscordID = {interaction.user.id}"
                )
                con.commit()

            elif self.player.value < self.dealer.value or self.dealer.value == 21:
                embed.title = "You Lose!"
                embed.color = 0xFF0000
                embed.description = f"You lost {self.amount} potatoes"
                cur.execute(
                    f"UPDATE Gambling SET AmountLost = AmountLost + {int(self.amount)} WHERE DiscordID = {interaction.user.id}"
                )
                con.commit()

            await interaction.response.edit_message(embed=embed, view=None)
        else:
            pass


@bot.tree.command(
    name="blackjack",
    description="Aim for as close a 21 as possible without busting. PAYOUTS: 2x for win, 2.5x for a blackjack",
)
async def bj(interaction: discord.Interaction, amount: int):
    cur.execute(f"SELECT Potatoes FROM Economy WHERE DiscordID = {interaction.user.id}")
    potatoes = cur.fetchone()
    cur.execute(
        f"SELECT DiscordID FROM Gambling WHERE DiscordID = {interaction.user.id}"
    )
    existance = cur.fetchone()
    try:
        if existance is None:
            cur.execute(
                f"INSERT INTO Gambling (TwitchID, DiscordID, Gambled, AmountGambled, AmountWon, AmountLost) VALUES ({0}, {interaction.user.id}, {0}, {0}, {0}, {0})"
            )
        if int(potatoes[0]) >= amount and amount > 0:
            cur.execute(
                f"UPDATE Economy SET Potatoes = Potatoes - {amount} WHERE DiscordID = {interaction.user.id}"
            )
            con.commit()
            cur.execute(
                f"UPDATE Gambling SET Gambled = Gambled + {1}, AmountGambled = AmountGambled + {amount} WHERE DiscordID = {interaction.user.id}"
            )
            con.commit()
        else:
            await interaction.response.send_message(
                f"{interaction.user.mention} It seems you might have less than {amount} potatoes or you did not put a valid bet."
            )
            return

    except Exception as e:
        print(e.with_traceback())
        await interaction.response.send_message(
            f"{interaction.user.mention} something went wrong! Please contact @floridaman0484"
        )
        return
    deck = Deck()
    player = Player(deck)
    player.handValue()
    dealer = Dealer(deck)
    dealer.handValue()
    embed = discord.Embed(title="Blackjack!", color=0xCCAC00)
    embed.add_field(
        name=f"Dealer's Hand:",
        value=f"{dealer.startDeck[0][0]}, Hidden",
        inline=False,
    )
    embed.add_field(
        name=f"Player's Hand (value: {player.value}):",
        value=f"{player.startDeck[0][0]}{player.startDeck[0][1]}, {player.startDeck[1][0]}{player.startDeck[1][1]} ",
        inline=False,
    )
    embed.set_thumbnail(url=interaction.user.avatar.url)
    embed.set_footer(text="Get as close to 21, but dont go over!")
    await interaction.response.send_message(
        embed=embed,
        view=ControlButtons(player, dealer, amount, interaction.user.id, deck),
    )


@bot.tree.command(name="stats", description="Check all your stats!")
@app_commands.default_permissions(administrator=True)
async def gstats(interaction: discord.Interaction, member: discord.Member = None):
    await interaction.response.defer(thinking=True)
    if member is None:
        member = interaction.user.id

        # ------------------Info--------------------------------
        cur.execute(
            f"SELECT TwitchName, TwitchID FROM Economy WHERE DiscordID = {member}"
        )
        info = cur.fetchone()

        # ------------------Gambling----------------------------

        cur.execute(f"SELECT * FROM Gambling WHERE DiscordID = {member}")
        gambleStats = cur.fetchone()
        gambled = gambleStats[2]
        amountGambled = gambleStats[3]
        amountWon = gambleStats[4]
        amountLost = gambleStats[5]

        # ------------------Economy-----------------------------

        cur.execute(f"SELECT Potatoes FROM Economy WHERE DiscordID = {member}")
        economyStats = cur.fetchone()
        potatoes = economyStats[0]
        cur.execute(f"SELECT DiscordID, Potatoes FROM Economy ORDER BY Potatoes DESC")
        result = cur.fetchall()
        count = 0
        for i in result:
            if i[0] == member:
                rank = count
            count += 1

        # ------------------Activity----------------------------

        cur.execute(f"SELECT Potatoes FROM Activity WHERE TwitchID = {info[1]}")
        messages = cur.fetchone()[0]

        # ------------------Embed--------------------------------
        embed = discord.Embed(
            title=f"{info[0]}'s stats:\t\t\t",
            color=discord.Color.random(),
        )
        embed.set_thumbnail(url=interaction.user.avatar.url)
        embed.add_field(name="✩─────────────✩────────────✩", value="", inline=False)
        embed.add_field(
            name=f"You have gambled {gambled} times:",
            value=f"Amount gambled: {amountGambled}\nAmount Won: {amountWon}\nAmount Lost: {amountLost}",
            inline=False,
        )

        embed.add_field(name="✩─────────────✩────────────✩", value="", inline=False)

        embed.add_field(
            name=f"Since {interaction.user.joined_at.date().ctime()[:10]} of {interaction.user.joined_at.date().ctime()[19:]} you have managed to climb to rank {rank} on the server",
            value=f"Balance: {potatoes}",
            inline=False,
        )
        embed.add_field(name="✩─────────────✩────────────✩", value="", inline=False)

        if messages < 50:
            embed.add_field(
                name=f"You have sent {messages} messages this month in Tatox3's chat",
                value="",
                inline=False,
            )
        elif 50 <= messages < 600:
            embed.add_field(
                name=f"You've been active this month with {messages} messages in Tatox3's chat",
                value="",
                inline=False,
            )
        else:
            embed.add_field(
                name=f"You've chatted up a storm this month, sending {messages} messages in Tatox3's chat is no small feat",
                value="",
                inline=False,
            )

        embed.set_footer(text="Messages reset on the first day of every month.")

        await interaction.followup.send(embed=embed)

    else:
        # ------------------Info--------------------------------
        cur.execute(
            f"SELECT TwitchName, TwitchID FROM Economy WHERE DiscordID = {member.id}"
        )
        info = cur.fetchone()

        # ------------------Gambling----------------------------

        cur.execute(f"SELECT * FROM Gambling WHERE DiscordID = {member.id}")
        gambleStats = cur.fetchone()
        if gambleStats is None:
            gambled = 0
            amountGambled = 0
            amountWon = 0
            amountLost = 0
        else:
            gambled = gambleStats[2]
            amountGambled = gambleStats[3]
            amountWon = gambleStats[4]
            amountLost = gambleStats[5]

        # ------------------Economy-----------------------------

        cur.execute(f"SELECT Potatoes FROM Economy WHERE DiscordID = {member.id}")
        economyStats = cur.fetchone()
        potatoes = economyStats[0]
        cur.execute(f"SELECT DiscordID, Potatoes FROM Economy ORDER BY Potatoes DESC")
        result = cur.fetchall()
        count = 0
        rank = 0
        for i in result:
            if i[0] == member:
                rank = count
            else:
                count += 1

        # ------------------Activity----------------------------

        cur.execute(f"SELECT Potatoes FROM Activity WHERE TwitchID = {info[1]}")
        messages = cur.fetchone()
        if messages is None:
            messages = 0
        else:
            messages = messages[0]

        # ------------------Embed----------------------------
        embed = discord.Embed(
            title=f"{info[0]}'s stats:\t\t\t",
            color=discord.Color.random(),
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="✩─────────────✩────────────✩", value="", inline=False)
        embed.add_field(
            name=f"They have gambled {gambled} times:",
            value=f"Amount gambled: {amountGambled}\nAmount Won: {amountWon}\nAmount Lost: {amountLost}",
            inline=False,
        )

        embed.add_field(name="✩─────────────✩────────────✩", value="", inline=False)

        embed.add_field(
            name=f"Since {member.joined_at.date().ctime()[:10]} of {member.joined_at.date().ctime()[19:]} they have managed to climb to rank {count} on the server",
            value=f"Balance: {potatoes}",
            inline=False,
        )
        embed.add_field(name="✩─────────────✩────────────✩", value="", inline=False)
        if messages < 50:
            embed.add_field(
                name=f"They have sent {messages} messages this month in Tatox3's chat",
                value="",
                inline=False,
            )
        elif 50 <= messages < 600:
            embed.add_field(
                name=f"They've been active this month with {messages} messages in Tatox3's chat",
                value="",
                inline=False,
            )
        else:
            embed.add_field(
                name=f"They've chatted up a storm this month, sending {messages} messages in Tatox3's chat is no small feat",
                value="",
                inline=False,
            )

        embed.set_footer(text="Messages reset on the first day of every month.")

        await interaction.followup.send(embed=embed)


@bot.tree.command(name="glb", description="Leaderboards for all the gambling done!")
@app_commands.default_permissions(administrator=True)
async def glb(interaction: discord.Interaction):
    cur.execute(
        f"SELECT TwitchID, DiscordID, Gambled FROM Gambling ORDER BY Gambled DESC LIMIT 5"
    )
    topGamblers = cur.fetchall()
    cur.execute(
        f"SELECT TwitchID, DiscordID, AmountGambled FROM Gambling ORDER BY AmountGambled DESC LIMIT 5"
    )
    bigSpenders = cur.fetchall()
    cur.execute(
        f"SELECT TwitchID, DiscordID, AmountWon FROM Gambling ORDER BY AmountWon DESC LIMIT 5"
    )
    bigWinners = cur.fetchall()
    cur.execute(
        f"SELECT TwitchID, DiscordID, AmountLost FROM Gambling ORDER BY AmountLost DESC LIMIT 5"
    )
    bigLosers = cur.fetchall()
    await interaction.response.defer()
    names = []
    embed = discord.Embed(title="CASINO LEADERBOARD", color=discord.Color.gold())
    embed.set_image(
        url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdWZvbXVvYmdjNW92ZTNua2EwZWRobnV1N2VqMHBlemM2aWk3eWVjcCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/24vTxomgaewVz5ZwPx/giphy.gif"
    )
    for person in topGamblers:
        if person[1] == 0:
            cur.execute(f"SELECT TwitchName FROM Economy WHERE TwitchID = {person[0]}")
            names.append(cur.fetchone()[0])
        else:
            cur.execute(f"SELECT TwitchName FROM Economy WHERE DiscordID = {person[1]}")
            names.append(cur.fetchone()[0])
    gambler = discord.Embed(
        title="Addiction levels:",
        description="Amount of times gambled",
        color=discord.Color.gold(),
    )

    for i in range(len(names)):
        gambler.add_field(
            name=f"#{i+1}. {names[i]} - {topGamblers[i][-1]}\t\t\t\t\t\t\t\t\t\t\t\t ‎",
            value="",
            inline=False,
        )

    names.clear()
    for person in bigSpenders:
        if person[1] == 0:
            cur.execute(f"SELECT TwitchName FROM Economy WHERE TwitchID = {person[0]}")
            names.append(cur.fetchone()[0])
        else:
            cur.execute(f"SELECT TwitchName FROM Economy WHERE DiscordID = {person[1]}")
            names.append(cur.fetchone()[0])
    spenders = discord.Embed(
        title="Big Time Ballers:",
        description="Amount of money gambled",
        color=discord.Color.gold(),
    )

    for i in range(len(names)):
        spenders.add_field(
            name=f"#{i+1}. {names[i]} - {bigSpenders[i][-1]}\t\t\t\t\t\t\t\t ‎",
            value="",
            inline=False,
        )

    names.clear()
    for person in bigWinners:
        if person[1] == 0:
            cur.execute(f"SELECT TwitchName FROM Economy WHERE TwitchID = {person[0]}")
            names.append(cur.fetchone()[0])
        else:
            cur.execute(f"SELECT TwitchName FROM Economy WHERE DiscordID = {person[1]}")
            names.append(cur.fetchone()[0])
    winners = discord.Embed(
        title="Swag levels:",
        description="Amount of money won",
        color=discord.Color.gold(),
    )

    for i in range(len(names)):
        winners.add_field(
            name=f"#{i+1}. {names[i]} - {bigWinners[i][-1]}\t\t\t\t\t\t\t\t ‎",
            value="",
            inline=False,
        )

    names.clear()

    for person in bigLosers:
        if person[1] == 0:
            cur.execute(f"SELECT TwitchName FROM Economy WHERE TwitchID = {person[0]}")
            names.append(cur.fetchone()[0])
        else:
            cur.execute(f"SELECT TwitchName FROM Economy WHERE DiscordID = {person[1]}")
            names.append(cur.fetchone()[0])
    losers = discord.Embed(
        title="Homelessness levels:",
        description="Amount of money lost",
        color=discord.Color.gold(),
    )

    for i in range(len(names)):
        losers.add_field(
            name=f"#{i+1}. {names[i]} - {bigLosers[i][-1]} \t\t\t\t\t\t\t\t\t\t\t ‎",
            value="",
            inline=False,
        )

    names.clear()

    await interaction.followup.send(
        embeds=[
            embed,
            gambler,
            spenders,
            winners,
            losers,
        ]
    )


# LATER
@bot.tree.command(name="slots", description="Slot machine!")
@app_commands.default_permissions(administrator=True)
async def slots(interaction: discord.Interaction, amount: int):
    emoji = random.choice(["🍇", "🍉", "🍎", "🍌", "🍓", "🥥", "🥔"])
    embed = discord.Embed(title="Slot Machine!")
    embed.add_field(
        name="S1\t\t\tS2\t\t\tS3\t\t\tS4\t\t\tS5", value=f"{emoji}\t\t\t{emoji}"
    )
    embed.set_thumbnail(url=interaction.user.avatar.url)
    await interaction.response.send_message(embed=embed)

    # time.sleep(0.2) best timing


bot.run("MTExMjQ2OTY4MDU5NTE1MjkxNw.GeAxW5.0TTdElhqfViY_zle-Z_RdBudns_YckUFfHXLn8")
# -------------------------------------------------------------------#
