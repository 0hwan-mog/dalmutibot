import discord
from discord.ext import commands, tasks
import os

from dotenv import load_dotenv

#.env 파일 변수 불러오기
load_dotenv()

bot_token = os.getenv("bot_token")
if bot_token is None:
    raise ValueError("봇 토큰이 .env 파일에 설정되지 않았습니다.")

# 권한 설정
intents = discord.Intents.default()
intents.all()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

welcome_channel_id = 1166665557240729640 #환영 채널 id

@bot.event #봇 시작
async def on_ready():
    await bot.change_presence(status=discord.Status.online)
    print(f'봇이 {bot.user.name}로 로그인했습니다!')

@bot.command() #ping
async def ping(ctx):
    await ctx.send('pong!')
    print("명령어 수신")

@bot.event #키워드 응답
async def on_message(message):
    # 메시지 작성자가 봇 자신인 경우 무시
    if message.author.bot:
        # 봇이 보낸 메시지이므로 무시
        return

    # 메시지 내용에 '테스트' 키워드가 포함된 경우
    if '테스트' in message.content:
        print(f"테스트 메시지 수신: {message.author.name} - {message.content}")
        await message.channel.send('테스트중입니다')

    # 다른 메시지의 경우
    else:
        print(f"무시된 메시지: {message.author.name} - {message.content}")
    # 명령어 처리
    await bot.process_commands(message)

@bot.event #신규 사용자 환영 메시지
async def on_member_join(member):
    # 환영 메시지를 보낼 채널을 가져옵니다
    channel = member.guild.get_channel(welcome_channel_id)
    
    # 환영 메시지를 보냅니다
    await channel.send(f'환영합니다, {member.mention}님! 서버에 참여해주셔서 감사합니다.')


# 봇을 실행
bot.run(bot_token)  # 봇 토큰을 여기에 입력

