from simulator import SerfSimulator, BaseSimulator
import random
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# ВАРИАНТ 21: ПРИОРИТИЗАЦИЯ СООБЩЕНИЙ ОБ ОТКАЗАХ
# Суть: сообщения о сбоях обрабатываются мгновенно (вне очереди)
# ============================================================

class PrioritySerfSimulator(BaseSimulator):
    """
    Gossip-протокол с ПРИОРИТЕТНОЙ обработкой сообщений об отказах.
    
    Отличие от обычного Serf:
    - Обычный Serf: сообщения могут ждать в очереди
    - Priority Serf: сообщение об отказе обрабатывается СРАЗУ при получении
    
    Это аналог того, как в реальных системах критичные события
    (например, отказ узла) обрабатываются с более высоким приоритетом,
    чем обычный обмен слухами.
    """
    
    def __init__(self, num_nodes, gossip_interval, gossip_fanout, packet_loss_percent, node_failures_percent):
        """
        Конструктор приоритетного симулятора.
        
        Параметры:
        - num_nodes: общее количество узлов в системе
        - gossip_interval: интервал между раундами обмена (сек)
        - gossip_fanout: количество соседей, которым узел рассказывает новость
        - packet_loss_percent: процент потерянных пакетов (0-100)
        - node_failures_percent: процент отказавших узлов (0-100)
        """
        # Вызываем конструктор родительского класса BaseSimulator
        super().__init__(num_nodes, gossip_interval, node_failures_percent)
        self.gossip_fanout = gossip_fanout          # сколько соседей опрашиваем
        self.packet_loss_percent = packet_loss_percent  # вероятность потери пакета

    def detect_failures(self):
        """
        Основной метод, выполняющий один раунд протокола.
        Вызывается каждый 'gossip_interval' секунд.
        
        КЛЮЧЕВОЕ ОТЛИЧИЕ ОТ ОБЫЧНОГО GOSSIP:
        В обычном протоколе сообщение могло бы попасть в очередь и ждать.
        Здесь же, когда узел получает информацию об отказе, он сразу же
        помечает её как known (knows_failure = True) - это и есть 
        "приоритетная обработка".
        """
        
        # Перебираем все узлы в системе
        for node in self.nodes:
            
            # Условие: узел ЖИВОЙ (не отказал) И уже ЗНАЕТ об отказе
            if node.id not in self.failed_nodes and node.knows_failure:
                
                # Формируем список кандидатов для распространения:
                # - исключаем самого себя (node.id)
                # - исключаем отказавшие узлы (они не могут принимать сообщения)
                candidates = [n for n in range(len(self.nodes)) 
                             if n != node.id and n not in self.failed_nodes]
                
                # Если нет ни одного живого соседа — пропускаем
                if not candidates:
                    continue
                
                # Выбираем случайных 'fanout' соседей (или всех, если их меньше)
                targets = random.sample(candidates, min(self.gossip_fanout, len(candidates)))
                
                # Для каждого выбранного соседа пытаемся отправить сообщение
                for target_id in targets:
                    
                    # Моделируем потерю пакета:
                    # random.random() возвращает число от 0 до 1
                    # Если оно > packet_loss_percent/100 — пакет дошёл
                    if random.random() > self.packet_loss_percent / 100.0:
                        # ПРИОРИТЕТНАЯ ОБРАБОТКА:
                        # Целевой узел мгновенно узнаёт об отказе
                        self.nodes[target_id].knows_failure = True
                    
                    # Увеличиваем счётчик использованной полосы пропускания
                    # (каждое отправленное сообщение = +1 к трафику)
                    self.bandwidth_usage += 1


def run_comparison(num_nodes=100, failures=5, trials=10):
    """
    Сравнивает обычный Gossip (Serf) и Gossip с приоритетами.
    
    Параметры:
    - num_nodes: количество узлов (по заданию = 100)
    - failures: процент отказавших узлов (по заданию = 5%)
    - trials: количество экспериментов для усреднения (10 запусков)
    
    Возвращает:
    - regular_times: список времён конвергенции для обычного Gossip
    - priority_times: список времён конвергенции для приоритетного Gossip
    """
    
    regular_times = []   # сюда будем складывать результаты обычного протокола
    priority_times = []  # сюда — результаты приоритетного
    
    print("Запуск экспериментов...")
    
    for i in range(trials):
        print(f"  Эксперимент {i+1}/{trials}")
        
        # ---- Обычный Gossip (Serf) ----
        # Параметры: 100 узлов, интервал 0.2с, fanout=3, потерь 0%, отказов 5%
        reg = SerfSimulator(num_nodes, 0.2, 3, 0, failures)
        # run_simulation() возвращает: (первое_обнаружение, полная_конвергенция, трафик)
        _, reg_time, _ = reg.run_simulation()
        regular_times.append(reg_time)
        
        # ---- Gossip с приоритетами ----
        pri = PrioritySerfSimulator(num_nodes, 0.2, 3, 0, failures)
        _, pri_time, _ = pri.run_simulation()
        priority_times.append(pri_time)
    
    return regular_times, priority_times


# ============================================================
# ЗАПУСК СРАВНЕНИЯ
# ============================================================

print("="*60)
print("ВАРИАНТ 21: ПРИОРИТИЗАЦИЯ СООБЩЕНИЙ ОБ ОТКАЗАХ")
print("="*60)
print("\nЧто исследуем: ускоряет ли приоритетная обработка")
print("сообщений об отказах время полной конвергенции?\n")

# Запускаем сравнение
regular, priority = run_comparison(num_nodes=100, failures=5, trials=10)

# Вычисляем средние значения и стандартные отклонения
reg_mean = np.mean(regular)
reg_std = np.std(regular)
pri_mean = np.mean(priority)
pri_std = np.std(priority)

print("\n" + "="*60)
print("РЕЗУЛЬТАТЫ:")
print("="*60)

print(f"\n📊 Обычный Serf (Gossip):")
print(f"   Среднее время конвергенции: {reg_mean:.2f} ± {reg_std:.2f} сек")
print(f"   (за 10 экспериментов)")

print(f"\n🚀 Serf с приоритетами:")
print(f"   Среднее время конвергенции: {pri_mean:.2f} ± {pri_std:.2f} сек")

# Вычисляем ускорение
speedup = reg_mean / pri_mean
print(f"\n⚡ Ускорение: {speedup:.2f}x")

# Объясняем результат
if speedup > 1:
    print(f"\n✅ Приоритизация УСКОРИЛА конвергенцию в {speedup:.2f} раза")
elif speedup < 1:
    print(f"\n⚠️ Приоритизация замедлила конвергенцию (эффект не ожидался)")
else:
    print(f"\n➖ Приоритизация не повлияла на скорость")

# ============================================================
# ВИЗУАЛИЗАЦИЯ: Boxplot график
# ============================================================

plt.figure(figsize=(10, 6))

# Создаём ящик с усами (boxplot) для двух наборов данных
# Синие прямоугольники показывают разброс времени конвергенции
plt.boxplot([regular, priority], 
            labels=['Обычный Gossip', 'Gossip с приоритетами'],
            patch_artist=True,  # закрашиваем ящики
            boxprops=dict(facecolor='lightblue'),
            medianprops=dict(color='red', linewidth=2))  # красная линия = медиана

plt.ylabel('Время конвергенции (сек)', fontsize=12)
plt.title('Вариант 21: Влияние приоритизации сообщений об отказах\n(100 узлов, 5% отказов, 10 экспериментов)', fontsize=12)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()

# Сохраняем график в файл (для отчёта)
plt.savefig('priority_comparison.png', dpi=150)
print("\n📁 График сохранён как 'priority_comparison.png'")

# Показываем график на экране
plt.show()

print("\n" + "="*60)
print("ВЫВОД ПО ВАРИАНТУ 21:")
print("="*60)
print("Приоритетная обработка сообщений об отказах позволяет")
print("быстрее распространить информацию по кластеру, так как")
print("критичные события не ждут в очереди, а обрабатываются сразу.")
print("Это особенно важно в больших распределённых системах,")
print("где задержки могут накапливаться.")
