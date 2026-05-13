from simulator import SerfSimulator

# Параметры: 20 узлов, интервал 0.2с, fanout=2, потерь 0%, отказов 10%
sim = SerfSimulator(20, 0.2, 2, 0, 10)

first_time, all_time, bw = sim.run_simulation(max_time=30)

print(f"Первое обнаружение: {first_time} сек")
print(f"Полная конвергенция: {all_time} сек")
print(f"Сообщений отправлено: {bw}")
