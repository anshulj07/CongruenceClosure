import matplotlib.pyplot as plt
import networkx as nx
import io
import base64
import matplotlib
matplotlib.use('Agg')

def visualize_proof_forest(cc):
    G = nx.DiGraph()
    edge_labels = {}

    for child, (parent, reason) in cc.proof_forest.items():
        G.add_edge(parent, child)

        if isinstance(reason, dict):
            if reason.get("type") == "function":
                label = f"{cc.term_to_str(reason['arguments'][0])} = {cc.term_to_str(reason['arguments'][1])}"
            elif reason.get("type") == "derived":
                t1, t2 = reason['equiv']
                label = f"{t1} = {t2}"
            elif reason.get("type") == "interpreted":
                label = reason['rule']
            else:
                label = str(reason)
        else:
            label = str(reason)

        edge_labels[(parent, child)] = label

    if not G.edges:
        return None  # Nothing to show

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, node_size=1800, node_color='lightblue', font_size=9, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=8)
    plt.title("📘 Proof Forest", fontsize=14)
    plt.axis('off')

    # Save image to memory
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64

def export_proof_forest_dot(cc, output_path="proof_forest.dot"):
    G = nx.DiGraph()
    for child, (parent, reason) in cc.proof_forest.items():
        label = ""
        if isinstance(reason, dict):
            if reason.get("type") == "function":
                label = f"{cc.term_to_str(reason['arguments'][0])} = {cc.term_to_str(reason['arguments'][1])}"
            elif reason.get("type") == "derived":
                label = f"{reason['equiv'][0]} = {reason['equiv'][1]}"
            elif reason.get("type") == "interpreted":
                label = f"{reason['rule']}"
        G.add_edge(parent, child, label=label)
    nx.drawing.nx_pydot.write_dot(G, output_path)
    print(f"✅ DOT file saved: {output_path}")
