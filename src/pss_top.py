#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
import discord
import discord.ext.commands as commands
from typing import List, Tuple

from discord.utils import escape_markdown

import emojis
import pss_assert
import pss_core as core
import pss_entity as entity
import pss_fleet as fleet
import pss_login as login
import pss_lookups as lookups
import pss_tournament as tourney
import settings
import utility as util


# ---------- Constants ----------

TOP_FLEETS_BASE_PATH = f'AllianceService/ListAlliancesByRanking?skip=0&take='
STARS_BASE_PATH = f'AllianceService/ListAlliancesWithDivision'

ALLOWED_DIVISION_LETTERS = sorted([letter for letter in lookups.DIVISION_CHAR_TO_DESIGN_ID.keys() if letter != '-'])










# ---------- Helper functions ----------

def is_valid_division_letter(div_letter: str) -> bool:
    if div_letter is None:
        result = True
    else:
        result = div_letter.lower() in [letter.lower() for letter in ALLOWED_DIVISION_LETTERS]
    return result



async def get_top_captains_dict(skip: int = 0, take: int = 100) -> dict:
    path = await _get_top_captains_path(skip, take)
    raw_data = await core.get_data_from_path(path)
    data = core.xmltree_to_dict3(raw_data)
    return data










# ---------- Top 100 Alliances ----------

async def get_top_fleets(ctx: commands.Context, take: int = 100, as_embed: bool = settings.USE_EMBEDS):
    tourney_running = tourney.is_tourney_running()
    raw_data = await core.get_data_from_path(TOP_FLEETS_BASE_PATH + str(take))
    data = core.xmltree_to_dict3(raw_data)
    if data:
        title = f'Top {take} fleets'
        prepared_data = __prepare_top_fleets(data)
        if tourney_running:
            body_lines = [f'**{position}.** {fleet_name} ({trophies} {emojis.trophy} - {stars} {emojis.star})' for position, fleet_name, trophies, stars in prepared_data]
        else:
            body_lines = [f'**{position}.** {fleet_name} ({trophies} {emojis.trophy})' for position, fleet_name, trophies, _ in prepared_data]

        if as_embed:
            body = '\n'.join(body_lines)
            colour = util.get_bot_member_colour(ctx.bot, ctx.guild)
            result = util.create_embed(title, description=body, colour=colour)
            return [result], True
        else:
            result = [f'**{title}**']
            result.extend(body_lines)
            return result, True
    else:
        return ['An unknown error occured. Please contact the bot\'s author!'], False


def __prepare_top_fleets(alliance_data: entity.EntitiesData) -> List[Tuple]:
    result = [(position, discord.utils.escape_markdown(alliance_info[fleet.FLEET_DESCRIPTION_PROPERTY_NAME]), alliance_info['Trophy'], alliance_info['Score']) for position, alliance_info in enumerate(alliance_data.values(), start=1)]
    return result










# ---------- Top 100 Captains ----------

async def get_top_captains(take: int = 100, as_embed: bool = settings.USE_EMBEDS):
    data = await get_top_captains_dict(0, take)
    if as_embed:
        return _get_top_captains_as_embed(data, take), True
    else:
        return _get_top_captains_as_text(data, take), True


def _get_top_captains_as_embed(captain_data: dict, take: int = 100):
    return ''


def _get_top_captains_as_text(captain_data: dict, take: int = 100):
    headline = f'**Top {take} captains**'
    lines = [headline]

    position = 0
    for entry in captain_data.values():
        position += 1
        name = util.escape_markdown(entry['Name'])
        trophies = entry['Trophy']
        fleet_name = entry['AllianceName']

        trophy_txt = f'{trophies} {emojis.trophy}'

        line = f'**{position}.** {name} ({fleet_name}): {trophy_txt}'
        lines.append(line)
        if position == take:
            break

    return lines


async def _get_top_captains_path(skip: int, take: int):
    skip += 1
    access_token = await login.DEVICES.get_access_token()
    result = f'LadderService/ListUsersByRanking?accessToken={access_token}&from={skip}&to={take}'
    return result










# ---------- Stars info ----------

async def get_division_stars(division: str = None, fleet_data: dict = None, retrieved_date: datetime = None, as_embed: bool = settings.USE_EMBEDS):
    if division:
        pss_assert.valid_parameter_value(division, 'division', min_length=1, allowed_values=ALLOWED_DIVISION_LETTERS)
        if division == '-':
            division = None
    else:
        division = None

    if fleet_data is None or retrieved_date is None:
        data = await core.get_data_from_path(STARS_BASE_PATH)
        fleet_infos = core.xmltree_to_dict3(data)
    else:
        fleet_infos = fleet_data

    divisions = {}
    if division:
        division_design_id = lookups.DIVISION_CHAR_TO_DESIGN_ID[division.upper()]
        divisions[division.upper()] = [fleet_info for fleet_info in fleet_infos.values() if fleet_info['DivisionDesignId'] == division_design_id]
        pass
    else:
        for division_design_id in lookups.DIVISION_DESIGN_ID_TO_CHAR.keys():
            if division_design_id != '0':
                division_letter = lookups.DIVISION_DESIGN_ID_TO_CHAR[division_design_id]
                divisions[division_letter] = [fleet_info for fleet_info in fleet_infos.values() if fleet_info['DivisionDesignId'] == division_design_id]

    if divisions:
        result = []
        for division_letter, fleet_infos in divisions.items():
            result.extend(_get_division_stars_as_text(division_letter, fleet_infos))
            result.append(settings.EMPTY_LINE)
        if result:
            result = result[:-1]
            if retrieved_date is not None:
                result.append(util.get_historic_data_note(retrieved_date))
        return result, True
    else:
        return [], False


def _get_division_stars_as_embed(division_letter: str, fleet_infos: dict):
    return ''


def _get_division_stars_as_text(division_letter: str, fleet_infos: list) -> list:
    lines = [f'__**Division {division_letter.upper()}**__']
    fleet_infos = util.sort_entities_by(fleet_infos, [('Score', int, True)])
    fleet_infos_count = len(fleet_infos)
    for i, fleet_info in enumerate(fleet_infos, start=1):
        fleet_name = util.escape_markdown(fleet_info['AllianceName'])
        if 'Trophy' in fleet_info.keys():
            trophies = fleet_info['Trophy']
            trophy_str = f' ({trophies} {emojis.trophy})'
        else:
            trophy_str = ''
        stars = fleet_info['Score']
        if i < fleet_infos_count:
            difference = int(stars) - int(fleet_infos[i]['Score'])
        else:
            difference = 0
        lines.append(f'**{i:d}.** {stars} (+{difference}) {emojis.star} {fleet_name}{trophy_str}')
    return lines