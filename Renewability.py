# -*- coding: utf-8 -*-
import json
import os
import time
from mcdreforged.api.all import *

PLUGIN_METADATA = {
    'id': 'renewability',
    'version': '1.0.0',
    'name': 'Renewability',
    'description': 'A plugin that allows players to clone non-renewable items.',
    'author': 'Fidel Yin',
    'link': 'https://github.com/Fidelxyz/',
    'dependencies': {
        'mcdreforged': '>=1.0.0',
        'minecraft_data_api': '*',
    }
}

Prefix = '!!clone'
MsgPrefix = f'[{PLUGIN_METADATA["name"]}] '
HelpMessage = '''
------ {1} v{2} ------
一个允许玩家§a复制§c不可再生物品§r的插件
§d【格式说明】§r
§7{0} §r复制手中物品
§7{0} help §r查看帮助
§7{0} query §r查询今日剩余复制次数
§7{0} list §r查看可复制的物品列表
'''.strip().format(Prefix, PLUGIN_METADATA['name'], PLUGIN_METADATA['version'])

# Data
DATA_DIRECTORY = './plugins/Renewability/'
DATA_FILE = DATA_DIRECTORY + 'RenewabilityData.json'
data = {
    'version': '',
    'players_data': {}
}

# Config
CONFIG_FILE = './config/Renewability.json'
config = {
    'max_daily_items_cloned': 1,
    'allowed_items_list': [
        'minecraft:elytra',
        'minecraft:enchanted_golden_apple',
        'minecraft:sponge'
    ]
}
default_config = config.copy()


def msg(content: str):
    return MsgPrefix + content


def get_day():
    return time.strftime("%Y-%m-%d", time.localtime(time.time()))


def list_allowed_items(server, info):
    global config
    msg_content = msg('允许复制的物品列表：')
    for item in config['allowed_items_list']:
        msg_content += f'\n-§7 {item} §a'
    server.reply(info, msg_content)


def query_counter(server, player):
    global data, config
    max_counter = config["max_daily_items_cloned"]
    player_data = data['players_data'][player]
    remaining_counter = max_counter
    if player_data['last_cloning_day'] == get_day():
        remaining_counter -= player_data['cloning_counter']
    server.tell(player, msg(f'今日剩余可复制次数：§a{remaining_counter}§r/§e{max_counter}§r'))


# Ref: https://github.com/TISUnion/QuickBackupM/blob/master/QuickBackupM.py
def load_config(server):
    global config
    try:
        config = {}
        with open(CONFIG_FILE) as file:
            js = json.load(file)
        for key in default_config.keys():
            config[key] = js[key]
        server.logger.info(msg('Config file loaded'))
    except Exception as e:
        server.logger.info(msg('Fail to read config file, using default value'))
        server.logger.debug(e)
        config = default_config
        with open(CONFIG_FILE, 'w+') as file:
            json.dump(config, file, indent=4)


def load_data(server):
    global data
    if not os.path.isfile(DATA_FILE):  # Data file not found
        try:
            os.makedirs(DATA_DIRECTORY)
            server.logger.info(msg('Data directory created'))
        except Exception as e:
            server.logger.warning(msg('Error occurred while creating data directory'))
            server.logger.debug(e)
    else:  # Data file found
        try:
            with open(DATA_FILE) as file:
                data = json.load(file, encoding='utf8')
                server.logger.info(msg('Data file loaded'))
        except Exception as e:
            server.logger.warning(msg('Error occurred while loading Json data file'))
            server.logger.debug(e)
            return
    data['version'] = PLUGIN_METADATA['version']
    save_data(server)


def save_data(server):
    global data
    try:
        with open(DATA_FILE, 'w+') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        server.logger.warning(msg('Error occurred while saving Json data file'))
        server.logger.debug(e)
        return


def update_last_cloning_day(server, player):
    global data
    now_day = get_day()
    print(now_day)
    player_data = data['players_data'][player]
    if player_data['last_cloning_day'] == now_day:
        player_data['cloning_counter'] += 1
    else:
        player_data['cloning_counter'] = 1
        player_data['last_cloning_day'] = now_day
    save_data(server)


def is_clone_allowed(server, player, item):
    global data, config

    if not item:
        server.tell(player, msg('§c当前主手上无物品§r'))
        return False

    if item['id'] not in config['allowed_items_list']:
        server.tell(player, msg('§c该物品不允许复制§r'))
        return False

    player_data = data['players_data'][player]
    if player_data['last_cloning_day'] == get_day() and player_data['cloning_counter'] >= config[
        'max_daily_items_cloned']:
        server.tell(player, msg('§c今日复制次数已达上限§r'))
        query_counter(server, player)
        return False

    return True


def get_item(server, player):
    MCDataAPI = server.get_plugin_instance('minecraft_data_api')
    try:
        item = MCDataAPI.get_player_info(player, 'SelectedItem', timeout=1)
        return item if type(item) == dict else None
    except Exception as e:
        server.logger.warning(msg('Error occurred while getting item'))
        server.logger.debug(e)
        return None


@new_thread(PLUGIN_METADATA['name'])
def clone_item(server, player):
    item = get_item(server, player)
    if is_clone_allowed(server, player, item):
        item_id = item['id']
        server.execute(f'give {player} {item_id}')
        update_last_cloning_day(server, player)
        server.tell(player, msg(f'§a物品§7 {item_id} §a复制成功§r'))
        query_counter(server, player)
        server.logger.info(msg(f'{player} cloned an item {item_id}'))


def on_info(server, info):
    if info.content.startswith(Prefix):
        command = info.content.split()
        if len(command) == 1 and info.is_user:
            clone_item(server, info.player)
        elif command[1] == 'help':
            server.reply(info, HelpMessage)
        elif command[1] == 'query' and info.is_user:
            query_counter(server, info.player)
        elif command[1] == 'list':
            list_allowed_items(server, info)
        else:
            server.reply(info, msg('§c参数错误§r'))


def on_load(server, old):
    load_config(server)
    load_data(server)
    server.register_help_message(Prefix, "复制手中的不可再生物品")


def on_player_joined(server, player, info):
    global data
    if player not in data['players_data'].keys():
        data['players_data'][player] = {'last_cloning_day': '', 'cloning_counter': 0}
        save_data(server)
