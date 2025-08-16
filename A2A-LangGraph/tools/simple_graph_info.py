"""
Simple LangGraph info viewer
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def main():
    print("LangGraph Analysis")
    print("=" * 50)
    
    try:
        from agent import CurrencyAgent
        
        print("Creating CurrencyAgent...")
        agent = CurrencyAgent()
        graph = agent.graph.get_graph()
        
        print(f"Nodes: {len(graph.nodes)}")
        print(f"Edges: {len(graph.edges)}")
        
        print("\nNode list:")
        for i, node in enumerate(graph.nodes, 1):
            print(f"  {i}. {node}")
        
        print("\nEdge list:")
        for i, edge in enumerate(graph.edges, 1):
            print(f"  {i}. {edge}")
            
        # Try to get mermaid diagram
        try:
            mermaid = graph.draw_mermaid()
            print("\nMermaid diagram:")
            print("-" * 30)
            print(mermaid)
            print("-" * 30)
        except Exception as e:
            print(f"Mermaid generation failed: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()