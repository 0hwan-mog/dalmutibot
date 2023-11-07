import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import asyncio
import random
import json
import datetime


#.env 파일 환경변수 불러오기
load_dotenv()

bot_token = os.getenv("bot_token")
if bot_token is None:
    raise ValueError("봇 토큰이 .env 파일에 설정되지 않았습니다.")

#봇 권한 설정
intents = discord.Intents.default()
intents.all()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 채널 ID 상수 정의
welcome_channel_id = 1166665557240729640 #환영 채널 id
test_channel_id = 1166631932470251540 #테스트 채널 id




# 유틸리티 함수 정의 부분
# ---------------------------------------------
# 무작위 메시지 목록읽어 오는 함수
def read_random_messages(filename):
    messages = []
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.read().split('\n\n')  # 빈 줄로 메시지를 분리합니다.
        for line in lines:
            parts = line.strip().split('\n', 1)  # 줄바꿈으로 이름과 내용을 분리합니다.
            if len(parts) == 2:
                message_name, message_content = parts
                messages.append((message_name, message_content))
    return messages

# 무작위 메시지 목록을 불러와서 random_messages 변수에 저장
random_messages = read_random_messages('messages.txt')

#랜덤 메시지 발송 함수 정의
async def send_random_message():
    random_message_tuple = random.choice(random_messages)
    channel = bot.get_channel(test_channel_id)
    message_content = random_message_tuple[1]
    if message_content.strip():
        await channel.send(message_content)
        print("랜덤 {} 전송 완료".format(random_message_tuple[0]))

# 파일에서 keyword_responses를 불러오는 함수
def load_keyword_responses(filename):
    keyword_responses = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split(":", 1)
            if len(parts) == 2:
                keyword, response = parts
                keyword_responses[keyword] = response
    return keyword_responses

# 파일에서 불러온 keyword_responses를 keyword_responses 변수에 저장
keyword_responses = load_keyword_responses('keywords.txt')

# JSON 파일에서 명령어 데이터를 로드하는 함수
def load_commands():
    with open('commands.json', 'r') as file:
        return json.load(file)
# 명령어에 대응하는 함수들을 동적으로 생성하는 코드
for command in load_commands()['commands']:
    @bot.command(name=command['name'])
    async def _command(ctx, *args, command=command):  # command 파라미터가 클로저에 바인딩됩니다.
        # 명령어 설명이 리스트 형태인지 문자열 형태인지 확인합니다.
        if isinstance(command['description'], list):
            # 리스트 형태일 경우, 명령어의 설명을 여러 메시지로 나누어 보냅니다.
            response = '\n'.join(command['description'])
        else:
            # 문자열 형태일 경우, 명령어의 설명을 그대로 사용합니다.
            response = command['description']
        await ctx.send(response)
    
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online)
    print(f'봇이 {bot.user.name}(으)로 로그인했습니다!')
    send_random_message_task.start()  # 랜덤 메시지 발송 시작
    send_morning_message.start()

@tasks.loop(hours=24) #하루에 한번씩 랜덤 메시지 발송
async def send_random_message_task():
    print("랜덤 메시지 발송 시작")
    await send_random_message()

@tasks.loop(hours=1)  # 1시간 주기로 실행하며 모닝 메시지 발송 시간인지 확인 후 메시지 전송
async def send_morning_message():
    now = datetime.datetime.now()
    
    # 평일 아침 9시인지 확인
    
    if now.weekday() < 5 and now.hour == 10:
        # 원하는 채널 ID를 넣어주세요
        channel_id = test_channel_id
        channel = bot.get_channel(channel_id)
        
        # 메시지 보내기
        await channel.send("아침 인사")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    for keyword, response in keyword_responses.items():
        if keyword in message.content:
            print(f"{keyword} 메시지 수신: {message.author.name} - {message.content}")
            await message.channel.send(response)

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    channel = member.guild.get_channel(welcome_channel_id)
    await channel.send(f'환영합니다, {member.mention}님! 서버에 참여해주셔서 감사합니다.')
    print('{} 환영메시지 전송'.format(member.mention))

# 봇 실행
bot.run(bot_token)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(bot.start(bot_token))
    except KeyboardInterrupt:
        # 키보드 인터럽트 예외가 발생하면 봇이 로그아웃하고 루프를 종료합니다.
        loop.run_until_complete(bot.logout())
        # 봇의 모든 비동기 작업이 정리되도록 보장합니다.
        loop.close()
        print("봇이 종료되었습니다.")
    except Exception as e:
        # 다른 예외가 발생한 경우에 대한 처리
        print("에러 발생:", e)
    finally:
        loop.close()