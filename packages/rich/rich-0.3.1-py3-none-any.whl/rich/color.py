import re
from colorsys import rgb_to_hls
from dataclasses import dataclass
from enum import IntEnum
from functools import lru_cache
from math import sqrt
from typing import Iterable, List, NamedTuple, Optional, Sequence, Tuple, TYPE_CHECKING

from ._palettes import STANDARD_PALETTE, EIGHT_BIT_PALETTE
from .color_triplet import ColorTriplet

if TYPE_CHECKING:  # pragma: no cover
    from .theme import Theme


class ColorSystem(IntEnum):
    """One of the 3 color system supported by terminals."""

    STANDARD = 1
    EIGHT_BIT = 2
    TRUECOLOR = 3


class ColorType(IntEnum):
    """Type of color stored in Color class."""

    DEFAULT = 0
    STANDARD = 1
    EIGHT_BIT = 2
    TRUECOLOR = 3


ANSI_COLOR_NAMES = {
    "black": 0,
    "red": 1,
    "green": 2,
    "yellow": 3,
    "blue": 4,
    "magenta": 5,
    "cyan": 6,
    "white": 7,
    "bright_black": 8,
    "bright_red": 9,
    "bright_green": 10,
    "bright_yellow": 11,
    "bright_blue": 12,
    "bright_magenta": 13,
    "bright_cyan": 14,
    "bright_white": 15,
    "grey0": 16,
    "navy_blue": 17,
    "dark_blue": 18,
    "blue3": 20,
    "blue1": 21,
    "dark_green": 22,
    "deep_sky_blue4": 25,
    "dodger_blue3": 26,
    "dodger_blue2": 27,
    "green4": 28,
    "spring_green4": 29,
    "turquoise4": 30,
    "deep_sky_blue3": 32,
    "dodger_blue1": 33,
    "green3": 40,
    "spring_green3": 41,
    "dark_cyan": 36,
    "light_sea_green": 37,
    "deep_sky_blue2": 38,
    "deep_sky_blue1": 39,
    "spring_green2": 47,
    "cyan3": 43,
    "dark_turquoise": 44,
    "turquoise2": 45,
    "green1": 46,
    "spring_green1": 48,
    "medium_spring_green": 49,
    "cyan2": 50,
    "cyan1": 51,
    "dark_red": 88,
    "deep_pink4": 125,
    "purple4": 55,
    "purple3": 56,
    "blue_violet": 57,
    "orange4": 94,
    "grey37": 59,
    "medium_purple4": 60,
    "slate_blue3": 62,
    "royal_blue1": 63,
    "chartreuse4": 64,
    "dark_sea_green4": 71,
    "pale_turquoise4": 66,
    "steel_blue": 67,
    "steel_blue3": 68,
    "cornflower_blue": 69,
    "chartreuse3": 76,
    "cadet_blue": 73,
    "sky_blue3": 74,
    "steel_blue1": 81,
    "pale_green3": 114,
    "sea_green3": 78,
    "aquamarine3": 79,
    "medium_turquoise": 80,
    "chartreuse2": 112,
    "sea_green2": 83,
    "sea_green1": 85,
    "aquamarine1": 122,
    "dark_slate_gray2": 87,
    "dark_magenta": 91,
    "dark_violet": 128,
    "purple": 129,
    "light_pink4": 95,
    "plum4": 96,
    "medium_purple3": 98,
    "slate_blue1": 99,
    "yellow4": 106,
    "wheat4": 101,
    "grey53": 102,
    "light_slate_grey": 103,
    "medium_purple": 104,
    "light_slate_blue": 105,
    "dark_olive_green3": 149,
    "dark_sea_green": 108,
    "light_sky_blue3": 110,
    "sky_blue2": 111,
    "dark_sea_green3": 150,
    "dark_slate_gray3": 116,
    "sky_blue1": 117,
    "chartreuse1": 118,
    "light_green": 120,
    "pale_green1": 156,
    "dark_slate_gray1": 123,
    "red3": 160,
    "medium_violet_red": 126,
    "magenta3": 164,
    "dark_orange3": 166,
    "indian_red": 167,
    "hot_pink3": 168,
    "medium_orchid3": 133,
    "medium_orchid": 134,
    "medium_purple2": 140,
    "dark_goldenrod": 136,
    "light_salmon3": 173,
    "rosy_brown": 138,
    "grey63": 139,
    "medium_purple1": 141,
    "gold3": 178,
    "dark_khaki": 143,
    "navajo_white3": 144,
    "grey69": 145,
    "light_steel_blue3": 146,
    "light_steel_blue": 147,
    "yellow3": 184,
    "dark_sea_green2": 157,
    "light_cyan3": 152,
    "light_sky_blue1": 153,
    "green_yellow": 154,
    "dark_olive_green2": 155,
    "dark_sea_green1": 193,
    "pale_turquoise1": 159,
    "deep_pink3": 162,
    "magenta2": 200,
    "hot_pink2": 169,
    "orchid": 170,
    "medium_orchid1": 207,
    "orange3": 172,
    "light_pink3": 174,
    "pink3": 175,
    "plum3": 176,
    "violet": 177,
    "light_goldenrod3": 179,
    "tan": 180,
    "misty_rose3": 181,
    "thistle3": 182,
    "plum2": 183,
    "khaki3": 185,
    "light_goldenrod2": 222,
    "light_yellow3": 187,
    "grey84": 188,
    "light_steel_blue1": 189,
    "yellow2": 190,
    "dark_olive_green1": 192,
    "honeydew2": 194,
    "light_cyan1": 195,
    "red1": 196,
    "deep_pink2": 197,
    "deep_pink1": 199,
    "magenta1": 201,
    "orange_red1": 202,
    "indian_red1": 204,
    "hot_pink": 206,
    "dark_orange": 208,
    "salmon1": 209,
    "light_coral": 210,
    "pale_violet_red1": 211,
    "orchid2": 212,
    "orchid1": 213,
    "orange1": 214,
    "sandy_brown": 215,
    "light_salmon1": 216,
    "light_pink1": 217,
    "pink1": 218,
    "plum1": 219,
    "gold1": 220,
    "navajo_white1": 223,
    "misty_rose1": 224,
    "thistle1": 225,
    "yellow1": 226,
    "light_goldenrod1": 227,
    "khaki1": 228,
    "wheat1": 229,
    "cornsilk1": 230,
    "grey100": 231,
    "grey3": 232,
    "grey7": 233,
    "grey11": 234,
    "grey15": 235,
    "grey19": 236,
    "grey23": 237,
    "grey27": 238,
    "grey30": 239,
    "grey35": 240,
    "grey39": 241,
    "grey42": 242,
    "grey46": 243,
    "grey50": 244,
    "grey54": 245,
    "grey58": 246,
    "grey62": 247,
    "grey66": 248,
    "grey70": 249,
    "grey74": 250,
    "grey78": 251,
    "grey82": 252,
    "grey85": 253,
    "grey89": 254,
    "grey93": 255,
}


class ColorParseError(Exception):
    """The color could not be parsed."""


RE_COLOR = re.compile(
    r"""^
\#([0-9a-f]{6})$|
([0-9]{1,3})$|
rgb\(([\d\s,]+)\)$
""",
    re.VERBOSE,
)


class Color(NamedTuple):
    """Terminal color definition."""

    name: str
    type: ColorType
    number: Optional[int] = None
    triplet: Optional[ColorTriplet] = None

    def __str__(self) -> str:
        """Render the color to the terminal."""
        attrs = self.get_ansi_codes(foreground=True)
        return (
            f"\x1b[{';'.join(attrs)}m⬤  \x1b[0m"
            f"<color {self.name!r} ({self.type.name.lower()})>"
        )

    def __repr__(self) -> str:
        return f"<color {self.name!r} ({self.type.name.lower()})>"

    @property
    def system(self) -> ColorSystem:
        """Get the native color system for this color."""
        if self.type == ColorType.DEFAULT:
            return ColorSystem.STANDARD
        return ColorSystem(int(self.type))

    def get_truecolor(self, theme: "Theme", foreground=True) -> ColorTriplet:
        """Get a color triplet for this color."""
        if self.type == ColorType.TRUECOLOR:
            assert self.triplet is not None
            return self.triplet
        elif self.type == ColorType.EIGHT_BIT:
            assert self.number is not None
            if self.number <= 15:
                return theme.ansi_colors[self.number]
            else:
                return EIGHT_BIT_PALETTE[self.number]
        elif self.type == ColorType.STANDARD:
            assert self.number is not None
            return theme.ansi_colors[self.number]
        else:  # self.type == ColorType.DEFAULT:
            assert self.number is None
            return theme.foreground_color if foreground else theme.background_color

    @classmethod
    def from_triplet(cls, triplet: "ColorTriplet") -> "Color":
        """Create a truecolor RGB color from a triplet of values.
        
        Args:
            triplet (ColorTriplet): A color triplet containing red, green and blue components.
        
        Returns:
            Color: A new color object.
        """
        return cls(name=triplet.hex, type=ColorType.TRUECOLOR, triplet=triplet)

    @classmethod
    def default(cls) -> "Color":
        """Get a Color instance representing the default color.
        
        Returns:
            Color: Default color.
        """
        return cls(name="default", type=ColorType.DEFAULT)

    @classmethod
    @lru_cache(maxsize=1000)
    def parse(cls, color: str) -> "Color":
        """Parse a color definition."""
        color = color.lower().strip()

        if color == "default":
            return cls(color, type=ColorType.DEFAULT)

        named_color_number = ANSI_COLOR_NAMES.get(color)
        if named_color_number is not None:
            return cls(
                color,
                type=(
                    ColorType.STANDARD
                    if named_color_number < 8
                    else ColorType.EIGHT_BIT
                ),
                number=named_color_number,
            )

        color_match = RE_COLOR.match(color)
        if color_match is None:
            raise ColorParseError(f"{color!r} is not a valid color")

        color_24, color_8, color_rgb = color_match.groups()
        if color_8:
            number = int(color_8)
            if number > 255:
                raise ColorParseError(f"8bit colors must be <= 255 in {color!r}")
            return cls(color, ColorType.EIGHT_BIT, number=number)

        elif color_24:
            triplet = ColorTriplet(
                int(color_24[0:2], 16), int(color_24[2:4], 16), int(color_24[4:6], 16)
            )
            return cls(color, ColorType.TRUECOLOR, triplet=triplet)

        else:  #  color_rgb:
            components = color_rgb.split(",")
            if len(components) != 3:
                raise ColorParseError(f"expected three components in {color!r}")
            red, green, blue = components
            triplet = ColorTriplet(int(red), int(green), int(blue))
            if not all(component <= 255 for component in triplet):
                raise ColorParseError(f"color components must be <= 255 in {color!r}")
            return cls(color, ColorType.TRUECOLOR, triplet=triplet)

    @lru_cache(maxsize=1000)
    def get_ansi_codes(self, foreground: bool = True) -> List[str]:
        """Get the ANSI escape codes for this color."""
        _type = self.type
        if _type == ColorType.DEFAULT:
            return ["39" if foreground else "49"]

        elif _type == ColorType.STANDARD:
            number = self.number
            assert number is not None
            return [str(30 + number if foreground else 40 + number)]

        elif _type == ColorType.EIGHT_BIT:
            assert self.number is not None
            return ["38" if foreground else "48", "5", str(self.number)]

        else:  # self.standard == ColorStandard.TRUECOLOR:
            assert self.triplet is not None
            red, green, blue = self.triplet
            return ["38" if foreground else "48", "2", str(red), str(green), str(blue)]

    @lru_cache(maxsize=1000)
    def downgrade(self, system: ColorSystem) -> "Color":
        """Downgrade a color system to a system with fewer colors."""

        # Convert to 8-bit color from truecolor color
        if system == ColorSystem.EIGHT_BIT and self.system == ColorSystem.TRUECOLOR:
            assert self.triplet is not None
            red, green, blue = self.triplet.normalized
            _h, l, s = rgb_to_hls(red, green, blue)

            # If saturation is under 10% assume it is grayscale
            if s < 0.1:
                gray = round(l * 25.0)
                if gray == 0:
                    color_number = 16
                elif gray == 25:
                    color_number = 231
                else:
                    color_number = 231 + gray
                return Color(self.name, ColorType.EIGHT_BIT, number=color_number)

            color_number = (
                16 + 36 * round(red * 5.0) + 6 * round(green * 5.0) + round(blue * 5.0)
            )
            return Color(self.name, ColorType.EIGHT_BIT, number=color_number)

        # Convert to standard from truecolor or 8-bit
        elif system == ColorSystem.STANDARD:
            if self.system == ColorSystem.TRUECOLOR:
                assert self.triplet is not None
                triplet = self.triplet
            else:  # self.system == ColorSystem.EIGHT_BIT
                assert self.number is not None
                triplet = ColorTriplet(*EIGHT_BIT_PALETTE[self.number])

            color_number = STANDARD_PALETTE.match(triplet)
            return Color(self.name, ColorType.STANDARD, number=color_number)

        return self


def parse_rgb_hex(hex_color: str) -> ColorTriplet:
    """Parse six hex characters in to RGB triplet."""
    assert len(hex_color) == 6, "must be 6 characters"
    color = ColorTriplet(
        int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    )
    return color


def blend_rgb(
    color1: ColorTriplet, color2: ColorTriplet, cross_fade: float = 0.5
) -> ColorTriplet:
    """Blend one RGB color in to another."""
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    new_color = ColorTriplet(
        int(r1 + (r2 - r1) * cross_fade),
        int(g1 + (g2 - g1) * cross_fade),
        int(b1 + (b2 - b1) * cross_fade),
    )
    return new_color


if __name__ == "__main__":  # pragma: no cover

    from .console import Console
    from .table import Column, Table
    from .text import Text
    from . import box

    console = Console(record=True)

    table = Table(show_footer=False, show_edge=True)
    table.add_column("Color", width=10)
    table.add_column("Number", justify="right", style="yellow")
    table.add_column("Name", style="green")
    table.add_column("Hex", style="blue")
    table.add_column("RGB", style="magenta")

    colors = sorted((v, k) for k, v in ANSI_COLOR_NAMES.items())
    for color_number, name in colors:
        color_cell = Text(" " * 10, style=f"on {name}")
        if color_number < 16:
            table.add_row(color_cell, f"{color_number}", Text(f'"{name}"'))
        else:
            color = EIGHT_BIT_PALETTE[color_number]
            table.add_row(
                color_cell, str(color_number), Text(f'"{name}"'), color.hex, color.rgb
            )

    console.print(table)
    console.save_html("color.html", inline_styles=True)
