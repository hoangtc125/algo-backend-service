from typing import Dict
from tabulate import tabulate
from colorama import init, Fore, Style


def services_info():
    init(autoreset=True)
    table_data = [
        ["Prometheus", "http://localhost:9090"],
        ["Grafana", "http://localhost:3000"],
        ["RabbitMQ", "http://localhost:15672"],
        ["Redis", "http://localhost:6379"],
        ["Locust", "http://localhost:8089"],
        ["Server", "http://localhost:8001"],
    ]
    headers = [Fore.LIGHTGREEN_EX + "Service", Fore.LIGHTGREEN_EX + "URL"]
    table = tabulate(table_data, headers, tablefmt="fancy_grid")
    title = f"{Fore.CYAN}{Style.BRIGHT}Service URLs"
    print("\n" + title.center(50))
    print(table)


def server_info():
    init(autoreset=True)
    table_data = [
        ["Project", "Algo Thesis"],
        ["Author", "Tran Cong Hoang"],
        ["School", "Hanoi University of Science and Technology"],
        ["Outlook", "hoang.tc194060@sis.hust.edu.vn"],
        ["Contact", "0846303882"],
        ["Github", "https://github.com/hoangtc125"],
    ]
    headers = []
    table = tabulate(table_data, headers, tablefmt="fancy_grid")
    print(table)


def print_dict_as_table(data: Dict, title: str = None):
    headers = ["Key", "Value"]
    table_data = [[key, value] for key, value in data.items()]
    table = tabulate(table_data, headers, tablefmt="fancy_grid")
    title = f"{Fore.CYAN}{Style.BRIGHT}{title}"
    print("\n" + title.center(50))
    print(table)
