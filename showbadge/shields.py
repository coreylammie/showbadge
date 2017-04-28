"""
Tools for making custom Shields badges.
"""
import re


class Shields:
    """
    Shields tool.

    Shields makes a badge for the ShowBadge item, more exactly, generates the
    URL of badge for the ShowBadge item. Badges are accessible by ShieldsIO_.

    .. _ShieldsIO: http://shields.io/
    """

    SHIELDS_IO_CUSTOM_BADGE_URL = "https://img.shields.io/badge/{subject}-{status}-{color}.svg"

    VALUE_ERROR = "undefined"
    COLOR_ERROR = "lightgrey"
    COLOR_COVER_0 = "red"
    COLOR_COVER_1 = "orange"
    COLOR_COVER_2 = "yellow"
    COLOR_COVER_3 = "yellowgreen"
    COLOR_COVER_4 = "green"
    COLOR_COVER_5 = "brightgreen"

    CHAR_RE = "[A-z!#$%&'*+-.^_`|~:]"
    NUM_RE = "-?([0-9]+(\.[0-9]+)?|\.[0-9]+)"
    COLOR_RE = "^auto(-?(?P<num1>{num})(-?(?P<num2>{num}))?)?$".format(num=NUM_RE)
    VALUE_RE = "^{char}*(?P<num>{num}){char}*$".format(char=CHAR_RE, num=NUM_RE)
    VALUE_FRAC_RE = "^{char}*(?P<num1>{num})/(?P<num2>{num}){char}*$".format(
        char=CHAR_RE, num=NUM_RE)

    @classmethod
    def get_badge_url(cls, key, value, color):
        """
        Returns the ShieldsIO URL of a badge for the given input.

        Set by `subject`, `status`, and `color` of the custom badge format of
        ShieldsIO service as `key`, `value`, and `color` of the given
        parameters, respectively. The basic URL of the custom badge of
        ShieldsIO is the form of
        `https://img.shields.io/badge/<subject>-<status>-<color>.svg`. See
        ShieldsIO_ for more information.

        `key` and `value` is escaped to follow conversion format of ShieldsIO.
        `color` is determined by more complicated conversion. For the cases of
        basic color names or hex number, color would be that given color. If
        `auto` mode is enabled, then color is determined by the numbers in
        `value`. If numbers in `value` are included in an invalid format or
        if `color` has not supported name or `value` is set to `undefined`,
        then color would be `lightgrey`.

        Args:
            key (:obj:`str`): Subject of a custom badge.
            value (:obj:`str`): Status of a custom badge.

                There are two special types of value to deal with continuous
                status. One is of the form `{char}*{num}{char}*`. Then this
                makes a badge with a color corresponding to the {num} compared
                to the range of `{num}`, given by default (0 to 100) or by
                `color`. The other is of the form `{char}*{num1}/{num2}{char}*`.
                This makes a badge with a color corresponding to the `{num1}`
                compared to the range 0 to `{num2}`. Note that these two special
                types would be enable only if `color` has `auto` option,
                described in below.

                In these two cases, `{char}` contains alphabets together with
                special characters among `!#$%&'*+-.^_`|~:` and {num} (or
                `{num1}`, `{num2}`) is of integers with or without decimals,
                such as `0.1`, `80`, `-.3`, etc.
            color (:obj:`str`): Color of a custom badge.

                Color should be 6-digits of hex color code in general. Or
                choose one of `brightgreen`, `green`, `yellowgreen`,
                `yellow`, `orange`, `red`, `lightgrey`, or `blue`.

                Moreover, there is a special type of color to deal with
                continuous status, `auto[-{num1}][-{num2}]`. If color is given
                of this type, the result color would be determined automatically
                by comparison `value` with range of numbers given by {num1} and
                {num2}. If number is not given, then it sets the range 0 to 100
                by default, if just one is given, the range would be 0 to that
                number. If two are given, {num1} to {num2} is going to be the
                range.

                Note that `{num1}` and `{num2}` are integers with or without
                decimals, such as `0.1`, `80`, `-.3`, etc.

                If color is set to `None`, then color would be treated as
                `auto`.

        Returns:
            :obj:`str`: The ShieldsIO URL of a badge for the given input.

        .. _ShieldsIO: http://shields.io/
        """
        key = cls.__escape_string(key)
        value = cls.__escape_string(value)
        color = cls.__parse_color(color, value)
        return cls.SHIELDS_IO_CUSTOM_BADGE_URL.format(subject=key, status=value, color=color)

    @classmethod
    def __escape_string(cls, string):
        if not string:
            return "undefined"
        return string.replace("-", "--").replace("_", "__").replace(" ", "_")

    @classmethod
    def __parse_color(cls, color, value):
        if value == cls.VALUE_ERROR:
            return cls.COLOR_ERROR

        if not color:
            color = "auto"

        color_match = re.compile(cls.COLOR_RE).match(color)
        if not color_match:
            return color

        color_args = color_match.groupdict()
        range_min = 0
        range_max = 100
        if color_args['num1']:
            range_max = float(color_args['num1'])
        if color_args['num2']:
            range_min = range_max
            range_max = float(color_args['num2'])

        value_match = re.compile(cls.VALUE_RE).match(value)
        if value_match:
            value_args = value_match.groupdict()
            value_num = float(value_args['num'])
            return cls.__get_color_by_range(value_num, range_min, range_max)

        frac_match = re.compile(cls.VALUE_FRAC_RE).match(value)
        if not frac_match:
            return color
        frac_args = frac_match.groupdict()
        value_num = float(frac_args['num1'])
        range_min = 0
        range_max = float(frac_args['num2'])
        return cls.__get_color_by_range(value_num, range_min, range_max)

    @classmethod
    def __get_color_by_range(cls, value_num, range_min, range_max):
        ratio = (value_num - range_min) / (range_max - range_min)
        if (ratio <= 0):
            return cls.COLOR_COVER_0
        if (ratio < .25):
            return cls.COLOR_COVER_1
        if (ratio < .5):
            return cls.COLOR_COVER_2
        if (ratio < .75):
            return cls.COLOR_COVER_3
        if (ratio < 1):
            return cls.COLOR_COVER_4
        return cls.COLOR_COVER_5
