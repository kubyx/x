from .files import copy_file
from .apps import open_app
from .registry import registry_action
from .services import service_action
from .media import media_action
from .menu import menu_action

def dispatch_system_action(action, params):
    if action == "dosya_kopyala":
        return copy_file(params)
    if action == "uygulama_ac":
        return open_app(params)
    if action == "registry":
        return registry_action(params)
    if action == "servis":
        return service_action(params)
    if action == "medya":
        return media_action(params)
    if action == "menu":
        return menu_action(params)
    return "Tanımsız veya desteklenmeyen işlem"
