"""
VECTIS Code Analyzer - SciTools Understand 代替ツール
=====================================================
Pythonの ast モジュールを使用してソースコードを静的解析し、
クラス継承・関数呼び出し・import依存をMermaidとGraphviz形式で可視化する。
"""

import ast
import os
import json
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class FunctionInfo:
    """関数の詳細情報"""
    name: str
    module: str
    class_name: Optional[str]
    lineno: int
    end_lineno: Optional[int]
    args: List[str]
    calls: List[str]  # 呼び出している関数名
    complexity: int = 1  # 循環的複雑度
    decorators: List[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    """クラスの詳細情報"""
    name: str
    module: str
    lineno: int
    bases: List[str]
    methods: List[str]
    attributes: List[str] = field(default_factory=list)


@dataclass
class ModuleInfo:
    """モジュール（ファイル）の詳細情報"""
    name: str
    filepath: str
    imports: List[str]
    classes: List[ClassInfo]
    functions: List[FunctionInfo]
    lines_of_code: int = 0


class DeepCodeAnalyzer(ast.NodeVisitor):
    """
    AST（抽象構文木）を深層解析するビジター。
    クラス定義、関数定義、Import、関数呼び出し、循環的複雑度を追跡する。
    """

    def __init__(self, module_name: str, filepath: str):
        self.module_name = module_name
        self.filepath = filepath
        self.classes: List[ClassInfo] = []
        self.functions: List[FunctionInfo] = []
        self.imports: List[str] = []
        self._current_class: Optional[str] = None
        self._current_function: Optional[FunctionInfo] = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{self._get_attr_chain(base)}")

        methods = []
        attrs = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                methods.append(item.name)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attrs.append(target.id)

        self.classes.append(ClassInfo(
            name=node.name,
            module=self.module_name,
            lineno=node.lineno,
            bases=bases,
            methods=methods,
            attributes=attrs
        ))

        old_class = self._current_class
        self._current_class = node.name
        self.generic_visit(node)
        self._current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._process_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._process_function(node)

    def _process_function(self, node) -> None:
        args = []
        for arg in node.args.args:
            args.append(arg.arg)

        decorators = []
        for d in node.decorator_list:
            if isinstance(d, ast.Name):
                decorators.append(d.id)
            elif isinstance(d, ast.Attribute):
                decorators.append(self._get_attr_chain(d))

        func_info = FunctionInfo(
            name=node.name,
            module=self.module_name,
            class_name=self._current_class,
            lineno=node.lineno,
            end_lineno=getattr(node, 'end_lineno', None),
            args=args,
            calls=[],
            complexity=self._calc_complexity(node),
            decorators=decorators
        )

        old_func = self._current_function
        self._current_function = func_info
        self.generic_visit(node)
        self._current_function = old_func

        self.functions.append(func_info)

    def visit_Call(self, node: ast.Call) -> None:
        if self._current_function:
            call_name = self._get_call_name(node)
            if call_name:
                self._current_function.calls.append(call_name)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)

    def _get_call_name(self, node: ast.Call) -> Optional[str]:
        func = node.func
        if isinstance(func, ast.Name):
            return func.id
        elif isinstance(func, ast.Attribute):
            return self._get_attr_chain(func)
        return None

    def _get_attr_chain(self, node: ast.Attribute) -> str:
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))

    def _calc_complexity(self, node) -> int:
        """循環的複雑度（Cyclomatic Complexity）を計算"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For,
                                  ast.ExceptHandler, ast.With,
                                  ast.Assert, ast.comprehension)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def get_module_info(self, source_code: str) -> ModuleInfo:
        return ModuleInfo(
            name=self.module_name,
            filepath=self.filepath,
            imports=self.imports,
            classes=self.classes,
            functions=self.functions,
            lines_of_code=len(source_code.splitlines())
        )


def analyze_file(filepath: str) -> Optional[ModuleInfo]:
    """単一ファイルを解析"""
    module_name = os.path.splitext(os.path.basename(filepath))[0]
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        analyzer = DeepCodeAnalyzer(module_name, filepath)
        analyzer.visit(tree)
        return analyzer.get_module_info(source)
    except Exception as e:
        print(f"[ERROR] Failed to parse {filepath}: {e}")
        return None


def analyze_directory(root_dir: str) -> List[ModuleInfo]:
    """ディレクトリを再帰的に解析"""
    modules = []
    for dirpath, _, filenames in os.walk(root_dir):
        # __pycache__, .venv, node_modules をスキップ
        if any(skip in dirpath for skip in ['__pycache__', '.venv', 'node_modules', '.git']):
            continue
        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            filepath = os.path.join(dirpath, filename)
            info = analyze_file(filepath)
            if info:
                modules.append(info)
    return modules


# ================================================================
# 出力フォーマット生成
# ================================================================

def generate_mermaid_class_diagram(modules: List[ModuleInfo]) -> str:
    """Mermaid.js クラス図を生成"""
    lines = ["classDiagram"]

    for mod in modules:
        for cls in mod.classes:
            qualified = f"{mod.name}__{cls.name}"
            # クラス定義
            lines.append(f"    class {qualified} {{")
            for attr in cls.attributes:
                lines.append(f"        +{attr}")
            for method in cls.methods:
                lines.append(f"        +{method}()")
            lines.append("    }")
            # 継承関係
            for base in cls.bases:
                lines.append(f"    {base} <|-- {qualified} : inherits")

    return "\n".join(lines)


def generate_mermaid_dependency_graph(modules: List[ModuleInfo]) -> str:
    """Mermaid.js 依存関係グラフを生成"""
    lines = ["flowchart LR"]
    seen = set()

    for mod in modules:
        for imp in mod.imports:
            edge = (mod.name, imp)
            if edge not in seen:
                seen.add(edge)
                lines.append(f"    {mod.name} --> {imp}")

    return "\n".join(lines)


def generate_mermaid_call_graph(modules: List[ModuleInfo]) -> str:
    """Mermaid.js コールグラフを生成"""
    lines = ["flowchart TD"]
    seen = set()

    for mod in modules:
        for func in mod.functions:
            caller = f"{mod.name}.{func.name}" if not func.class_name else f"{mod.name}.{func.class_name}.{func.name}"
            for call in func.calls:
                edge = (caller, call)
                if edge not in seen:
                    seen.add(edge)
                    safe_caller = caller.replace(".", "_")
                    safe_call = call.replace(".", "_")
                    lines.append(f'    {safe_caller}["{caller}"] --> {safe_call}["{call}"]')

    return "\n".join(lines)


def generate_metrics_report(modules: List[ModuleInfo]) -> str:
    """コードメトリクスレポートを生成"""
    lines = ["# Code Metrics Report", ""]

    total_loc = 0
    total_classes = 0
    total_functions = 0
    high_complexity = []

    for mod in modules:
        total_loc += mod.lines_of_code
        total_classes += len(mod.classes)
        total_functions += len(mod.functions)

        for func in mod.functions:
            if func.complexity > 5:
                qualified = f"{mod.name}.{func.class_name}.{func.name}" if func.class_name else f"{mod.name}.{func.name}"
                high_complexity.append((qualified, func.complexity, func.lineno))

    lines.append("## Summary")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Files | {len(modules)} |")
    lines.append(f"| Total Lines of Code | {total_loc} |")
    lines.append(f"| Total Classes | {total_classes} |")
    lines.append(f"| Total Functions | {total_functions} |")
    lines.append("")

    if high_complexity:
        lines.append("## ⚠️ High Complexity Functions (Cyclomatic > 5)")
        lines.append(f"| Function | Complexity | Line |")
        lines.append(f"|----------|-----------|------|")
        for name, complexity, lineno in sorted(high_complexity, key=lambda x: -x[1]):
            lines.append(f"| `{name}` | {complexity} | L{lineno} |")
        lines.append("")

    # Module詳細
    lines.append("## Module Details")
    for mod in modules:
        lines.append(f"### `{mod.name}` ({mod.lines_of_code} lines)")
        if mod.classes:
            lines.append(f"- Classes: {', '.join(c.name for c in mod.classes)}")
        if mod.functions:
            lines.append(f"- Functions: {len(mod.functions)}")
        if mod.imports:
            lines.append(f"- Imports: {', '.join(mod.imports[:10])}{'...' if len(mod.imports) > 10 else ''}")
        lines.append("")

    return "\n".join(lines)


def generate_full_report(target_dir: str, output_dir: str = None) -> dict:
    """完全な解析レポートを生成"""
    if output_dir is None:
        output_dir = os.path.join(target_dir, "_analysis_output")
    os.makedirs(output_dir, exist_ok=True)

    print(f"[ANALYZER] Scanning: {os.path.abspath(target_dir)}")
    modules = analyze_directory(target_dir)
    print(f"[ANALYZER] Found {len(modules)} Python files")

    # 各種出力
    class_diagram = generate_mermaid_class_diagram(modules)
    dep_graph = generate_mermaid_dependency_graph(modules)
    call_graph = generate_mermaid_call_graph(modules)
    metrics = generate_metrics_report(modules)

    # ファイル書き出し
    with open(os.path.join(output_dir, "class_diagram.mmd"), "w", encoding="utf-8") as f:
        f.write(class_diagram)
    with open(os.path.join(output_dir, "dependency_graph.mmd"), "w", encoding="utf-8") as f:
        f.write(dep_graph)
    with open(os.path.join(output_dir, "call_graph.mmd"), "w", encoding="utf-8") as f:
        f.write(call_graph)
    with open(os.path.join(output_dir, "metrics_report.md"), "w", encoding="utf-8") as f:
        f.write(metrics)

    # JSON形式の生データ
    raw_data = []
    for mod in modules:
        mod_dict = {
            "name": mod.name,
            "filepath": mod.filepath,
            "lines_of_code": mod.lines_of_code,
            "imports": mod.imports,
            "classes": [asdict(c) for c in mod.classes],
            "functions": [asdict(f) for f in mod.functions]
        }
        raw_data.append(mod_dict)

    with open(os.path.join(output_dir, "analysis_data.json"), "w", encoding="utf-8") as f:
        json.dump(raw_data, f, indent=2, ensure_ascii=False)

    print(f"[ANALYZER] Reports saved to: {output_dir}")

    # HTMLレポート生成
    generate_html_report(output_dir, class_diagram, dep_graph, call_graph, metrics)

    return {
        "modules": len(modules),
        "output_dir": output_dir,
        "class_diagram": class_diagram,
        "dependency_graph": dep_graph,
        "call_graph": call_graph,
        "metrics": metrics
    }


def generate_html_report(output_dir, class_diagram, dep_graph, call_graph, metrics):
    """インタラクティブなHTMLレポートを生成"""
    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VECTIS Code Analysis Report</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #f4f4f4; }}
        header {{ background: #2c3e50; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }}
        .container {{ display: flex; height: calc(100vh - 60px); }}
        .sidebar {{ width: 250px; background: #34495e; color: white; padding: 1rem; }}
        .sidebar button {{ display: block; width: 100%; padding: 10px; margin-bottom: 5px; background: none; border: none; color: #bdc3c7; text-align: left; cursor: pointer; transition: 0.3s; }}
        .sidebar button:hover, .sidebar button.active {{ background: #2c3e50; color: white; border-left: 4px solid #3498db; }}
        .content {{ flex: 1; padding: 2rem; overflow: auto; background: white; }}
        .view-section {{ display: none; }}
        .view-section.active {{ display: block; }}
        h2 {{ border-bottom: 2px solid #eee; padding-bottom: 0.5rem; color: #2c3e50; }}
        pre.mermaid {{ background: #f9f9f9; padding: 20px; border-radius: 5px; border: 1px solid #ddd; overflow: auto; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .metric-card {{ background: #fff; padding: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 1rem; }}
    </style>
</head>
<body>
    <header>
        <div style="font-size: 1.2rem; font-weight: bold;">VECTIS CODE ANALYZER</div>
        <div style="font-size: 0.8rem;">Generated by Antigravity</div>
    </header>
    <div class="container">
        <div class="sidebar">
            <button onclick="switchView('overview')" class="active" id="btn-overview">📊 Overview & Metrics</button>
            <button onclick="switchView('callgraph')" id="btn-callgraph">🔗 Call Graph</button>
            <button onclick="switchView('classdiagram')" id="btn-classdiagram">📦 Class Diagram</button>
            <button onclick="switchView('dependency')" id="btn-dependency">🕸 Dependency Graph</button>
        </div>
        <div class="content">
            <!-- Overview -->
            <div id="overview" class="view-section active">
                <div id="metrics-content">Loading...</div>
            </div>

            <!-- Call Graph -->
            <div id="callgraph" class="view-section">
                <h2>Call Graph</h2>
                <p>Function calling relationships.</p>
                <div class="mermaid">
{call_graph}
                </div>
            </div>

            <!-- Class Diagram -->
            <div id="classdiagram" class="view-section">
                <h2>Class Diagram</h2>
                <p>Class inheritance and structure.</p>
                <div class="mermaid">
{class_diagram}
                </div>
            </div>

            <!-- Dependency Graph -->
            <div id="dependency" class="view-section">
                <h2>Dependency Graph</h2>
                <p>Module import dependencies.</p>
                <div class="mermaid">
{dep_graph}
                </div>
            </div>
        </div>
    </div>

    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});

        function switchView(id) {{
            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            
            document.querySelectorAll('.sidebar button').forEach(el => el.classList.remove('active'));
            document.getElementById('btn-' + id).classList.add('active');
        }}

        // Parse Metrics Markdown
        const metricsMd = `{metrics.replace('`', '\`').replace('{', '{{').replace('}', '}}')}`;
        document.getElementById('metrics-content').innerHTML = marked.parse(metricsMd);
    </script>
</body>
</html>"""
    
    with open(os.path.join(output_dir, "report.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[HTML] Generated interactive report: {os.path.join(output_dir, 'report.html')}")

    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    generate_full_report(target)
