from discord import TextChannel as _TextChannel
from discord.ext.commands import command as _command
from discord.ext.commands import group as _command_group
from discord.ext.commands import Context as _Context
from discord.ext.commands import BucketType as _BucketType
from discord.ext.commands import cooldown as _cooldown
import discord.ext.commands.errors as _command_errors

from .base import CogBase as _CogBase
from ..pss_exception import Error as _Error
from .. import settings as _settings
from .. import server_settings as _server_settings
from .. import utils as _utils
from ..yadc_bot import YadcBot as _YadcBot



class SettingsCog(_CogBase, name='Settings'):
    @_command_group(name='settings', brief='Display or change server settings', invoke_without_command=True)
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings(self, ctx: _Context, *args):
        """
        Retrieve settings for this Discord server/guild.
        Set settings for this server using the subcommands 'set' and 'reset'.

        You need the 'Manage Server' permission to use any of these commands.
        This command can only be used on Discord servers/guilds.

        Usage:
        /settings

        Examples:
        /settings - Prints all settings for the current Discord server/guild.
        """

        if ctx.invoked_subcommand is None:
            self._log_command_use(ctx)
            await self._assert_settings_command_valid(ctx)

            _, on_reset = self._extract_dash_parameters(ctx.message.content, args, '--on_reset')
            guild_settings = await _server_settings.GUILD_SETTINGS.get(self.bot, ctx.guild.id)
            full_settings = guild_settings.get_full_settings()
            title = f'Server settings for {ctx.guild.name}'
            note = None if not on_reset else 'Successfully reset all bot settings for this server!'
            output = await _server_settings.get_pretty_guild_settings(ctx, full_settings, title=title, note=note)
            await _utils.discord.reply_with_output(ctx, output)


    @settings.group(name='autodaily', aliases=['daily'], brief='Retrieve auto-daily settings', invoke_without_command=True)
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_get_autodaily(self, ctx: _Context, *args):
        """
        Retrieve the auto-daily setting for this server.

        You need the 'Manage Server' permission to use this command.
        This command can only be used on Discord servers/guilds.

        Usage:
        /settings autodaily
        /settings daily

        Examples:
        /settings autodaily - Prints all auto-daily settings for the current Discord server/guild.
        """

        if ctx.invoked_subcommand is None:
            self._log_command_use(ctx)
            await self._assert_settings_command_valid(ctx)

            _, on_reset = self._extract_dash_parameters(ctx.message.content, args, '--on_reset')
            guild_settings = await _server_settings.GUILD_SETTINGS.get(self.bot, ctx.guild.id)
            full_autodaily_settings = guild_settings.autodaily.get_full_settings()
            title = f'Auto-daily settings for {ctx.guild.name}'
            note = None if not on_reset else 'Successfully reset auto-daily settings for this server!'
            output = await _server_settings.get_pretty_guild_settings(ctx, full_autodaily_settings, title=title, note=note)
            await _utils.discord.reply_with_output(ctx, output)


    @settings_get_autodaily.command(name='channel', aliases=['ch'], brief='Retrieve auto-daily channel')
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_get_autodaily_channel(self, ctx: _Context, *args):
        """
        Retrieve the auto-daily setting for this server.

        You need the 'Manage Server' permission to use this command.
        This command can only be used on Discord servers/guilds.

        Usage:
        /settings autodaily channel
        /settings daily ch

        Examples:
        /settings autodaily ch - Prints the auto-daily channel settings for the current Discord server/guild.
        """
        self._log_command_use(ctx)
        await self._assert_settings_command_valid(ctx)

        _, on_reset, on_set = self._extract_dash_parameters(ctx.message.content, args, '--on_reset', '--on_set')
        guild_settings = await _server_settings.GUILD_SETTINGS.get(ctx.bot, ctx.guild.id)
        full_autodaily_settings = guild_settings.autodaily.get_channel_setting()
        title = f'Auto-daily settings for {ctx.guild.name}'
        note = None
        if on_reset:
            note = 'Successfully reset auto-daily channel for this server!'
        elif on_set:
            note = 'Successfully set auto-daily channel for this server!'
        output = await _server_settings.get_pretty_guild_settings(ctx, full_autodaily_settings, title=title, note=note)
        await _utils.discord.reply_with_output(ctx, output)


    @settings_get_autodaily.command(name='changemode', aliases=['mode'], brief='Retrieve auto-daily mode', hidden=True)
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_get_autodaily_mode(self, ctx: _Context, *args):
        """
        Retrieve the auto-daily setting for this server.

        You need the 'Manage Server' permission to use this command.
        This command can only be used on Discord servers/guilds.

        Usage:
        /settings autodaily changemode
        /settings daily mode

        Examples:
        /settings autodaily mode - Prints the auto-daily change mode settings for the current Discord server/guild.
        """
        self._log_command_use(ctx)
        await self._assert_settings_command_valid(ctx)

        _, on_reset, on_set = self._extract_dash_parameters(ctx.message.content, args, '--on_reset', '--on_set')
        guild_settings = await _server_settings.GUILD_SETTINGS.get(ctx.bot, ctx.guild.id)
        full_autodaily_settings = guild_settings.autodaily.get_changemode_setting()
        title = f'Auto-daily settings for {ctx.guild.name}'
        note = None
        if on_reset:
            note = 'Successfully reset auto-daily mode for this server!'
        elif on_set:
            note = 'Successfully set auto-daily mode for this server!'
        output = await _server_settings.get_pretty_guild_settings(ctx, full_autodaily_settings, title=title, note=note)
        await _utils.discord.reply_with_output(ctx, output)


    @settings.command(name='embed', aliases=['embeds'], brief='Retrieve embed settings')
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_get_embeds(self, ctx: _Context, *args):
        """
        Retrieve the embed setting for this server. It determines, whether the bot output on this server will be served in embeds or in plain text.

        You need the 'Manage Server' permission to use this command.
        This command can only be used on Discord servers/guilds.

        Usage:
        /settings embed
        /settings embeds

        Examples:
        /settings embed - Prints the embed setting for the current Discord server/guild.
        """
        self._log_command_use(ctx)
        await self._assert_settings_command_valid(ctx)

        _, on_reset, on_set = self._extract_dash_parameters(ctx.message.content, args, '--on_reset', '--on_set')
        guild_settings = await _server_settings.GUILD_SETTINGS.get(self.bot, ctx.guild.id)
        full_settings = guild_settings.get_use_embeds_setting()
        title = f'Server settings for {ctx.guild.name}'
        note = None
        if on_reset:
            note = 'Successfully reset embed usage for this server!'
        elif on_set:
            note = 'Successfully toggled embed usage for this server!'
        output = await _server_settings.get_pretty_guild_settings(ctx, full_settings, title=title, note=note)
        await _utils.discord.reply_with_output(ctx, output)


    @settings.command(name='pagination', aliases=['pages'], brief='Retrieve pagination settings')
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_get_pagination(self, ctx: _Context, *args):
        """
        Retrieve the pagination setting for this server. For information on what pagination is and what it does, use this command: /help pagination

        You need the 'Manage Server' permission to use this command.
        This command can only be used on Discord servers/guilds.

        Usage:
        /settings pagination
        /settings pages

        Examples:
        /settings pagination - Prints the pagination setting for the current Discord server/guild.
        """
        self._log_command_use(ctx)
        await self._assert_settings_command_valid(ctx)

        _, on_reset, on_set = self._extract_dash_parameters(ctx.message.content, args, '--on_reset', '--on_set')
        guild_settings = await _server_settings.GUILD_SETTINGS.get(self.bot, ctx.guild.id)
        full_settings = guild_settings.get_pagination_setting()
        title = f'Server settings for {ctx.guild.name}'
        note = None
        if on_reset:
            note = 'Successfully reset pagination for this server!'
        elif on_set:
            note = 'Successfully toggled pagination for this server!'
        output = await _server_settings.get_pretty_guild_settings(ctx, full_settings, title=title, note=note)
        await _utils.discord.reply_with_output(ctx, output)


    @settings.command(name='prefix', brief='Retrieve prefix settings')
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_get_prefix(self, ctx: _Context, *args):
        """
        Retrieve the prefix setting for this server.

        You need the 'Manage Server' permission to use this command.
        This command can only be used on Discord servers/guilds.

        Usage:
        /settings prefix

        Examples:
        /settings prefix - Prints the prefix setting for the current Discord server/guild.
        """
        self._log_command_use(ctx)
        await self._assert_settings_command_valid(ctx)

        await ctx.invoke(self.bot.get_command('prefix'), *args)


    @_command(name='prefix', brief='Retrieve prefix settings')
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def prefix(self, ctx: _Context, *args):
        """
        Retrieve the prefix setting for this server.

        This command can only be used on Discord servers/guilds.

        Usage:
        /prefix

        Examples:
        /prefix - Prints the prefix setting for the current Discord server/guild.
        """
        self._log_command_use(ctx)

        _, on_reset, on_set = self._extract_dash_parameters(ctx.message.content, args, '--on_reset', '--on_set')
        if _utils.discord.is_guild_channel(ctx.channel):
            title = f'Server settings for {ctx.guild.name}'
            guild_settings = await _server_settings.GUILD_SETTINGS.get(self.bot, ctx.guild.id)
            prefix_settings = guild_settings.get_prefix_setting()
        else:
            title = 'Bot settings'
            prefix_settings = {'prefix': _settings.DEFAULT_PREFIX}
        note = None
        if on_reset:
            note = 'Successfully reset prefix for this server!'
        elif on_set:
            note = 'Successfully set prefix for this server!'
        output = await _server_settings.get_pretty_guild_settings(ctx, prefix_settings, title=title, note=note)
        await _utils.discord.reply_with_output(ctx, output)





    @settings.group(name='reset', brief='Reset server settings', invoke_without_command=True)
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_reset(self, ctx: _Context):
        """
        Reset settings for this server.

        You need the 'Manage Server' permission to use any of these commands.
        This command can only be used on Discord servers/guilds.

        Usage:
        /settings reset

        Examples:
        /settings reset - Resets all settings for the current Discord server/guild.
        """
        if ctx.invoked_subcommand is None:
            self._log_command_use(ctx)
            await self._assert_settings_command_valid(ctx)

            guild_settings = await _server_settings.GUILD_SETTINGS.get(self.bot, ctx.guild.id)
            success = await guild_settings.reset()
            if all(success):
                await ctx.invoke(self.bot.get_command('settings'), '--on_reset')
            else:
                raise _Error('Could not reset all settings for this server. Please check the settings and try again or contact the bot\'s author.')


    @settings_reset.group(name='autodaily', aliases=['daily'], brief='Reset auto-daily settings to defaults')
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_reset_autodaily(self, ctx: _Context):
        """
        Reset the auto-daily settings for this server.

        You need the 'Manage Server' permission to use this command.
        This command can only be used on Discord servers/guilds.

        Usage:
        /settings reset autodaily
        /settings reset daily

        Examples:
        /settings reset autodaily - Resets the auto-daily settings for the current Discord server/guild.
        """
        if ctx.invoked_subcommand is None:
            self._log_command_use(ctx)
            await self._assert_settings_command_valid(ctx)

            autodaily_settings = (await _server_settings.GUILD_SETTINGS.get(self.bot, ctx.guild.id)).autodaily
            success = await autodaily_settings.reset()
            if success:
                await ctx.invoke(self.bot.get_command(f'settings autodaily'), '--on_reset')
            else:
                raise _Error('An error ocurred while trying to remove the auto-daily settings for this server.\n'
                            + 'Please try again or contact the bot\'s author.')


    @settings_reset_autodaily.command(name='channel', aliases=['ch'], brief='Reset auto-daily channel')
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_reset_autodaily_channel(self, ctx: _Context):
        """
        Reset the auto-daily channel settings for this server.

        You need the 'Manage Server' permission to use this command.
        This command can only be used on Discord servers/guilds.

        Usage:
        /settings reset autodaily channel
        /settings reset daily ch

        Examples:
        /settings reset autodaily - Removes the auto-daily channel settings for the current Discord server/guild.
        """
        self._log_command_use(ctx)
        await self._assert_settings_command_valid(ctx)

        if _utils.discord.is_guild_channel(ctx.channel):
            autodaily_settings = (await _server_settings.GUILD_SETTINGS.get(self.bot, ctx.guild.id)).autodaily
            success = await autodaily_settings.reset_channel()
            if success:
                await ctx.invoke(self.bot.get_command(f'settings autodaily channel'), '--on_reset')
            else:
                raise _Error('An error ocurred while trying to remove the auto-daily channel setting for this server.\n'
                            + 'Please try again or contact the bot\'s author.')


    @settings_reset_autodaily.command(name='changemode', aliases=['mode'], brief='Reset auto-daily change mode')
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_reset_autodaily_mode(self, ctx: _Context):
        """
        Reset the auto-daily change mode settings for this server.

        You need the 'Manage Server' permission to use this command.
        This command can only be used on Discord servers/guilds.

        Usage:
        /settings reset autodaily changemode
        /settings reset daily mode

        Examples:
        /settings reset autodaily mode - Resets the change mode for auto-daily changes for the current Discord server/guild.
        """
        self._log_command_use(ctx)
        await self._assert_settings_command_valid(ctx)

        if _utils.discord.is_guild_channel(ctx.channel):
            autodaily_settings = (await _server_settings.GUILD_SETTINGS.get(self.bot, ctx.guild.id)).autodaily
            success = await autodaily_settings.reset_daily_delete_on_change()
            if success:
                await ctx.invoke(self.bot.get_command(f'settings autodaily mode'), '--on_reset')
            else:
                raise _Error('An error ocurred while trying to remove the auto-daily notification settings for this server.\n'
                            + 'Please try again or contact the bot\'s author.')


    @settings_reset.command(name='embed', aliases=['embeds'], brief='Reset embed settings')
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_reset_embeds(self, ctx: _Context):
        """
        Reset the embed settings for this server to 'ON'. It determines, whether the bot output on this server will be served in embeds or in plain text.

        You need the 'Manage Server' permission to use this command.
        This command can only be used on Discord servers/guilds.

        Usage:
        /settings reset embed
        /settings reset embeds

        Examples:
        /settings reset embed - Resets the embed settings for the current Discord server/guild.
        """
        self._log_command_use(ctx)
        await self._assert_settings_command_valid(ctx)

        if _utils.discord.is_guild_channel(ctx.channel):
            guild_settings = await _server_settings.GUILD_SETTINGS.get(self.bot, ctx.guild.id)
            success = await guild_settings.reset_use_embeds()
            if success:
                await ctx.invoke(self.bot.get_command(f'settings embed'), '--on_reset')
            else:
                raise _Error('An error ocurred while trying to reset the embed settings for this server.\n'
                            + 'Please try again or contact the bot\'s author.')


    @settings_reset.command(name='pagination', aliases=['pages'], brief='Reset pagination settings')
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_reset_pagination(self, ctx: _Context):
        """
        Reset the pagination settings for this server to 'ON'. For information on what pagination is and what it does, use this command: /help pagination

        You need the 'Manage Server' permission to use this command.
        This command can only be used on Discord servers/guilds.

        Usage:
        /settings reset pagination
        /settings reset pages

        Examples:
        /settings reset pagination - Resets the pagination settings for the current Discord server/guild.
        """
        self._log_command_use(ctx)
        await self._assert_settings_command_valid(ctx)

        if _utils.discord.is_guild_channel(ctx.channel):
            guild_settings = await _server_settings.GUILD_SETTINGS.get(self.bot, ctx.guild.id)
            success = await guild_settings.reset_use_pagination()
            if success:
                await ctx.invoke(self.bot.get_command(f'settings pagination'), '--on_reset')
            else:
                raise _Error('An error ocurred while trying to reset the pagination settings for this server.\n'
                            + 'Please try again or contact the bot\'s author.')


    @settings_reset.command(name='prefix', brief='Reset prefix settings')
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_reset_prefix(self, ctx: _Context):
        """
        Reset the prefix settings for this server to '/'.

        You need the 'Manage Server' permission to use this command.
        This command can only be used on Discord servers/guilds.

        Usage:
        /settings reset prefix

        Examples:
        /settings reset prefix - Resets the prefix settings for the current Discord server/guild.
        """
        self._log_command_use(ctx)
        await self._assert_settings_command_valid(ctx)

        if _utils.discord.is_guild_channel(ctx.channel):
            guild_settings = await _server_settings.GUILD_SETTINGS.get(self.bot, ctx.guild.id)
            success = await guild_settings.reset_prefix()
            if success:
                await ctx.invoke(self.bot.get_command(f'settings prefix'), '--on_reset')
            else:
                raise _Error('An error ocurred while trying to reset the prefix settings for this server.\n'
                            + 'Please try again or contact the bot\'s author.')





    @settings.group(name='set', brief='Change server settings', invoke_without_command=False)
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_set(self, ctx: _Context):
        """
        Set settings for this server.

        You need the 'Manage Server' permission to use any of these commands.
        This command can only be used on Discord servers/guilds.

        Usage:
        Refer to sub-command help.

        Examples:
        Refer to sub-command help.
        """
        self._log_command_use(ctx)
        if ctx.invoked_subcommand is None:
            await ctx.send_help('settings set')


    @settings_set.group(name='autodaily', aliases=['daily'], brief='Change auto-daily settings', invoke_without_command=False)
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_set_autodaily(self, ctx: _Context):
        """
        Set auto-daily settings for this server.

        You need the 'Manage Server' permission to use any of these commands.
        This command can only be used on Discord servers/guilds.
        """
        self._log_command_use(ctx)
        if ctx.invoked_subcommand is None:
            await ctx.send_help('settings set autodaily')


    @settings_set_autodaily.command(name='channel', aliases=['ch'], brief='Set auto-daily channel')
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_set_autodaily_channel(self, ctx: _Context, text_channel: _TextChannel = None):
        """
        Set the auto-daily channel for this server. This channel will receive an automatic /daily message at 1 am UTC.

        You need the 'Manage Server' permission to use this command.
        This command can only be used on Discord servers/guilds.

        Usage:
        /settings set autodaily channel <text_channel_mention>
        /settings set daily ch <text_channel_mention>

        Parameters:
        text_channel_mention: Optional. A mention of a text-channel on the current Discord server/guild. If omitted, the bot will attempt try to set the current channel.

        Examples:
        /settings set daily channel - Sets the current channel to receive the /daily message once a day.
        /settings set autodaily ch #announcements - Sets the channel #announcements to receive the /daily message once a day.
        """
        self._log_command_use(ctx)
        await self._assert_settings_command_valid(ctx)

        autodaily_settings: _server_settings.AutoDailySettings = (await _server_settings.GUILD_SETTINGS.get(self.bot, ctx.guild.id)).autodaily
        if not text_channel:
            text_channel = ctx.channel

        permissions = text_channel.permissions_for(ctx.me)
        if permissions.read_messages is not True:
            raise _Error('I don\'t have access to that channel.')
        if permissions.read_message_history is not True:
            raise _Error('I don\'t have access to the messages history in that channel.')
        if permissions.send_messages is not True:
            raise _Error('I don\'t have permission to post in that channel.')

        success = await autodaily_settings.set_channel(text_channel)
        if success:
            await ctx.invoke(self.bot.get_command('settings autodaily channel'), '--on_set')
        else:
            raise _Error(f'Could not set autodaily channel for this server. Please try again or contact the bot\'s author.')


    @settings_set_autodaily.command(name='changemode', aliases=['mode'], brief='Set auto-daily repost mode')
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_set_autodaily_mode(self, ctx: _Context):
        """
        Set the auto-daily mode for this server. If the contents of the daily post change, this setting decides, whether an existing daily post gets edited, or if it gets deleted and a new one gets posted instead.

        You need the 'Manage Server' permission to use this command.
        This command can only be used on Discord servers/guilds.

        Usage:
        /settings set autodaily changemode
        /settings set daily change

        Examples:
        /settings set autodaily changemode - Toggles the change mode.
        """
        self._log_command_use(ctx)
        await self._assert_settings_command_valid(ctx)

        autodaily_settings = (await _server_settings.GUILD_SETTINGS.get(self.bot, ctx.guild.id)).autodaily
        success = await autodaily_settings.toggle_change_mode()
        if success:
            await ctx.invoke(self.bot.get_command('settings autodaily changemode'), '--on_set')
        else:
            raise _Error(f'Could not set repost on autodaily change mode for this server. Please try again or contact the bot\'s author.')


    @settings_set.command(name='embed', aliases=['embeds'], brief='Set embed settings')
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_set_embeds(self, ctx: _Context, switch: str = None):
        """
        Set or toggle the pagination for this server. The default is 'ON'. It determines, whether the bot output on this server will be served in embeds or in plain text.

        You need the 'Manage Server' permission to use this command.
        This command can only be used on Discord servers/guilds.

        Usage:
        /settings set embed <switch>
        /settings set embeds <switch>

        Parameters:
        format: Optional. A string determining the new pagination setting. Valid values: [on, off, true, false, yes, no, 1, 0, 👍, 👎]

        Notes:
        If the parameter <switch> is being omitted, the command will toggle between 'ON' and 'OFF' depending on the current setting.

        Examples:
        /settings set embed - Toggles the embed setting for the current Discord server/guild depending on the current setting.
        /settings set embed off - Turns off embeds for the current Discord server/guild.
        """
        self._log_command_use(ctx)
        await self._assert_settings_command_valid(ctx)

        guild_settings = await _server_settings.GUILD_SETTINGS.get(self.bot, ctx.guild.id)
        success = await guild_settings.set_use_embeds(switch)
        if success:
            await ctx.invoke(self.bot.get_command('settings embed'), '--on_set')
        else:
            raise _Error(f'Could not set embed settings for this server. Please try again or contact the bot\'s author.')


    @settings_set.command(name='pagination', aliases=['pages'], brief='Set pagination')
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_set_pagination(self, ctx: _Context, switch: str = None):
        """
        Set or toggle the pagination for this server. The default is 'ON'. For information on what pagination is and what it does, use this command: /help pagination

        You need the 'Manage Server' permission to use this command.
        This command can only be used on Discord servers/guilds.

        Usage:
        /settings set pagination <switch>
        /settings set pages <switch>

        Parameters:
        format: Optional. A string determining the new pagination setting. Valid values: [on, off, true, false, yes, no, 1, 0, 👍, 👎]

        Notes:
        If the parameter <switch> is being omitted, the command will toggle between 'ON' and 'OFF' depending on the current setting.

        Examples:
        /settings set pagination - Toggles the pagination setting for the current Discord server/guild depending on the current setting.
        /settings set pagination off - Turns off pagination for the current Discord server/guild.
        """
        self._log_command_use(ctx)
        await self._assert_settings_command_valid(ctx)

        guild_settings = await _server_settings.GUILD_SETTINGS.get(self.bot, ctx.guild.id)
        success = await guild_settings.set_use_pagination(switch)
        if success:
            await ctx.invoke(self.bot.get_command('settings pagination'), '--on_set')
        else:
            raise _Error(f'Could not set pagination settings for this server. Please try again or contact the bot\'s author.')


    @settings_set.command(name='prefix', brief='Set prefix')
    @_cooldown(rate=_CogBase.RATE, per=_CogBase.COOLDOWN, type=_BucketType.user)
    async def settings_set_prefix(self, ctx: _Context, prefix: str):
        """
        Set the prefix for this server. The default is '/'.

        You need the 'Manage Server' permission to use this command.
        This command can only be used on Discord servers/guilds.

        Usage:
        /settings set prefix [prefix]

        Parameters:
        prefix: Mandatory. A string determining the new prefix. Leading whitespace will be omitted.

        Examples:
        /settings set prefix & - Sets the bot's prefix for the current Discord server/guild to '&'
        """
        self._log_command_use(ctx)
        await self._assert_settings_command_valid(ctx)

        prefix = prefix.lstrip()
        guild_settings = await _server_settings.GUILD_SETTINGS.get(self.bot, ctx.guild.id)
        success = await guild_settings.set_prefix(prefix)
        if success:
            await ctx.invoke(self.bot.get_command('settings prefix'), '--on_set')
        else:
            raise _Error(f'Could not set prefix for this server. Please try again or contact the bot\'s author.')


    async def _assert_settings_command_valid(self, ctx: _Context) -> None:
        if _utils.discord.is_guild_channel(ctx.channel):
            permissions = ctx.channel.permissions_for(ctx.author)
            if permissions.manage_guild is not True:
                raise _command_errors.MissingPermissions(['manage_guild'])
        else:
            raise Exception('This command cannot be used in DMs or group chats, but only in Discord servers/guilds.')





def setup(bot: _YadcBot):
    bot.add_cog(SettingsCog(bot))