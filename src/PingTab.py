import re
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from src.CommandThread import CommandThread


class PingTab(QWidget):
    """Тестирует сетевое соединение путем посылки пакетов"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.command_thread = None
        self.G = nx.Graph()
        self.current_node = "127.0.0.1"
        self.target_node = None
        self.animation = None

    def setup_ui(self):
        layout = QVBoxLayout()

        self.ping_input = QLineEdit()
        self.ping_input.setPlaceholderText("Введите адрес для ping")
        self.ping_params = QLineEdit()
        self.ping_params.setPlaceholderText("Введите параметры (например, -n 4 -l 32)")
        self.ping_output = QTextEdit()
        self.ping_output.setReadOnly(True)
        self.ping_table = QTableWidget(0, 4)
        self.ping_table.setHorizontalHeaderLabels(["IP", "Байты", "Время", "TTL"])
        self.ping_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ping_button = QPushButton("Ping")
        self.ping_button.clicked.connect(self.perform_ping)
        self.stop_button = QPushButton("Остановить")
        self.stop_button.clicked.connect(self.stop_command)

        layout.addWidget(QLabel("Адрес для Ping:"))
        layout.addWidget(self.ping_input)
        layout.addWidget(QLabel("Параметры:"))
        layout.addWidget(self.ping_params)
        layout.addWidget(self.ping_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.ping_output)
        layout.addWidget(self.ping_table)

        self.setLayout(layout)

    def perform_ping(self):
        self.ping_output.clear()
        self.ping_table.setRowCount(0)
        target = self.ping_input.text() or "8.8.8.8"
        params = self.ping_params.text().strip()
        command = ["ping"] + params.split() + [target]
        self.target_node = target
        self.start_command_thread(command)
        self.visualize_packet_movement()

    def start_command_thread(self, command):
        """Запускает команду в отдельном потоке"""
        if self.command_thread is not None and self.command_thread.isRunning():
            self.stop_command()

        self.command_thread = CommandThread(command)
        self.command_thread.output_signal.connect(self.handle_output)
        self.command_thread.finished_signal.connect(lambda: self.finished_signal())
        self.command_thread.start()

    def finished_signal(self):
        self.ping_output.append("Команда завершена.")
        self.command_thread = None

    def handle_output(self, output):
        """Обрабатывает вывод и добавляет данные в таблицу"""
        self.ping_output.append(output)

        match = re.search(r"Ответ от (\d+\.\d+\.\d+\.\d+): число байт=(\d+) время[<>=](\d+мс) TTL=(\d+)", output)
        if match:
            ip, bytes_, time_, ttl = match.groups()
            row_position = self.ping_table.rowCount()
            self.ping_table.insertRow(row_position)
            self.ping_table.setItem(row_position, 0, QTableWidgetItem(ip))
            self.ping_table.setItem(row_position, 1, QTableWidgetItem(bytes_))
            self.ping_table.setItem(row_position, 2, QTableWidgetItem(time_))
            self.ping_table.setItem(row_position, 3, QTableWidgetItem(ttl))

    def visualize_packet_movement(self):
        """Визуализирует перемещение пакетов между узлами"""
        if not self.target_node:
            self.ping_output.append("Не указан целевой узел для ping.")
            return

        self.G.clear()
        self.G.add_node(self.current_node, pos=(0, 0))
        self.G.add_node(self.target_node, pos=(1, 0))
        self.G.add_edge(self.current_node, self.target_node)

        pos = nx.get_node_attributes(self.G, 'pos')

        fig, ax = plt.subplots(figsize=(6, 4))
        nx.draw(self.G, pos, with_labels=True, node_size=2000, node_color='lightblue', font_size=12, font_weight='bold', edge_color='gray')

        def update(num):
            ax.clear()
            nx.draw(self.G, pos, with_labels=True, node_size=2000, node_color='lightblue', font_size=12, font_weight='bold', edge_color='gray')

            packet_pos = (num / 50.0, 0)
            if self.command_thread is not None:
                ax.plot(*packet_pos, 'ro', markersize=10)

        self.animation = FuncAnimation(fig, update, frames=range(51), interval=20, repeat=True)

        plt.show()

    def stop_command(self):
        """Останавливает выполнение команды"""
        if self.command_thread is not None:
            self.command_thread.stop()
            self.command_thread.wait()
            self.command_thread = None
