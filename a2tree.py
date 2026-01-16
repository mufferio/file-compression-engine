from __future__ import annotations

import math
from copy import deepcopy

from typing import List, Tuple, Optional


# No other imports allowed


def mean_and_count(matrix: List[List[int]]) -> Tuple[float, int]:
    """
    Returns the average of the values in a 2D list
    Also returns the number of values in the list
    """
    total = 0
    count = 0
    for row in matrix:
        for v in row:
            total += v
            count += 1
    return total / count, count


def standard_deviation_and_mean(matrix: List[List[int]]) -> Tuple[float, float]:
    """
    Return the standard deviation and mean of the values in <matrix>

    https://en.wikipedia.org/wiki/Root-mean-square_deviation

    Note that the returned average is a float.
    It may need to be rounded to int when used.
    """
    avg, count = mean_and_count(matrix)
    total_square_error = 0
    for row in matrix:
        for v in row:
            total_square_error += ((v - avg) ** 2)
    return math.sqrt(total_square_error / count), avg


class QuadTreeNode:
    """
    Base class for a node in a quad tree
    """

    def __init__(self) -> None:
        pass

    def tree_size(self) -> int:
        """notimplemented"""
        raise NotImplementedError

    def convert_to_pixels(self, width: int, height: int) -> List[List[int]]:
        """notimplemented"""
        raise NotImplementedError

    def preorder(self) -> str:
        """notimplemented"""
        raise NotImplementedError


class QuadTreeNodeEmpty(QuadTreeNode):
    """
    An empty node represents an area with no pixels included
    """

    def __init__(self) -> None:
        super().__init__()

    def tree_size(self) -> int:
        """
        Note: An empty node still counts as 1 node in the quad tree
        """
        return 1

    def convert_to_pixels(self, width: int, height: int) -> List[List[int]]:
        """
        Convert to a properly formatted empty list
        """
        # Note: Normally, this method should return an empty list or a list of
        # empty lists. However, when the tree is mirrored, this returned list
        # might not be empty and may contain the value 255 in it. This will
        # cause the decompressed image to have unexpected white pixels.
        # You may ignore this caveat for the purpose of this assignment.
        return [[255] * width for _ in range(height)]

    def preorder(self) -> str:
        """
        The letter E represents an empty node
        """
        return 'E'


class QuadTreeNodeLeaf(QuadTreeNode):
    """
    A leaf node in the quad tree could be a single pixel or an area in which
    all pixels have the same colour (indicated by self.value).
    """

    value: int  # the colour value of the node

    def __init__(self, value: int) -> None:
        super().__init__()
        assert isinstance(value, int)
        self.value = value

    def tree_size(self) -> int:
        """
        Return the size of the subtree rooted at this node
        """
        return 1

    def convert_to_pixels(self, width: int, height: int) -> List[List[int]]:
        """
        Return the pixels represented by this node as a 2D list

        >>> sample_leaf = QuadTreeNodeLeaf(5)
        >>> sample_leaf.convert_to_pixels(2, 2)
        [[5, 5], [5, 5]]
        """
        return [[self.value] * width for _ in range(height)]

    def preorder(self) -> str:
        """
        A leaf node is represented by an integer value in the preorder string
        """
        return str(self.value)


class QuadTreeNodeInternal(QuadTreeNode):
    """
    An internal node is a non-leaf node, which represents an area that will be
    further divided into quadrants (self.children).

    The four quadrants must be ordered in the following way in self.children:
    bottom-left, bottom-right, top-left, top-right

    (List indices increase from left to right, bottom to top)

    Representation Invariant:
    - len(self.children) == 4
    """
    children: List[Optional[QuadTreeNode]]

    def __init__(self) -> None:
        """
        Order of children: bottom-left, bottom-right, top-left, top-right
        """
        super().__init__()

        # Length of self.children must be always 4.
        self.children = [None, None, None, None]

    def tree_size(self) -> int:
        """
        The size of the subtree rooted at this node.

        This method returns the number of nodes that are in this subtree,
        including the root node.
        """
        missing = [i for i, c in enumerate(self.children) if c is None]
        if missing:
            raise ValueError(f"Internal node missing children at {missing}")
        return 1 + sum(c.tree_size() for c in self.children)

    def convert_to_pixels(self, width: int, height: int) -> List[List[int]]:
        """
        Return the pixels represented by this node as a 2D list.

        You'll need to recursively get the pixels for the quadrants and
        combine them together.

        Make sure you get the sizes (width/height) of the quadrants correct!
        Read the docstring for split_quadrants() for more info.
        """
        bottom_height = height // 2
        top_height = height - bottom_height
        left_width = width // 2
        right_width = width - left_width
        b_l = self.children[0].convert_to_pixels(left_width, bottom_height)
        b_r = self.children[1].convert_to_pixels(right_width, bottom_height)
        t_l = self.children[2].convert_to_pixels(left_width, top_height)
        t_r = self.children[3].convert_to_pixels(right_width, top_height)
        final = []

        for r in range(bottom_height):
            final.append(b_l[r] + b_r[r])
        for r in range(top_height):
            final.append(t_l[r] + t_r[r])
        return final

    def preorder(self) -> str:
        """
        Return a string representing the preorder traversal or the tree rooted
        at this node. See the docstring of the preorder() method in the
        QuadTree class for more details.

        An internal node is represented by an empty string in the preorder
        string.
        """
        parts = [""]
        for child in self.children:
            parts.append(child.preorder())
        return ','.join(parts)

    def restore_from_preorder(self, lst: List[str], start: int) -> int:
        """
        Restore subtree from preorder list <lst>, starting at index <start>
        Return the number of entries used in the list to restore this subtree
        """
        if lst[start] != '':
            leaf = QuadTreeNodeLeaf(int(lst[start]))
            for i in range(4):
                self.children[i] = leaf
            return 1
        used = 1
        for i in range(4):
            token = lst[start + used]
            if token == '':
                node = QuadTreeNodeInternal()
                consumed = node.restore_from_preorder(lst, start + used)
                self.children[i] = node
                used += consumed
            elif token == 'E':
                self.children[i] = QuadTreeNodeEmpty()
                used += 1
            else:
                self.children[i] = QuadTreeNodeLeaf(int(token))
                used += 1
        return used

    def mirror(self) -> None:
        """
        Mirror the bottom half of the image represented by this tree over
        the top half

        Example:
            Original Image
            1 2
            3 4

            Mirrored Image
            3 4 (this row is flipped upside down)
            3 4

        See the assignment handout for a visual example.
        """
        bl = self.children[0]
        br = self.children[1]
        bl_copy = deepcopy(bl)
        br_copy = deepcopy(br)

        def flip_vert(node: QuadTreeNode) -> None:
            if not isinstance(node, QuadTreeNodeInternal):
                return
            (node.children[0],
             node.children[2]) = (node.children[2],
                                  node.children[0])
            (node.children[1],
             node.children[3]) = (node.children[3],
                                  node.children[1])
            for child in node.children:
                flip_vert(child)
        flip_vert(bl_copy)
        flip_vert(br_copy)
        self.children[2] = bl_copy
        self.children[3] = br_copy


class QuadTree:
    """
    The class for the overall quadtree
    """

    loss_level: float
    height: int
    width: int
    root: Optional[QuadTreeNode]  # safe to assume root is an internal node

    def __init__(self, loss_level: int = 0) -> None:
        """
        Precondition: the size of <pixels> is at least 1x1
        """
        self.loss_level = float(loss_level)
        self.height = -1
        self.width = -1
        self.root = None

    def build_quad_tree(self, pixels: List[List[int]],
                        mirror: bool = False) -> None:
        """
        Build a quad tree representing all pixels in <pixels>
        and assign its root to self.root

        <mirror> indicates whether the compressed image should be mirrored.
        See the assignment handout for examples of how mirroring works.
        """
        # print('building_quad_tree...')
        self.height = len(pixels)
        self.width = len(pixels[0])
        self.root = self._build_tree_helper(pixels)
        if mirror:
            self.root.mirror()
        return

    def _build_tree_helper(self, pixels: List[List[int]]) -> QuadTreeNode:
        """
        Build a quad tree representing all pixels in <pixels>
        and return the root

        Note that self.loss_level should affect the building of the tree.
        This method is where the compression happens.

        IMPORTANT: the condition for compressing a quadrant is the standard
        deviation being __LESS THAN OR EQUAL TO__ the loss level. You must
        implement this condition exactly; otherwise, you could fail some
        test cases unexpectedly.
        """
        if not pixels or not pixels[0]:
            return QuadTreeNodeEmpty()
        std, mean = standard_deviation_and_mean(pixels)
        if ((std <= self.loss_level)
                or (len(pixels) == 1
                    and len(pixels[0]) == 1)):
            return QuadTreeNodeLeaf(round(mean))
        node = QuadTreeNodeInternal()
        bl, br, tl, tr = self._split_quadrants(pixels)
        node.children[0] = self._build_tree_helper(bl)
        node.children[1] = self._build_tree_helper(br)
        node.children[2] = self._build_tree_helper(tl)
        node.children[3] = self._build_tree_helper(tr)
        return node

    @staticmethod
    def _split_quadrants(pixels: List[List[int]]) -> List[List[List[int]]]:
        """
        Precondition: size of <pixels> is at least 1x1
        Returns a list of four lists of lists, correspoding to the quadrants in
        the following order: bottom-left, bottom-right, top-left, top-right

        IMPORTANT: when dividing an odd number of entries, the smaller half
        must be the left half or the bottom half, i.e., the half with lower
        indices.

        Postcondition: the size of the returned list must be 4

        >>> example = QuadTree(0)
        >>> example._split_quadrants([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        [[[1]], [[2, 3]], [[4], [7]], [[5, 6], [8, 9]]]
        """
        height = len(pixels)
        width = len(pixels[0])
        row_mid = height // 2
        col_mid = width // 2
        bottom_half = pixels[:row_mid]
        top_half = pixels[row_mid:]
        bottom_left = [row[:col_mid] for row in bottom_half]
        bottom_right = [row[col_mid:] for row in bottom_half]
        top_left = [row[:col_mid] for row in top_half]
        top_right = [row[col_mid:] for row in top_half]
        return [bottom_left, bottom_right, top_left, top_right]

    def tree_size(self) -> int:
        """
        Return the number of nodes in the tree, including all Empty, Leaf, and
        Internal nodes.
        """
        return self.root.tree_size()

    def convert_to_pixels(self) -> List[List[int]]:
        """
        Return the pixels represented by this tree as a 2D matrix
        """
        return self.root.convert_to_pixels(self.width, self.height)

    def preorder(self) -> str:
        """
        return a string representing the preorder traversal of the quadtree.
        The string is a series of entries separated by comma (,).
        Each entry could be one of the following:
        - empty string '': represents a QuadTreeNodeInternal
        - string of an integer value such as '5': represents a QuadTreeNodeLeaf
        - string 'E': represents a QuadTreeNodeEmpty

        For example, consider the following tree with a root and its 4 children
                __      Root       __
              /      |       |        \
            Empty  Leaf(5), Leaf(8), Empty

        preorder() of this tree should return exactly this string: ",E,5,8,E"

        (Note the empty-string entry before the first comma)
        """
        return self.root.preorder()

    @staticmethod
    def restore_from_preorder(lst: List[str],
                              width: int, height: int) -> QuadTree:
        """
        Restore the quad tree from the preorder list <lst>
        The preorder list <lst> is the preorder string split by comma

        Precondition: the root of the tree must be an internal node (non-leaf)
        """
        tree = QuadTree()
        tree.width = width
        tree.height = height
        tree.root = QuadTreeNodeInternal()
        tree.root.restore_from_preorder(lst, 0)
        return tree


def maximum_loss(original: QuadTreeNode, compressed: QuadTreeNode) -> float:
    """
    Given an uncompressed image as a quad tree and the compressed version,
    return the maximum loss across all compressed quadrants.

    Precondition: original.tree_size() >= compressed.tree_size()

    Note: original, compressed are the root nodes (QuadTreeNode) of the
    trees, *not* QuadTree objects

    >>> pixels = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    >>> orig, comp = QuadTree(0), QuadTree(2)
    >>> orig.build_quad_tree(pixels)
    >>> comp.build_quad_tree(pixels)
    >>> maximum_loss(orig.root, comp.root)
    1.5811388300841898
    """
    def orig_stats(node: QuadTreeNode) -> Tuple[float, float, int]:
        if isinstance(node, QuadTreeNodeEmpty):
            return 0.0, 0.0, 0
        if isinstance(node, QuadTreeNodeLeaf):
            v = float(node.value)
            return v, v * v, 1
        total, squares, cnt = 0.0, 0.0, 0
        for child in node.children:
            s, sq, c = orig_stats(child)
            total += s
            squares += sq
            cnt += c
        return total, squares, cnt

    def helper(orig_node: QuadTreeNode, comp_node: QuadTreeNode) -> float:
        max_loss = 0.0
        if (isinstance(comp_node, QuadTreeNodeLeaf)
                and not isinstance(orig_node, QuadTreeNodeLeaf)):
            total, squares, cnt = orig_stats(orig_node)
            if cnt > 0:
                mean = total / cnt
                var = squares / cnt - mean * mean
                max_loss = math.sqrt(var) if var > 0 else 0.0
            return max_loss
        if (isinstance(comp_node, QuadTreeNodeInternal)
                and isinstance(orig_node, QuadTreeNodeInternal)):
            for i in range(4):
                loss_i = helper(orig_node.children[i], comp_node.children[i])
                if loss_i > max_loss:
                    max_loss = loss_i
        return max_loss
    return helper(original, compressed)


if __name__ == '__main__':
    import doctest

    doctest.testmod(verbose=True)

    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'doctest', 'math', 'copy', '__future__'
        ],
        'disable': ['E9955', 'E9951']
    })
