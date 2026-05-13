import random
import numpy as np

class Node:
    """Узел распределённой системы"""
    def __init__(self, node_id):
        self.id = node_id
        self.knows_failure = False   # знает ли узел об отказе


class BaseSimulator:
    """Базовый класс для всех симуляторов протоколов"""
    def __init__(self, num_nodes, interval, node_failures_percent):
        self.nodes = [Node(i) for i in range(num_nodes)]
        self.interval = interval           # интервал между раундами (сек)
        self.node_failures_percent = node_failures_percent
        self.failed_nodes = set()          # множество ID отказавших узлов
        self.bandwidth_usage = 0           # счётчик сообщений
        self.convergence_history = []      # история распространения

    def simulate_failure(self):
        """Случайно выбираем отказавшие узлы"""
        num_failures = int(len(self.nodes) * self.node_failures_percent / 100)
        if num_failures > 0:
            self.failed_nodes = set(random.sample(range(len(self.nodes)), num_failures))
        
        # Один живой узел узнаёт об отказе первым (источник информации)
        alive_nodes = [n for n in self.nodes if n.id not in self.failed_nodes]
        if alive_nodes:
            alive_nodes[0].knows_failure = True

    def detect_failures(self):
        """Этот метод будут переопределять дочерние классы"""
        pass

    def run_simulation(self, max_time=60):
        """Запуск симуляции до max_time секунд"""
        self.simulate_failure()
        first_knowledge_time = None
        all_knowledge_time = None
        
        current_time = 0
        
        while current_time < max_time:
            self.detect_failures()   # выполняем один раунд протокола
            
            alive_nodes = [n for n in self.nodes if n.id not in self.failed_nodes]
            nodes_knowing = [n for n in alive_nodes if n.knows_failure]
            
            # Запоминаем историю для графиков
            self.convergence_history.append({
                'time': current_time,
                'knowing': len(nodes_knowing),
                'total': len(alive_nodes)
            })
            
            if first_knowledge_time is None and len(nodes_knowing) > 0:
                first_knowledge_time = current_time
            
            if len(nodes_knowing) == len(alive_nodes):
                all_knowledge_time = current_time
                break
                
            current_time += self.interval
        
        return first_knowledge_time or 0, all_knowledge_time or max_time, self.bandwidth_usage
class SerfSimulator(BaseSimulator):
    """Gossip-протокол (как в Serf) — каждый узел сообщает случайным fanout соседям"""
    def __init__(self, num_nodes, gossip_interval, gossip_fanout, packet_loss_percent, node_failures_percent):
        super().__init__(num_nodes, gossip_interval, node_failures_percent)
        self.gossip_fanout = gossip_fanout
        self.packet_loss_percent = packet_loss_percent   # % потерь пакетов

    def detect_failures(self):
        for node in self.nodes:
            # Если узел живой и знает об отказе — распространяет информацию
            if node.id not in self.failed_nodes and node.knows_failure:
                # Выбираем живых соседей (не себя, не отказавших)
                candidates = [n for n in range(len(self.nodes)) 
                             if n != node.id and n not in self.failed_nodes]
                if not candidates:
                    continue
                
                # Выбираем fanout случайных соседей
                targets = random.sample(candidates, min(self.gossip_fanout, len(candidates)))
                
                for target_id in targets:
                    # Потеря пакета: если random() > packet_loss/100 — пакет дошёл
                    if random.random() > self.packet_loss_percent / 100.0:
                        self.nodes[target_id].knows_failure = True
                    self.bandwidth_usage += 1   # каждое отправленное сообщение


class HeartbeatSimulator(BaseSimulator):
    """Heartbeat (полносвязная) — каждый узел проверяет ВСЕХ остальных"""
    def detect_failures(self):
        for node in self.nodes:
            if node.id not in self.failed_nodes:
                for other in self.nodes:
                    if other.id != node.id:
                        # Если другой узел отказал — узнаём об этом
                        if other.id in self.failed_nodes:
                            node.knows_failure = True
                        self.bandwidth_usage += 1


class PingSimulator(BaseSimulator):
    """Ping (случайный опрос) — каждый узел пингует одного случайного соседа"""
    def detect_failures(self):
        for node in self.nodes:
            if node.id not in self.failed_nodes:
                # Выбираем случайного соседа (не себя)
                candidates = [n for n in range(len(self.nodes)) if n != node.id]
                if not candidates:
                    continue
                target_id = random.choice(candidates)
                
                # Если выбранный сосед отказал — узнаём об этом
                if target_id in self.failed_nodes:
                    node.knows_failure = True
                self.bandwidth_usage += 1
