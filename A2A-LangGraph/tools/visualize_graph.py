"""
LangGraph 시각화 도구
이 스크립트는 현재 실행 중인 LangGraph 에이전트들의 그래프 구조를 시각화합니다.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from agent import CurrencyAgent
import tempfile
import webbrowser

def visualize_currency_agent():
    """CurrencyAgent의 그래프 구조를 시각화합니다."""
    print("🎯 CurrencyAgent 그래프 생성 중...")
    
    try:
        # CurrencyAgent 인스턴스 생성
        agent = CurrencyAgent()
        
        # 그래프 구조를 mermaid 다이어그램으로 가져오기
        mermaid_code = agent.graph.get_graph().draw_mermaid()
        
        # HTML 파일 생성
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>CurrencyAgent LangGraph 시각화</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
</head>
<body>
    <h1>🤖 CurrencyAgent LangGraph 구조</h1>
    <div class="mermaid">
        {mermaid_code}
    </div>
    <script>
        mermaid.initialize({{startOnLoad: true}});
    </script>
</body>
</html>
        """
        
        # 임시 HTML 파일로 저장
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_path = f.name
        
        print(f"✅ 그래프가 생성되었습니다: {temp_path}")
        print("🌐 브라우저에서 여는 중...")
        
        # 기본 브라우저로 열기
        webbrowser.open(f'file://{temp_path}')
        
        return temp_path
        
    except Exception as e:
        print(f"❌ 그래프 생성 중 오류: {e}")
        return None

def print_graph_info():
    """그래프의 기본 정보를 출력합니다."""
    print("📊 LangGraph 정보:")
    print("=" * 50)
    
    try:
        agent = CurrencyAgent()
        graph = agent.graph.get_graph()
        
        print(f"🔗 노드 수: {len(graph.nodes)}")
        print(f"🔀 엣지 수: {len(graph.edges)}")
        print("\n📋 노드 목록:")
        for node in graph.nodes:
            print(f"  - {node}")
        
        print("\n🔄 엣지 목록:")
        for edge in graph.edges:
            print(f"  - {edge}")
            
    except Exception as e:
        print(f"❌ 그래프 정보 조회 중 오류: {e}")

if __name__ == "__main__":
    print("🎨 LangGraph 시각화 도구")
    print("=" * 50)
    
    # 그래프 기본 정보 출력
    print_graph_info()
    
    print("\n" + "=" * 50)
    
    # 그래프 시각화
    html_file = visualize_currency_agent()
    
    if html_file:
        print(f"\n💡 팁: 브라우저에서 그래프를 확인하세요!")
        print(f"📁 파일 위치: {html_file}")
    else:
        print("\n⚠️  그래프 시각화에 실패했습니다.")