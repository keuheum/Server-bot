import os
import math
import psutil
import cpuinfo
import asyncio
import discord
import datetime
import platform
import traceback
from discord.ext import commands
from discord.ext.tasks import loop
from time import strftime, localtime, time

##########################################봇 기본 선언##########################################
INTENTS = discord.Intents.default()
bot = commands.Bot(command_prefix=".", intents=INTENTS)

bot_start_time = datetime.datetime.utcnow()

##########################################함수##########################################
def get_uptime():
  uptime = datetime.datetime.utcnow() - bot_start_time
  uptime = str(uptime).split(":")
  hours = uptime[0]
  hours = hours.replace(" days,", "일")
  hours = hours.replace(" day,", "일")
  minitues = uptime[1]
  seconds = uptime[2]
  seconds = seconds.split(".")
  seconds = seconds[0]
  return {
    "hours" : hours,
    "minitues" : minitues,
    "seconds" : seconds
  }
  
def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

async def log_msg(msg):
  await bot.get_channel(880050941632606268).send(f"> `{strftime('%Z %Y-%m-%d %H:%M:%S', localtime(time()))}`\n{msg}")

@loop(count=None, seconds=60)
async def send_message():
  memory_usage_dict = dict(psutil.virtual_memory()._asdict())
  net = psutil.net_io_counters()
  await bot.get_channel(880050941632606268).send(
    f"""
    > `{strftime('%Z %Y-%m-%d %H:%M:%S', localtime(time()))}`
CPU 사용량: {psutil.cpu_percent()}%\n램 사용량: {memory_usage_dict['percent']}%
인터넷: Sent: {round(net.bytes_sent/1024**2, 1)}MB, Recv: {round(net.bytes_recv/1024**2, 1)}MB
    """)
  
##########################################on_ready##########################################
@bot.event
async def on_ready():
  bot.owner_ids = [604983644733440001]
  await log_msg(f"bot is started")
  send_message.start()

##########################################소유자용##########################################
@bot.command(name="정지", aliases=["중지", "stop"])
@commands.is_owner()
async def stop_bot(ctx):
  await ctx.send("봇을 정지합니다")
  await log_msg(f"bot is stoped by {ctx.message.author}")
  exit()

@bot.command(name="종료")
@commands.is_owner()
async def stop_com(ctx):
  await ctx.send("컴퓨터를 종료합니다.")
  await log_msg(f"computer is stoped by {ctx.message.author}")
  os.system('shutdown -h now')

@bot.command(name="리셋", aliases=["reset"])
@commands.is_owner()
async def reset(ctx):
  await ctx.send("컴퓨터를 리셋합니다.")
  await log_msg(f"computer is reseted by {ctx.message.author}")
  os.system('shutdown -r now')

@bot.command(name="소유자-추가", aliases=["소추"])
@commands.is_owner()
async def add_owner(ctx, user_id):
  bot.owner_ids.append(int(user_id))
  await ctx.send(f"소유자에 아이디({user_id})를 추가했습니다.")

@bot.command(name="소유자-삭제", aliases=["소삭"])
@commands.is_owner()
async def delete_owner(ctx, user_id):
  try:
    bot.owner_ids.remove(int(user_id))
  except ValueError:
    await ctx.send("해당 아이디의 소유자는 존재하지 않습니다.")
  except Exception as e:
    await ctx.send(f"`오류 발생`\n{e}")
  else:
    await ctx.send(f"소유자에 아이디({user_id})를 삭제했습니다.")

@bot.command(name="소유자-확인", aliases=["소확"])
@commands.is_owner()
async def see_owner(ctx):
  await ctx.send(bot.owner_ids)

@bot.command(name="이블", aliases=["exec"])
@commands.is_owner()
async def exec_owner(ctx, _exec):
  i = exec(f"""
  {_exec}
  """)
  await ctx.send(f"실행결과: {i}")

##########################################유저용##########################################
@bot.command(name="업타임", aliases=["uptime", "ㅇㅌㅇ", "dxd"])
async def uptime(ctx):
    embed = discord.Embed(
        title="업타임",
        description="%s시간 %s분 %s초"
        % (get_uptime()["hours"], get_uptime()["minitues"], get_uptime()["seconds"]),
        color=0x2F3136,
        timestamp=datetime.datetime.utcnow()
    )
    await ctx.reply(embed=embed, mention_author=False)

@bot.command(name="정보", aliases=["info", "ㅈㅂ", "wq"])
async def uptime(ctx):
  memory_usage_dict = dict(psutil.virtual_memory()._asdict())
  net = psutil.net_io_counters()
  embed = discord.Embed(
       title="서버 정보",
       color=0x2F3136,
       timestamp=datetime.datetime.utcnow())
  embed.add_field(name="OS", value=platform.system(), inline=True)
  embed.add_field(name="OS Version", value=platform.version(), inline=True)
  embed.add_field(name="가동시간", value=f'{get_uptime()["hours"]}시간 {get_uptime()["minitues"]}분 {get_uptime()["seconds"]}초')
  for disk in psutil.disk_partitions():
      if disk.fstype:
        embed.add_field(
          name=f"{disk.device[0]}드라이브", 
          value=f"용량: {convert_size(psutil.disk_usage(disk.mountpoint)[0])}\n사용량: {psutil.disk_usage(disk.mountpoint)[3]}%", 
          inline=True
          )
  embed.add_field(name="­", value="­", inline=True)#2개의 하드가 있어서 이쁘게 하려고 공백문자를 넣었습니다
  embed.add_field(name="램 용량", value=str(round(psutil.virtual_memory().total / (1024.0 **3)))+"GB", inline=True)
  embed.add_field(name="남은 램 용량", value=f"{convert_size(memory_usage_dict['available'])}", inline=True)
  embed.add_field(name="램 사용량", value=f"{memory_usage_dict['percent']}%", inline=True)
  embed.add_field(name="CPU 정보", value=f"이름: {cpuinfo.get_cpu_info()['brand_raw']}\n코어: {os.cpu_count()}\n비트: {cpuinfo.get_cpu_info()['bits']}bits", inline=True)
  #위 코드에서 시간 소모가 많아, 빠르게 임베드가 나오게 하고싶다면, 실시간이 아닌 미리 내용을 적어두세요
  embed.add_field(name="CPU 사용량", value=f"{psutil.cpu_percent()}%", inline=True)
  embed.add_field(name="네크워크", value=f"Sent: {round(net.bytes_sent/1024**2, 1)}MB\nRecv: {round(net.bytes_recv/1024**2, 1)}MB", inline=True)

  await ctx.reply(embed=embed, mention_author=False)
##########################################에러##########################################
@bot.event
async def on_command_error(ctx, error):
  await ctx.send(f"오류 발생\n{error}")
  tb = traceback.format_exception(type(error), error, error.__traceback__)
  err = [line.rstrip() for line in tb]
  errstr = '\n'.join(err)
  await log_msg(f"<@!your id> , 에러 발생\n{errstr}")

bot.run("your bot token")
