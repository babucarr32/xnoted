from xnoted.config.manager import ConfigHandler
config = ConfigHandler()
if config:
    c = config.get()
    c.keybindings.global_.create_task

print()
