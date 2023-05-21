import toml
import argparse
from dataclasses import dataclass
from typing import Union, List
from enum import Enum


class FactoryMode(Enum):
    none = 0
    factory = 1
    safe_factory = 2


@dataclass
class ArgDescriptor:
    name: str
    type: Union[str, 'ClassDescriptor']
    is_list: bool = False

    def __repr__(self):
        pre_type = ""
        post_type = ""
        if self.is_list:
            pre_type = "List["
            post_type = "]"
        return f"{self.name}: {pre_type}{self.type}{post_type}"


@dataclass
class ClassDescriptor:
    name: str
    args: List[ArgDescriptor]

    def __repr__(self):
        return self.name.capitalize()


def has_list_arg(descriptor: ClassDescriptor) -> bool:
    for arg in descriptor.args:
        if arg.is_list:
            return True
        if type(arg.type) is ClassDescriptor and has_list_arg(arg.type):
            return True
    return False


def setup_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("TOML to PyDTO")
    parser.add_argument("toml", type=str)
    parser.add_argument("out", type=str)
    parser.add_argument("-n", "--name", type=str)
    parser.add_argument("-f", "--factory", action="store_true")
    parser.add_argument("-s", "--safe", action="store_true")
    return parser


def process_object(name: str, d: dict):
    args = []
    for k, v in d.items():
        value = v
        is_list = False
        if type(v) is list:
            is_list = True
            value = v[0]

        if type(value) is int or type(value) is str or type(value) is float or type(value) is bool:
            args.append(ArgDescriptor(k, type(value).__name__, is_list))
        elif type(value) is dict:
            args.append(ArgDescriptor(k, process_object(k, value), is_list))

    return ClassDescriptor(name, args)


INDENT = "    "
FACTORY_MODE = FactoryMode.none


def generate_factory(descriptor: ClassDescriptor) -> str:
    if FACTORY_MODE == FactoryMode.none:
        return ""

    body = ""
    ret = []
    for arg in descriptor.args:
        entry = ""
        if FACTORY_MODE == FactoryMode.factory:
            entry = f"d[\"{arg.name}\"]"
        elif FACTORY_MODE == FactoryMode.safe_factory:
            entry = f"d.get(\"{arg.name}\", None)"
        if type(arg.type) is ClassDescriptor:
            entry = f"{arg.type}.from_dict({entry})"
        body += f"{INDENT*2}{arg.name} = {entry}\n"
        ret.append(arg.name)

    if FACTORY_MODE == FactoryMode.factory:
        arg_type = "Dict"
    elif FACTORY_MODE == FactoryMode.safe_factory:
        arg_type = "Union[Dict, None]"

    ret = ", ".join(ret)
    ret = f"{INDENT*2}return {descriptor}({ret})"
    return f"{INDENT}@staticmethod\n{INDENT}def from_dict(d: {arg_type}) -> '{descriptor}':\n{body}\n{ret}\n"


def represent_descriptor(descriptor: ClassDescriptor) -> str:
    inner_classes = []
    args = ""
    for arg in descriptor.args:
        if type(arg.type) is str:
            args += f"{INDENT}{arg}\n"
        elif type(arg.type) is ClassDescriptor:
            args += f"{INDENT}{arg}\n"
            inner_classes.insert(0, represent_descriptor(arg.type))
    if len(inner_classes) > 0:
        inner = "\n\n".join(inner_classes) + "\n\n"
    else:
        inner = ""

    from_dict = generate_factory(descriptor)
    if from_dict:
        from_dict = f"\n{from_dict}"

    return f"{inner}@dataclass\nclass {descriptor}:\n{args}{from_dict}"


def evaluate_descriptor(descriptor: ClassDescriptor, into: str):
    content = "from dataclasses import dataclass\n"
    if has_list_arg(descriptor):
        content += "from typing import List\n"
    if FACTORY_MODE == FactoryMode.factory:
        content += "from typing import Dict\n"
    if FACTORY_MODE == FactoryMode.safe_factory:
        content += "from typing import Dict, Union\n"
    content += "\n\n"
    content += represent_descriptor(descriptor).strip(" ")

    with open(into, "w") as file:
        file.write(content)


def main(toml_path: str, out_path: str, name: str):
    with open(toml_path, "r") as file:
        content = toml.load(file)

    descriptor = process_object(name, content)
    evaluate_descriptor(descriptor, out_path)


if __name__ == "__main__":
    parser = setup_args()
    args = parser.parse_args()
    toml_path = args.toml
    out_path = args.out
    if args.name is not None:
        name = args.name
    else:
        name = "config"

    if args.factory:
        FACTORY_MODE = FactoryMode.factory

    if args.factory and args.safe:
        FACTORY_MODE = FactoryMode.safe_factory

    main(toml_path, out_path, name)
