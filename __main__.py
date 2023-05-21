import toml
import argparse
from dataclasses import dataclass
from typing import Union, List


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
    return f"{inner}@dataclass\nclass {descriptor}:\n{args}"


def evaluate_descriptor(descriptor: ClassDescriptor, into: str):
    content = "from dataclasses import dataclass\n"
    if has_list_arg(descriptor):
        content += "from typing import List\n"
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

    main(toml_path, out_path, name)
