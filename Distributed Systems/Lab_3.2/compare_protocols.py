from simulator import SerfSimulator, HeartbeatSimulator, PingSimulator
import numpy as np

def run_trials(protocol_class, num_nodes, interval, fanout, packet_loss, failures_percent, trials=5):
    first_times = []
    all_times = []
    bandwidths = []
    
    for _ in range(trials):
        if protocol_class == SerfSimulator:
            sim = protocol_class(num_nodes, interval, fanout, packet_loss, failures_percent)
        else:
            sim = protocol_class(num_nodes, interval, failures_percent)
        
        first, all_time, bw = sim.run_simulation(max_time=60)
        first_times.append(first)
        all_times.append(all_time)
        bandwidths.append(bw)
    
    return {
        'first_mean': np.mean(first_times),
        'first_std': np.std(first_times),
        'all_mean': np.mean(all_times),
        'all_std': np.std(all_times),
        'bw_mean': np.mean(bandwidths),
        'bw_std': np.std(bandwidths)
    }

NUM_NODES = 100
INTERVAL = 0.2
FANOUT = 3
PACKET_LOSS = 0
FAILURES = 5

print("="*60)
print("СРАВНЕНИЕ ПРОТОКОЛОВ ОБНАРУЖЕНИЯ ОТКАЗОВ")
print(f"Узлов: {NUM_NODES}, Отказов: {FAILURES}%, Интервал: {INTERVAL}с")
print("="*60)

print("\n🔵 SERF (GOSSIP)")
serf_res = run_trials(SerfSimulator, NUM_NODES, INTERVAL, FANOUT, PACKET_LOSS, FAILURES)
print(f"  Первое обнаружение: {serf_res['first_mean']:.2f} ± {serf_res['first_std']:.2f} сек")
print(f"  Полная конвергенция: {serf_res['all_mean']:.2f} ± {serf_res['all_std']:.2f} сек")
print(f"  Сообщений: {serf_res['bw_mean']:.0f} ± {serf_res['bw_std']:.0f}")

print("\n❤️ HEARTBEAT")
hb_res = run_trials(HeartbeatSimulator, NUM_NODES, INTERVAL, None, None, FAILURES)
print(f"  Первое обнаружение: {hb_res['first_mean']:.2f} ± {hb_res['first_std']:.2f} сек")
print(f"  Полная конвергенция: {hb_res['all_mean']:.2f} ± {hb_res['all_std']:.2f} сек")
print(f"  Сообщений: {hb_res['bw_mean']:.0f} ± {hb_res['bw_std']:.0f}")

print("\n🟢 PING")
ping_res = run_trials(PingSimulator, NUM_NODES, INTERVAL, None, None, FAILURES)
print(f"  Первое обнаружение: {ping_res['first_mean']:.2f} ± {ping_res['first_std']:.2f} сек")
print(f"  Полная конвергенция: {ping_res['all_mean']:.2f} ± {ping_res['all_std']:.2f} сек")
print(f"  Сообщений: {ping_res['bw_mean']:.0f} ± {ping_res['bw_std']:.0f}")
