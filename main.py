"""TODO"""

import os
from enum import Enum
from dataclasses import dataclass

import pyray as rl  # type: ignore


W, H = 640, 400
SCALE = 2
WW, WH = W * SCALE, H * SCALE  # Window size
FH = 20.0  # Font height/size
FW = 17.5

GREEN = rl.Color(57, 212, 81, 255)

HELP = """\
Command                 Description
-------                 -----------
- [digits] [content]    Write a line in program
- DEL [digits]          Remove a line in program
- LIST                  Print the program
- HOME                  Clear the terminal
- HELP                  Display this menu
- ISA                   Return the BatPU-2 Instruction Set Architecture
- SAVE [optional file]  Save the program (default: main)
- LOAD [optional file]  Load the program (default: main)
- LS                    Display the list of programs in the memory"""

# Official doc:
# https://docs.google.com/spreadsheets/d/1Bj3wHV-JifR2vP4HRYoCWrdXYp3sGMG0Q58Nm56W4aI
ISA = """\
Mnemonic Operands                      Description
-------- --------                      -----------

- NOP                                  No operation
- HLT                                  Halt

- ADD    [target] [a] [b]              Addition
- SUB    [target] [a] [b]              Substraction
- NOR    [target] [a] [b]              Bitwise NOR
- AND    [target] [a] [b]              Bitwise AND
- XOR    [target] [a] [b]              Bitwise XOR
- RSH    [target] [a]                  Right shift

- LDI    [target]                      Load immediate
- ADI    [target]                      Add immediate

- JMP    [address]                     Jump
- BRH    [condition] [address]         Branch
- CAL    [address]                     Call
- RET                                  Return

- LOD    [a] [target] [offset]         Memory load
- STR    [target] [a] [target_offset]  Memory store

- CMP    [a] [b]                       Compare
- MOV    [a] [b]                       Move
- LSH    [a] [b]                       Left shift
- INC    [a]                           Increment
- DEC    [a]                           Decrement
- NOT    [a] [b]                       Bitwise NOT
- NEG    [a] [b]                       Negate"""


class CursorStyle(Enum):
    """TODO"""

    SOLID = 0
    FRAME = 1
    LINE = 2


@dataclass
class Line:
    """TODO"""

    cmd: bool = False
    content: str = ""


class Program:
    """TODO"""

    def __init__(self) -> None:
        """TODO"""
        self.saved = True  # Empty at beginning
        self.content: dict[int, str] = {}

    def iter(self) -> list[tuple[int, str]]:
        """TODO"""
        return sorted(self.content.items(), key=lambda item: item[0])

    def to_string(self) -> str:
        """TODO"""
        result = ""

        n = 1
        for line, content in self.iter():
            for _ in range(line - n):
                result += "\n"
            n = line + 1

            result += content + "\n"

        return result


class Cursor:
    """TODO"""

    def __init__(self) -> None:
        """TODO"""
        self.style = CursorStyle.SOLID
        self.cmd = True

        self.x = 0
        self.y = 2
        self.offy = 0

        self.tick = 0

        # Helper
        self.nlines = 1

    def draw(self) -> None:
        """TODO"""
        self.tick += 1

        offset = 2 if self.cmd else 0

        if self.tick % 30 < 16:
            match self.style:
                case CursorStyle.SOLID:
                    rl.draw_rectangle(
                        int((self.x + offset) * FW),
                        int((self.y - self.offy) * 20.0),
                        17,
                        20,
                        GREEN,
                    )

                case CursorStyle.FRAME:
                    rl.draw_rectangle_lines_ex(
                        rl.Rectangle(
                            int((self.x + offset) * FW),
                            int((self.y - self.offy) * 20.0),
                            17,
                            20,
                        ),
                        2.0,
                        GREEN,
                    )

                case CursorStyle.LINE:
                    rl.draw_line_ex(
                        rl.Vector2(
                            int((self.x + offset) * FW),
                            int((self.y - self.offy) * 20.0),
                        ),
                        rl.Vector2(
                            int((self.x + offset) * FW),
                            int((self.y - self.offy) * 20.0) + FH,
                        ),
                        2.0,
                        GREEN,
                    )

    def fix_offy(self) -> None:
        """TODO"""
        if self.y > 40:
            self.offy = self.y - 38

    def handle_key(self, line_length: int):
        """TODO"""
        if (
            rl.is_key_pressed_repeat(rl.KeyboardKey.KEY_UP)
            or rl.is_key_pressed(rl.KeyboardKey.KEY_UP)
        ):
            self.offy -= 1
            if self.offy == -1:
                self.offy = 0

        elif (
            rl.is_key_pressed_repeat(rl.KeyboardKey.KEY_DOWN)
            or rl.is_key_pressed(rl.KeyboardKey.KEY_DOWN)
        ):
            self.offy += 1
            if self.offy > self.nlines - 1:
                self.offy -= 1

        elif (
            rl.is_key_pressed_repeat(rl.KeyboardKey.KEY_LEFT)
            or rl.is_key_pressed(rl.KeyboardKey.KEY_LEFT)
        ):
            self.x -= 1
            if self.x == -1:
                self.x = 0
            self.fix_offy()

        elif (
            rl.is_key_pressed_repeat(rl.KeyboardKey.KEY_RIGHT)
            or rl.is_key_pressed(rl.KeyboardKey.KEY_RIGHT)
        ):
            self.x += 1
            if self.x == line_length + 1:
                self.x -= 1
            self.fix_offy()


class Terminal:
    """TODO"""

    def __init__(self) -> None:
        """TODO"""
        self.lines: list[Line] = [Line(content="Welcome!"), Line(), Line(True)]
        self.program = Program()
        self.cursor = Cursor()

    def add_cmd_char(self, char: str) -> None:
        """TODO"""
        # End of line
        if self.cursor.x == len(self.lines[self.cursor.y].content):
            self.lines[self.cursor.y].content += char
            self.cursor.x += 1
        # Not at the end
        else:
            content = self.lines[self.cursor.y].content
            self.lines[self.cursor.y].content = (
                content[:self.cursor.x] + char + content[self.cursor.x:]
            )
            self.cursor.x += 1

    def remove_cmd_char(self) -> None:
        """TODO"""
        if len(self.lines[self.cursor.y].content) != 0:
            # End of line
            if self.cursor.x == len(self.lines[self.cursor.y].content):
                self.lines[self.cursor.y].content = \
                    self.lines[self.cursor.y].content[:-1]
                self.cursor.x -= 1

            # Not at the end
            else:
                if self.cursor.x != 0:
                    content = self.lines[self.cursor.y].content
                    self.lines[self.cursor.y].content = (
                        content[:self.cursor.x - 1] + content[self.cursor.x:]
                    )
                    self.cursor.x -= 1

    def remove_cmd_word(self) -> None:
        """TODO"""
        content = self.lines[self.cursor.y].content
        in_word = False

        for i in range(len(content) - 1, -1, -1):
            if in_word:
                if content[i] == " ":
                    self.cursor.x -= len(content) - i
                    self.lines[self.cursor.y].content = content[:i]
                    return
                continue

            if content[i] == " ":
                continue
            in_word = True

        self.cursor.x = 0
        self.lines[self.cursor.y].content = ""

    def add_line(self, cmd: bool = False, content: str = "") -> None:
        """TODO"""
        self.lines.append(Line(cmd, content))
        self.cursor.y += 1
        self.cursor.nlines += 1

    def add_lines(self, lines: list[str]) -> None:
        """TODO"""
        for line in lines:
            self.add_line(content=line)

    def end_of_cmd(self) -> None:
        """TODO"""
        self.add_line(True)
        self.cursor.x = 0
        self.cursor.fix_offy()

    def handle_key(self) -> None:
        """TODO"""
        char_id = rl.get_char_pressed()

        if 32 <= char_id <= 126:
            self.add_cmd_char(chr(char_id))
            self.cursor.fix_offy()

        elif rl.is_key_pressed_repeat(
            rl.KeyboardKey.KEY_BACKSPACE
        ) or rl.is_key_pressed(rl.KeyboardKey.KEY_BACKSPACE):
            if rl.is_key_down(rl.KeyboardKey.KEY_LEFT_CONTROL):
                self.remove_cmd_word()
            else:
                self.remove_cmd_char()
            self.cursor.fix_offy()

        elif rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER):
            if self.cursor.cmd:
                self.run_cmd()

        else:
            self.cursor.handle_key(len(self.lines[self.cursor.y].content))

    def remove_program_line(self, args: list[str]) -> None:
        """TODO"""
        if args[0].isdigit():
            try:
                del self.program.content[int(args[0])]
                self.program.saved = False
            except KeyError:
                self.add_line(
                    content="Error: Line number doesn't exists in the program"
                )
        else:
            self.add_line(content="Error: Argument expected digits")

        self.end_of_cmd()

    def save_program(self, args: list[str]) -> None:
        """TODO"""
        os.makedirs("memory", exist_ok=True)

        if len(args):
            path = "memory/" + "".join(args) + ".as"
        else:
            path = "memory/main.as"

        with open(path, "w+", encoding="utf-8") as f:
            f.write(self.program.to_string())

        self.program.saved = True

        self.end_of_cmd()

    def load_program(self, args: list[str]) -> None:
        """TODO"""
        if not self.program.saved:
            self.add_line(content="Warn: the program isn't saved")

        else:
            self.program.content = {}

            if len(args):
                path = "memory/" + "".join(args) + ".as"
            else:
                path = "memory/main.as"

            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as f:
                    file_content = f.read()

                    for line, content in enumerate(file_content.split("\n")):
                        if content != "":
                            self.program.content[line + 1] = content

                # Don't need that but keep in mind the file is saved at load
                # self.program.saved = True

            else:
                self.add_line(content=f"Error: {path} doen't exists")

        self.end_of_cmd()

    def run_cmd(self) -> None:
        """TODO"""
        splitted_content = self.lines[self.cursor.y].content.split(" ")
        cmd = splitted_content[0]
        args = splitted_content[1:]

        # Write
        if cmd.isdigit():
            line = int(cmd)
            if line < 1:
                self.add_line(content="Error: Line number expected > 0")
            else:
                self.program.content[int(cmd)] = " ".join(args)
                self.program.saved = False
            self.end_of_cmd()

        else:
            match cmd:
                case "DEL" | "del":
                    self.remove_program_line(args)

                case "LIST" | "list":
                    self.add_line()
                    for line, file_content in self.program.iter():
                        self.add_line(content=f"{line} {file_content}")
                    self.add_line()

                    self.end_of_cmd()

                case "HOME" | "home":
                    self.lines = [Line(True)]
                    self.cursor.x = 0
                    self.cursor.y = 0
                    self.cursor.nlines = 1
                    self.cursor.offy = 0

                case "HELP" | "help":
                    self.add_line()
                    self.add_lines(HELP.split("\n"))
                    self.add_line()

                    self.end_of_cmd()

                case "ISA" | "isa":
                    self.add_line()
                    self.add_lines(ISA.split("\n"))
                    self.add_line()

                    self.end_of_cmd()

                case "SAVE" | "save":
                    self.save_program(args)

                case "LOAD" | "load":
                    self.load_program(args)

                case "LS" | "ls":
                    self.add_line()
                    for file in os.listdir("memory/"):
                        if file.endswith(".as"):
                            self.add_line(content=f"- {file[:-3]}")
                    self.add_line()

                    self.end_of_cmd()

                # Unknown command
                case _:
                    self.add_line(
                        content="Unknown command, use HELP to display commands"
                    )
                    self.end_of_cmd()

    def draw(self) -> None:
        """TODO"""
        for index, line in enumerate(self.lines):
            if line.cmd:
                content = "] "
            else:
                content = ""

            rl.draw_text_ex(
                font,
                content + line.content,
                rl.Vector2(0.0, (index - self.cursor.offy) * FH),
                FH,
                0.0,
                GREEN,
            )

        self.cursor.draw()

    @staticmethod
    def draw_grid() -> None:
        """TODO"""
        x = 0.0
        while x < WW:
            rl.draw_line(int(x), 0, int(x), WH, rl.DARKGRAY)
            x += 17.5

        y = 0.0
        while y < WW:
            rl.draw_line(0, int(y), WW, int(y), rl.DARKGRAY)
            y += 20.0


rl.init_window(WW, WH, "Apple ][")
rl.set_target_fps(60)
rl.set_exit_key(rl.KeyboardKey.KEY_NULL)

font = rl.load_font("assets/font/PrintChar21.ttf")  # 17.5, 20.0
terminal = Terminal()
target = rl.load_render_texture(WW, WH)

shader = rl.load_shader("assets/base.vert", "assets/main.frag")
rl.set_shader_value(
    shader,
    rl.get_shader_location(shader, "resolution"),
    rl.ffi.new("float[]", [WW, WH]),
    rl.ShaderUniformDataType.SHADER_UNIFORM_VEC2,
)


while not rl.window_should_close():
    # Update
    terminal.handle_key()

    # Render
    rl.begin_drawing()

    rl.begin_texture_mode(target)
    rl.clear_background(rl.BLACK)
    # terminal.draw_grid()
    terminal.draw()
    rl.end_texture_mode()

    rl.begin_shader_mode(shader)
    rl.draw_texture(target.texture, 0, 0, rl.WHITE)
    rl.end_shader_mode()

    rl.end_drawing()

rl.close_window()
