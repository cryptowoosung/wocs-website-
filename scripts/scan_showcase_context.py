"""
Scan wocs-common.css and report, for every line containing 'showcase',
which @media context (if any) it belongs to. Handles nested braces properly.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = os.path.join(ROOT, 'assets', 'css', 'wocs-common.css')

with open(CSS, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# media_stack[i] = (start_line, query, brace_depth_when_opened)
media_stack = []
brace_depth = 0

results = []

for i, line in enumerate(lines, 1):
    stripped = line.strip()

    # Process the line character by character to track braces
    # but first check if this line starts an @media rule.
    j = 0
    # Handle @media on this line
    if stripped.startswith('@media'):
        # The opening '{' may be on this line or on a later line
        query = stripped.split('{')[0].strip()
        # Track: media opens when its '{' is encountered
        # We'll push on seeing the '{' below, with the query
        pending_media_query = query
    else:
        pending_media_query = None

    # Walk through line chars to update brace_depth and pop media_stack
    for ch in line:
        if ch == '{':
            brace_depth += 1
            if pending_media_query is not None:
                media_stack.append((i, pending_media_query, brace_depth))
                pending_media_query = None
        elif ch == '}':
            # Pop any media that was opened at this depth
            while media_stack and media_stack[-1][2] == brace_depth:
                media_stack.pop()
            brace_depth -= 1

    # Now, for lines containing 'showcase', record the current media context
    if 'showcase' in line.lower():
        if media_stack:
            ctx = media_stack[-1][1]
        else:
            ctx = '(global - no @media)'
        results.append((i, ctx, stripped[:100]))

for i, ctx, text in results:
    print(f"L{i:4d} [{ctx[:40]:40}] {text}")
