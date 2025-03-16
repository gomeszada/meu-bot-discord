import discord
import random
from discord.ext import commands, tasks
import datetime
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Lista de canais permitidos
CANAL_PERMITIDO_IDS = [1350908011060924416, 1350937589213040680]
usuarios_geraram = {}  # Dicionário para controlar o limite diário
ESTOQUE_ARQUIVO = "estoque.txt"  # Arquivo para armazenar as contas

# Função para carregar contas do arquivo
def carregar_contas():
    if os.path.exists(ESTOQUE_ARQUIVO):
        with open(ESTOQUE_ARQUIVO, "r", encoding="utf-8") as f:
            return [linha.strip() for linha in f.readlines()]
    return []

# Função para salvar contas no arquivo
def salvar_contas(contas):
    with open(ESTOQUE_ARQUIVO, "w", encoding="utf-8") as f:
        f.write("\n".join(contas) + "\n")

contas = carregar_contas()  # Carrega as contas ao iniciar o bot

@tasks.loop(hours=24)
async def resetar_contagem_diaria():
    usuarios_geraram.clear()
    print("Contagens diárias resetadas.")

@bot.event
async def on_ready():
    print(f'Bot {bot.user} está online!')
    resetar_contagem_diaria.start()

@bot.command()
async def genrock(ctx):
    if ctx.channel.id not in CANAL_PERMITIDO_IDS:
        await ctx.send(
            f'{ctx.author.mention}, este comando só pode ser usado nos canais permitidos!'
        )
        return

    user_id = ctx.author.id
    hoje = datetime.date.today()

    if user_id not in usuarios_geraram:
        usuarios_geraram[user_id] = {'contagem': 0, 'data': hoje}

    usuario = usuarios_geraram[user_id]

    if usuario['data'] != hoje:
        usuario['contagem'] = 0
        usuario['data'] = hoje

    if usuario['contagem'] >= 5:
        await ctx.send(
            f'{ctx.author.mention}, você já gerou 5 contas hoje. Tente novamente amanhã!'
        )
        return

    if not contas:
        await ctx.send(
            f'{ctx.author.mention}, não há mais contas disponíveis no estoque.'
        )
        return

    conta_aleatoria = contas.pop(0)  # Remove a primeira conta da lista
    salvar_contas(contas)  # Atualiza o arquivo removendo a conta usada

    try:
        await ctx.author.send(conta_aleatoria)
        usuario['contagem'] += 1
        await ctx.send(
            f'{ctx.author.mention}, eu te enviei uma conta no privado! verifique!.'
        )
    except discord.Forbidden:
        await ctx.send(
            f'{ctx.author.mention}, não consegui te enviar a conta no privado. Talvez você tenha bloqueado mensagens privadas.'
        )

    if not contas:
        await ctx.send(
            "O estoque de contas acabou. Não há mais contas disponíveis no momento."
        )

@bot.command()
async def estoque(ctx, action: str = None, *, conta: str = None):
    owner_id = 576198819918774283  # Seu ID do Discord
    if ctx.author.id != owner_id:
        await ctx.send("Você não tem permissão para usar este comando.")
        return

    if action is None:
        await ctx.send(
            "Use: `!estoque ver`, `!estoque adicionar [conta]`, ou `!estoque remover [conta]`."
        )
        return

    if action == 'ver':
        if not contas:
            await ctx.send("O estoque de contas está vazio.")
        else:
            await ctx.send(f"Contas no estoque:\n" + "\n".join(contas))

    elif action == 'adicionar' and conta:
        contas.append(conta)
        salvar_contas(contas)
        await ctx.send(f"A conta foi adicionada ao estoque:\n{conta}")

    elif action == 'remover' and conta:
        if conta in contas:
            contas.remove(conta)
            salvar_contas(contas)
            await ctx.send(f"A conta foi removida do estoque:\n{conta}")
        else:
            await ctx.send("Essa conta não está no estoque.")

    else:
        await ctx.send("Comando inválido ou parâmetros ausentes.")

# Inicia o bot
TOKEN = os.getenv('MTM1MDkwMDU2NTAwNTA0NTk1Mg.Gxwz80.DgpWzFFk-UxX2p0n4kxZNvqMChtTP7WzGrW9cI')
if TOKEN:
    bot.run(TOKEN)
else:
    print("Token não encontrado. Verifique o arquivo .env.")
