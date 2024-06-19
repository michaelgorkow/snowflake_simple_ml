import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.cm as cm

def plot_evidently_results(drift_detection_results):
    # Extracting summary data
    summary_data = drift_detection_results['summary']

    # Extracting test data
    test_data = pd.DataFrame(drift_detection_results['tests'])

    # Extracting feature drift data
    feature_drift = []
    for test in drift_detection_results['tests']:
        if 'parameters' in test and 'features' in test['parameters']:
            for feature, params in test['parameters']['features'].items():
                feature_drift.append({'feature': feature,
                                    'detected': params['detected'],
                                    'score': params['score'],
                                    'stattest': params['stattest'],
                                    'threshold': params['threshold']})

    feature_drift_df = pd.DataFrame(feature_drift)

    # Plotting
    fig, ax = plt.subplots(1, 3, figsize=(21, 6))

    # Summary plot
    ax[0].bar(summary_data['by_status'].keys(), summary_data['by_status'].values(), color=['red', 'green'])
    ax[0].set_title('Test Summary')
    ax[0].set_ylabel('Count')
    ax[0].set_xlabel('Status')

    # Drift scores bar plot
    feature_drift_df.plot(kind='bar', x='feature', y='score', ax=ax[1], color='skyblue')
    ax[1].set_title('Feature Drift Scores')
    ax[1].set_ylabel('Drift Score')
    ax[1].set_xlabel('Feature')

    # Pie chart for drifted features
    drifted_counts = feature_drift_df['detected'].value_counts()
    drifted_counts.plot(kind='pie', ax=ax[2], labels=['No Drift', 'Drift'], autopct='%1.1f%%', colors=['green', 'red'])
    ax[2].set_title('Proportion of Drifted Features')

    plt.tight_layout()
    plt.show()

def plot_model_metrics(model_metrics):
# Ensure 'created_on' column is of datetime type
    model_metrics['created_on'] = pd.to_datetime(model_metrics['created_on'])

    # Create a color map
    colors = cm.get_cmap('tab10', len(model_metrics))

    # Plotting the MAPE values on a time axis
    plt.figure(figsize=(10, 6))

    for i, row in model_metrics.iterrows():
        plt.plot(row['created_on'], row['MAPE'], marker='o', linestyle='-', color=colors(i), label=row['name'], markersize=10)

    # Formatting the x-axis to show the date and time
    date_format = DateFormatter("%Y-%m-%d %H:%M")
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.gcf().autofmt_xdate()  # Rotation for date labels

    plt.xlabel('Created On')
    plt.ylabel('MAPE')
    plt.title('MAPE Value Over Time')

    # Adding the legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='best')

    plt.grid(True)
    plt.tight_layout()

    # Display the plot
    plt.show()