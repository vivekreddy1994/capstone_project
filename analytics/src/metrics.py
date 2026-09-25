def calculate_average(metrics):
    if not metrics:
        return 0
    return sum(metrics) / len(metrics)

def calculate_median(metrics):
    if not metrics:
        return 0
    sorted_metrics = sorted(metrics)
    mid = len(sorted_metrics) // 2
    if len(sorted_metrics) % 2 == 0:
        return (sorted_metrics[mid - 1] + sorted_metrics[mid]) / 2
    return sorted_metrics[mid]

def calculate_standard_deviation(metrics):
    if not metrics:
        return 0
    mean = calculate_average(metrics)
    variance = sum((x - mean) ** 2 for x in metrics) / len(metrics)
    return variance ** 0.5

def calculate_metrics(data):
    metrics = {
        'average': calculate_average(data),
        'median': calculate_median(data),
        'standard_deviation': calculate_standard_deviation(data)
    }
    return metrics


calculate_metric_1 = calculate_average
calculate_metric_2 = calculate_average