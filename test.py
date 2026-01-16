from a2tree import QuadTree, QuadTreeNodeLeaf, QuadTreeNodeInternal

# Small 4x4 grayscale image
pixels = [
    [10, 10, 20, 20],
    [10, 10, 20, 20],
    [30, 30, 40, 40],
    [30, 30, 40, 40]
]

# Build tree with no compression
qt = QuadTree(loss_level=12
              )
qt.build_quad_tree(pixels)

# Check type of root node
print("Root type:", type(qt.root).__name__)

if isinstance(qt.root, QuadTreeNodeInternal):
    for i, child in enumerate(qt.root.children):
        print(f"Child {i} type: {type(child).__name__}")
        if isinstance(child, QuadTreeNodeLeaf):
            print(f"  → Leaf value: {child.value}")
        elif isinstance(child, QuadTreeNodeInternal):
            print(f"  → Internal node with 4 children")
