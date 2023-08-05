from invoke import Collection, Program
from ez_cli import tasks

program = Program(namespace=Collection.from_module(tasks), version='0.3.0')
