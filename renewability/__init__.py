# -*- coding: utf-8 -*-
import json
import os
import time
from mcdreforged.api.all import *

Prefix = '!!clone'
MsgPrefix = '[{0}] '
HelpMessage = '''
------ {1} v{2} ------
一个允许玩家§a复制§c不可再生物品§r的插件
§d【格式说明】§r
§7{0} §r复制手中物品
§7{0} help §r查看帮助
§7{0} query §r查询今日剩余复制次数
§7{0} list §r查看可复制的物品列表
'''.strip()
# {0} = Prefix
# {1} = PLUGIN_METADATA.name
# {2} = PLUGIN_METADATA.version

PLUGIN_METADATA = Metadata({'id': 'renewability'})

# Data
DATA_FILE = ''
data = {
    'version': '',
    'players_data': {}
}
default_data = data

# Config
CONFIG_FILE = ''
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
    return time.strftime('%Y-%m-%d', time.localtime(time.time()))


# Ref: https://github.com/TISUnion/QuickBackupM/blob/master/QuickBackupM.py
def load_config(server):
    global config
    try:
        config = {}
        with open(CONFIG_FILE) as file:
            js = json.load(file)
        for key in default_config.keys():
            config[key] = js[key]
        server.logger.info('Config file loaded')
    except Exception as e:
        server.logger.info('Fail to read config file, using default value')
        server.logger.debug(e)
        config = default_config
        try:
            with open(CONFIG_FILE, 'w+') as file:
                json.dump(config, file, indent=4)
        except Exception as e:
            server.logger.error('Error occurred while creating config file')
            server.logger.error(e)



def load_data(server):
    global data
    try:
        data = {}
        with open(DATA_FILE) as file:
            js = json.load(file)
        for key in default_data.keys():
            data[key] = js[key]
        server.logger.info('Data file loaded')
    except Exception as e:
        server.logger.info('Fail to read data file, using default value')
        server.logger.debug(e)
        data = default_data
        try:
            with open(DATA_FILE, 'w+') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            server.logger.error('Error occurred while creating config file')
            server.logger.error(e)
    data['version'] = str(PLUGIN_METADATA.version)
    save_data(server)


def save_data(server):
    global data
    try:
        with open(DATA_FILE, 'w+') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        server.logger.error('Error occurred while saving Json data file')
        server.logger.error(e)
        return


def list_allowed_items(source):
    global config
    msg_content = msg('允许复制的物品列表：')
    for item in config['allowed_items_list']:
        msg_content += f'\n§a-§7 {item} §r'
    source.reply(msg_content)


def query_counter(source):
    if not source.is_player:
        source.reply(msg('§c不可在 Console 中使用§r'))
        return
    server = source.get_server()
    player = source.get_info().player
    max_counter = config['max_daily_items_cloned']
    player_data = data['players_data'][player]
    remaining_counter = max_counter
    if player_data['last_cloning_day'] == get_day():
        remaining_counter -= player_data['cloning_counter']
    source.reply(msg(f'今日剩余可复制次数：§a{remaining_counter}§r/§e{max_counter}§r'))


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


def is_clone_allowed(source, player, item):
    global data, config

    if not item:
        source.reply(msg('§c当前主手上无物品§r'))
        return False

    if item['id'] not in config['allowed_items_list']:
        source.reply(msg('§c该物品不允许复制§r'))
        return False

    player_data = data['players_data'][player]
    if player_data['last_cloning_day'] == get_day() and player_data['cloning_counter'] >= config[
        'max_daily_items_cloned']:
        source.reply(msg('§c今日复制次数已达上限§r'))
        query_counter(source)
        return False

    return True


def get_item(server, player):
    MCDataAPI = server.get_plugin_instance('minecraft_data_api')
    try:
        item = MCDataAPI.get_player_info(player, 'SelectedItem', timeout=1)
        return item if type(item) == dict else None
    except Exception as e:
        server.logger.error('Error occurred while getting item')
        server.logger.error(e)
        return None


@new_thread(PLUGIN_METADATA.name)
def clone_item(source):
    if not source.is_player:
        source.reply(msg('§c不可在 Console 中使用§r'))
        return
    server = source.get_server()
    player = source.get_info().player
    item = get_item(server, player)
    if is_clone_allowed(source, player, item):
        item_id = item['id']
        server.execute(f'give {player} {item_id}')
        update_last_cloning_day(server, player)
        source.reply(msg(f'§a物品§7 {item_id} §a复制成功§r'))
        query_counter(server, player)
        server.logger.info(f'{player} cloned an item {item_id}')


def on_load(server, old):
    global PLUGIN_METADATA, DATA_FILE, CONFIG_FILE, MsgPrefix, HelpMessage
    PLUGIN_METADATA = server.get_self_metadata()
    DATA_FILE = os.path.join(server.get_data_folder(), 'data.json')
    CONFIG_FILE = os.path.join(server.get_data_folder(), 'config.json')
    MsgPrefix = MsgPrefix.format(PLUGIN_METADATA.name)
    HelpMessage = HelpMessage.format(Prefix, PLUGIN_METADATA.name, PLUGIN_METADATA.version)
    server.register_help_message(Prefix, '复制手中的不可再生物品')
    server.register_command(
        Literal(Prefix). \
        then(Literal('help').runs(lambda source: source.reply(HelpMessage))). \
        then(Literal('list').runs(list_allowed_items)). \
        then(Literal('query').runs(query_counter)). \
        runs(clone_item)
    )
    load_config(server)
    load_data(server)


def on_player_joined(server, player, info):
    global data
    if player not in data['players_data'].keys():
        data['players_data'][player] = {'last_cloning_day': '', 'cloning_counter': 0}
        save_data(server)
