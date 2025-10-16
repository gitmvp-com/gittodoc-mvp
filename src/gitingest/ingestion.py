"""Functions to ingest and analyze a codebase directory."""

from pathlib import Path
from typing import Tuple

from gitingest.config import MAX_DIRECTORY_DEPTH, MAX_FILES, MAX_TOTAL_SIZE_BYTES
from gitingest.query_parsing import IngestionQuery
from gitingest.schemas import FileSystemNode, FileSystemNodeType, FileSystemStats


def ingest_query(query: IngestionQuery) -> Tuple[str, str, str]:
    """Run the ingestion process for a parsed query."""
    
    path = query.local_path
    
    if not path.exists():
        raise ValueError(f"{query.slug} cannot be found")
    
    root_node = FileSystemNode(
        name=path.name,
        type=FileSystemNodeType.DIRECTORY,
        path_str=str(path.relative_to(query.local_path)),
        path=path,
    )
    
    stats = FileSystemStats()
    
    _process_node(
        node=root_node,
        query=query,
        stats=stats,
    )
    
    summary, tree, content = _format_output(root_node, query)
    
    return summary, tree, content


def _process_node(
    node: FileSystemNode,
    query: IngestionQuery,
    stats: FileSystemStats,
) -> None:
    """Process a directory node recursively."""
    
    if _limit_exceeded(stats, node.depth):
        return
    
    for sub_path in node.path.iterdir():
        # Skip .git directory
        if sub_path.name == ".git":
            continue
        
        if sub_path.is_symlink():
            child = FileSystemNode(
                name=sub_path.name,
                type=FileSystemNodeType.SYMLINK,
                path_str=str(sub_path.relative_to(query.local_path)),
                path=sub_path,
                depth=node.depth + 1,
            )
            stats.total_files += 1
            node.children.append(child)
            node.file_count += 1
        
        elif sub_path.is_file():
            file_size = sub_path.stat().st_size
            
            if file_size > query.max_file_size:
                continue
            
            if stats.total_size + file_size > MAX_TOTAL_SIZE_BYTES:
                continue
            
            stats.total_files += 1
            stats.total_size += file_size
            
            if stats.total_files > MAX_FILES:
                continue
            
            child = FileSystemNode(
                name=sub_path.name,
                type=FileSystemNodeType.FILE,
                size=file_size,
                file_count=1,
                path_str=str(sub_path.relative_to(query.local_path)),
                path=sub_path,
                depth=node.depth + 1,
            )
            
            node.children.append(child)
            node.size += file_size
            node.file_count += 1
        
        elif sub_path.is_dir():
            child_directory_node = FileSystemNode(
                name=sub_path.name,
                type=FileSystemNodeType.DIRECTORY,
                path_str=str(sub_path.relative_to(query.local_path)),
                path=sub_path,
                depth=node.depth + 1,
            )
            
            _process_node(
                node=child_directory_node,
                query=query,
                stats=stats,
            )
            
            node.children.append(child_directory_node)
            node.size += child_directory_node.size
            node.file_count += child_directory_node.file_count
            node.dir_count += 1 + child_directory_node.dir_count
    
    node.sort_children()


def _limit_exceeded(stats: FileSystemStats, depth: int) -> bool:
    """Check if any traversal limits have been exceeded."""
    
    if depth > MAX_DIRECTORY_DEPTH:
        return True
    
    if stats.total_files >= MAX_FILES:
        return True
    
    if stats.total_size >= MAX_TOTAL_SIZE_BYTES:
        return True
    
    return False


def _format_output(node: FileSystemNode, query: IngestionQuery) -> Tuple[str, str, str]:
    """Format the node tree into summary, tree, and content strings."""
    
    # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
    total_chars = sum(len(child.content or "") for child in _get_all_files(node))
    estimated_tokens = total_chars // 4
    
    # Summary
    summary = f"""Repository: {query.slug}
Files analyzed: {node.file_count}
Directories: {node.dir_count}
Total size: {node.size / 1024:.2f} KB
Estimated tokens: {estimated_tokens:,}
"""
    
    # Tree structure
    tree_lines = ["File Tree:"]
    tree_lines.append("")
    _build_tree_string(node, tree_lines, "")
    tree = "\n".join(tree_lines)
    
    # File contents
    content_lines = ["File Contents:"]
    content_lines.append("")
    for file_node in _get_all_files(node):
        content_lines.append(f"{'='*80}")
        content_lines.append(f"File: {file_node.path_str}")
        content_lines.append(f"{'='*80}")
        content_lines.append(file_node.content or "")
        content_lines.append("")
    
    content = "\n".join(content_lines)
    
    return summary, tree, content


def _build_tree_string(node: FileSystemNode, lines: list, prefix: str) -> None:
    """Recursively build tree structure string."""
    
    if node.depth == 0:
        lines.append(node.name + "/")
    
    for i, child in enumerate(node.children):
        is_last = i == len(node.children) - 1
        connector = "└── " if is_last else "├── "
        
        if child.type == FileSystemNodeType.DIRECTORY:
            lines.append(f"{prefix}{connector}{child.name}/")
            extension = "    " if is_last else "│   "
            _build_tree_string(child, lines, prefix + extension)
        else:
            lines.append(f"{prefix}{connector}{child.name}")


def _get_all_files(node: FileSystemNode) -> list:
    """Get all file nodes recursively."""
    files = []
    
    if node.type == FileSystemNodeType.FILE:
        return [node]
    
    for child in node.children:
        if child.type == FileSystemNodeType.FILE:
            files.append(child)
        elif child.type == FileSystemNodeType.DIRECTORY:
            files.extend(_get_all_files(child))
    
    return files
