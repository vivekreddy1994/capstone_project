import matplotlib.pyplot as plt
import pandas as pd

class Reporting:
    def __init__(self, model_results):
        self.model_results = model_results

    def generate_summary(self):
        summary = {
            'Mean Absolute Error': self.model_results['mae'].mean(),
            'Mean Squared Error': self.model_results['mse'].mean(),
            'R-squared': self.model_results['r2'].mean()
        }
        return summary

    def plot_results(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.model_results['actual'], label='Actual', color='blue')
        plt.plot(self.model_results['predicted'], label='Predicted', color='orange')
        plt.title('Actual vs Predicted')
        plt.xlabel('Index')
        plt.ylabel('Values')
        plt.legend()
        plt.grid()
        plt.show()

    def save_report(self, summary, file_path='report.txt'):
        with open(file_path, 'w') as f:
            for key, value in summary.items():
                f.write(f"{key}: {value}\n")