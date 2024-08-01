import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.cm as cm
import networkx as nx
import matplotlib.colors as mcolors
import snowflake.snowpark.functions as F

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
    fig, ax = plt.subplots(1, 3, figsize=(10, 5))

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
    plt.figure(figsize=(8, 3))

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


# Function to draw lineage information from Snowflake
def plot_lineage(df):
    df = df.with_column('SOURCE_NAME', F.split(F.col('SOURCE_OBJECT')['name'].cast('string'),F.lit('.'))[2].cast('string'))
    df = df.with_column('SOURCE_CATEGORY', F.col('SOURCE_OBJECT')['domain'].cast('string'))
    df = df.with_column('TARGET_NAME', F.split(F.col('TARGET_OBJECT')['name'].cast('string'),F.lit('.'))[2].cast('string'))
    df = df.with_column('TARGET_CATEGORY', F.col('TARGET_OBJECT')['domain'].cast('string'))
    df = df[['SOURCE_NAME','TARGET_NAME','SOURCE_CATEGORY','TARGET_CATEGORY','DISTANCE']]
    df = df.to_pandas()

    root_node = df.iloc[0]['TARGET_NAME']

    # Create a directed graph
    G = nx.DiGraph()
    
    # Add edges to the graph (reversed direction)
    for _, row in df.iterrows():
        G.add_edge(row['TARGET_NAME'], row['SOURCE_NAME'])
        G.nodes[row['SOURCE_NAME']]['category'] = row['SOURCE_CATEGORY']
        G.nodes[row['TARGET_NAME']]['category'] = row['TARGET_CATEGORY']
    
    # Define your categories
    categories = ['MODEL', 'DATASET', 'TABLE', 'FEATURE_VIEW', 'VIEW']
    
    # Define a colormap using matplotlib's colormap function
    colormap = plt.get_cmap('Set2')
    
    # Generate colors programmatically for each category
    color_map = {category: colormap(i / len(categories)) for i, category in enumerate(categories)}
    
    # Assign colors to nodes
    node_colors = [color_map[G.nodes[node]['category']] for node in G.nodes]
    
    def custom_layout(G, root, horizontal_spacing=2):
        levels = {}
        for node in G.nodes:
            try:
                levels[node] = nx.shortest_path_length(G, source=root, target=node)
            except nx.NetworkXNoPath:
                levels[node] = float('inf')
            
        pos = {}
        current_level = 0
        max_level = max(level for level in levels.values() if level != float('inf'))
        for level in range(max_level + 1):
            nodes_at_level = [node for node, lvl in levels.items() if lvl == level]
            num_nodes = len(nodes_at_level)
            for i, node in enumerate(nodes_at_level):
                pos[node] = ((max_level - current_level) * horizontal_spacing, i - num_nodes / 2)  # Reverse the horizontal position
            current_level += 1
        
        return pos
    
    # Define the layout for the nodes
    pos = custom_layout(G, root_node)

    # Function to draw rectangles around text with padding
    def draw_rectangles(pos, ax):
        padding = 0.1
        node_bbox = {}
        for node, (x, y) in pos.items():
            x = x * 0.8
            y = y * 0.8
            text = ax.text(x, y, node, fontsize=5, ha='center', va='center', color='black', zorder=2)
            bbox = text.get_window_extent(renderer=ax.get_figure().canvas.get_renderer())
            bbox = bbox.transformed(ax.transData.inverted())
            width = 1.2
            height = bbox.height + padding
            rect = plt.Rectangle((x - width / 2, y - height / 2), width, height, linewidth=0.1, edgecolor='black', facecolor=color_map[G.nodes[node]['category']], zorder=1)
            ax.add_patch(rect)
            node_bbox[node] = (x, y, width, height)
        return node_bbox
    
    # Function to draw edges with adjusted arrow positions
    def draw_edges_with_arrows(G, pos, ax, node_bbox):
        for edge in G.edges:
            end_node, start_node = edge
            start_x, start_y, start_width, start_height = node_bbox[start_node]
            end_x, end_y, end_width, end_height = node_bbox[end_node]
            
            # Adjust start and end points
            start_point = (start_x + start_width / 2, start_y)
            end_point = (end_x - end_width / 2, end_y)
            
            arrow = plt.arrow(start_point[0], start_point[1], end_point[0] - start_point[0], end_point[1] - start_point[1],
                              length_includes_head=True, head_width=0.02, head_length=0.02, fc='black', ec='black', zorder=0)
            ax.add_patch(arrow)
    
    # Draw the graph
    fig, ax = plt.subplots(figsize=(11, 6))
    node_bbox = draw_rectangles(pos, ax)
    draw_edges_with_arrows(G, pos, ax, node_bbox)
    
    # Add legend
    handles = [plt.Line2D([0], [0], marker='s', color='w', markerfacecolor=color_map[category], markersize=10, label=category) for category in categories]
    ax.legend(handles=handles, title="Categories", loc="best")
    
    # Show the plot
    plt.title("Lineage")
    plt.axis('off')
    return
