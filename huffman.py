"""
Code for compressing and decompressing using Huffman compression.
"""

from nodes import HuffmanNode, ReadNode


# ====================
# Helper functions for manipulating bytes


def get_bit(byte, bit_num):
    """ Return bit number bit_num from right in byte.
    @param int byte: a given byte
    @param int bit_num: a specific bit number within the byte
    @rtype: int
    >>> get_bit(0b00000101, 2)
    1
    >>> get_bit(0b00000101, 1)
    0
    """
    return (byte & (1 << bit_num)) >> bit_num


def byte_to_bits(byte):
    """ Return the representation of a byte as a string of bits.
    @param int byte: a given byte
    @rtype: str
    >>> byte_to_bits(14)
    '00001110'
    """
    return "".join([str(get_bit(byte, bit_num))
                    for bit_num in range(7, -1, -1)])


def bits_to_byte(bits):
    """ Return int represented by bits, padded on right.
    @param str bits: a string representation of some bits
    @rtype: int
    >>> bits_to_byte("00000101")
    5
    >>> bits_to_byte("101") == 0b10100000
    True
    """
    return sum([int(bits[pos]) << (7 - pos)
                for pos in range(len(bits))])


# ====================
# Functions for compression


def make_freq_dict(text):
    """ Return a dictionary that maps each byte in text to its frequency.
    @param bytes text: a bytes object
    @rtype: dict{int,int}
    >>> d = make_freq_dict(bytes([65, 66, 67, 66]))
    >>> d == {65: 1, 66: 2, 67: 1}
    True
    """
    dic = {}
    for char in text:
        if not char in dic.keys():
            dic[char] = 1
        else:
            dic[char] += 1
    return dic


def huffman_tree(freq_dict):
    """ Return the root HuffmanNode of a Huffman tree corresponding
    to frequency dictionary freq_dict.
    @param dict(int,int) freq_dict: a frequency dictionary
    @rtype: HuffmanNode
    >>> freq = {2: 6, 3: 4}
    >>> t = huffman_tree(freq)
    >>> result1 = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> result2 = HuffmanNode(None, HuffmanNode(2), HuffmanNode(3))
    >>> t == result1 or t == result2
    True
    """

    def find_biggest_key(keylist):
        """
        :param keylist: list of keys
        :return: key that holds largest value in freq_dict

        >>> find_biggest_key([2,3])
        2

        """
        if len(keylist) > 0:
            current_key = keylist[0]
        else:
            return
        for key in keylist:
            if freq_dict[key] > freq_dict[current_key]:
                current_key = key
        return current_key

    frequency = freq_dict.copy()
    key_list = list(frequency.keys())
    biggest_key = find_biggest_key(key_list)

    temp = []
    tree = HuffmanNode()

    while len(key_list) > 0:
        temp.append(biggest_key)
        del frequency[biggest_key]
        key_list.remove(biggest_key)
        biggest_key = find_biggest_key(key_list)
    # print('temp', temp)

    nodes_list = []
    while len(temp) > 0:
        nodes_list.append(HuffmanNode(temp.pop()))
    nodes_list.reverse()
    # print('nodeslist', nodes_list)

    while True:
        first_node = nodes_list.pop()
        if not nodes_list:
            return first_node
        second_node = nodes_list.pop()
        parent_node = HuffmanNode(None, first_node, second_node)
        nodes_list.insert(0, parent_node)


def get_codes(tree):
    """ Return a dict mapping symbols from tree rooted at HuffmanNode to codes.
    @param HuffmanNode tree: a Huffman tree rooted at node 'tree'
    @rtype: dict(int,str)

    >>> tree = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> d = get_codes(tree)
    >>> d == {3: "0", 2: "1"}
    True
    """

    d = {}
    # TODO GET RID OF THIS
    '''if tree.is_leaf():
        d[tree.symbol] = ''
    else:
        if tree.left:
            temp1 = get_codes(tree.left)
            for key in temp1.keys():
                temp1[key] = '0' + temp1[key]
            d.update(temp1)
        if tree.right:
            temp2 = get_codes(tree.right)
            for key in temp2.keys():
                temp2[key] = '1' + temp2[key]
            d.update(temp2)
    return d'''

    ##############
    if tree.is_leaf():
        return d

    if tree.left.is_leaf():
        d[tree.left.symbol] = '0'
    elif not tree.left.is_leaf():
        temp1 = get_codes(tree.left)
        for key in temp1.keys():
            temp1[key] = '0' + temp1[key]
        d.update(temp1)

    if tree.right.is_leaf():
        d[tree.right.symbol] = '1'
    elif not tree.right.is_leaf():
        temp2 = get_codes(tree.right)
        for key in temp2.keys():
            temp2[key] = '1' + temp2[key]
        d.update(temp2)

    return d


def number_nodes(tree):
    """ Number internal nodes in tree according to postorder traversal;
    start numbering at 0.
    @param HuffmanNode tree:  a Huffman tree rooted at node 'tree'
    @rtype: NoneType
    >>> left = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> right = HuffmanNode(None, HuffmanNode(9), HuffmanNode(10))
    >>> tree = HuffmanNode(None, left, right)
    >>> number_nodes(tree)
    >>> tree.left.number
    0
    >>> tree.right.number
    1
    >>> tree.number
    2
    """

    def traverse_node(node, x: 'int', max: 'int'):
        """
        :param node: HuffmanNode tree rooted at node 'tree'
        :param x: int assigning number to each internal node
        :param max: int assigning number to node 'tree'
        :return: None
        Helper function used to traverse tree
        and assign a number to each internal node

        >>> traverse_node(HuffmanNode(None,HuffmanNode(3),HuffmanNode(2)), 0,0)
        None

        """
        if not node:
            return
        node.number = x
        traverse_node(node.left, x, max)
        traverse_node(node.right, (x + 1), max)
        max += 1
        tree.number = max + 1

    return traverse_node(tree, 0, 0)


def avg_length(tree, freq_dict):
    """ Return the number of bits per symbol required to compress text
    made of the symbols and frequencies in freq_dict, using the Huffman tree.
    @param HuffmanNode tree: a Huffman tree rooted at node 'tree'
    @param dict(int,int) freq_dict: frequency dictionary
    @rtype: float
    >>> freq = {3: 2, 2: 7, 9: 1}
    >>> left = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> right = HuffmanNode(9)
    >>> tree = HuffmanNode(None, left, right)
    >>> avg_length(tree, freq)
    1.9
    """

    l = 0
    divisor = 0

    for key in freq_dict.keys():
        l += (len((get_codes(tree)[key])) * freq_dict[key])
        divisor += freq_dict[key]

    return l / divisor


def generate_compressed(text, codes):
    """ Return compressed form of text, using mapping in codes for each symbol.
    @param bytes text: a bytes object
    @param dict(int,str) codes: mappings from symbols to codes
    @rtype: bytes
    >>> d = {0: "0", 1: "10", 2: "11"}
    >>> text = bytes([1, 2, 1, 0])
    >>> result = generate_compressed(text, d)
    >>> [byte_to_bits(byte) for byte in result]
    ['10111000']
    >>> text = bytes([1, 2, 1, 0, 2])
    >>> result = generate_compressed(text, d)
    >>> [byte_to_bits(byte) for byte in result]
    ['10111001', '10000000']
    """
    byte = ''
    for i in text:
        byte += codes[i]
    if len(byte) < 8:
        return [int(bits_to_byte(byte))]
    else:
        lst = []
        length = (len(byte) % 8) + 2
        for i in range(1, length):
            lst.append(bits_to_byte(byte[:8 * i]))
            byte = byte[8 * i:]
        return lst


def tree_to_bytes(tree):
    """ Return a bytes representation of the tree rooted at tree.
    @param HuffmanNode tree: a Huffman tree rooted at node 'tree'
    @rtype: bytes
    The representation should be based on the postorder traversal of tree
    internal nodes, starting from 0.
    Precondition: tree has its nodes numbered.
    >>> tree = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> number_nodes(tree)
    >>> list(tree_to_bytes(tree))
    [0, 3, 0, 2]
    >>> left = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> right = HuffmanNode(5)
    >>> tree = HuffmanNode(None, left, right)
    >>> number_nodes(tree)
    >>> list(tree_to_bytes(tree))
    [0, 3, 0, 2, 1, 0, 0, 5]
    """

    lst = []

    def traverse_tree(node):
        """
        Helper function used to traverse through tree
        and append 0/1 to list if a node is a leaf or not
        :param node: HuffmanNode tree
        :return: none

        """
        if not node:
            return
        if node.left and node.left.is_leaf():
            lst.append(0)
            lst.append(node.left.symbol)
        else:
            traverse_tree(node.left)
        if node.right and node.right.is_leaf():
            lst.append(0)
            lst.append(node.right.symbol)
        else:
            traverse_tree(node.right)
        if not node.is_leaf():
            lst.append(1)
            lst.append(node.number)

    traverse_tree(tree)
    return bytes(lst[:-2])


def num_nodes_to_bytes(tree):
    """ Return number of nodes required to represent tree (the root of a
    numbered Huffman tree).
    @param HuffmanNode tree: a Huffman tree rooted at node 'tree'
    @rtype: bytes
    """
    return bytes([tree.number + 1])


def size_to_bytes(size):
    """ Return the size as a bytes object.
    @param int size: a 32-bit integer that we want to convert to bytes
    @rtype: bytes
    >>> list(size_to_bytes(300))
    [44, 1, 0, 0]
    """
    # little-endian representation of 32-bit (4-byte)
    # int size
    return size.to_bytes(4, "little")


def compress(in_file, out_file):
    """ Compress contents of in_file and store results in out_file.
    @param str in_file: input file whose contents we want to compress
    @param str out_file: output file, where we store our compressed result
    @rtype: NoneType
    """
    with open(in_file, "rb") as f1:
        text = f1.read()
    freq = make_freq_dict(text)
    tree = huffman_tree(freq)
    codes = get_codes(tree)
    number_nodes(tree)
    # TODO: DELETE THESE AFTERWARDS
    print(text)
    print(freq)
    print(tree)
    print(codes)
    ####
    print("Bits per symbol:", avg_length(tree, freq))
    result = (num_nodes_to_bytes(tree) + tree_to_bytes(tree) +
              size_to_bytes(len(text)))
    result += generate_compressed(text, codes)
    with open(out_file, "wb") as f2:
        f2.write(result)
        print("Writing: Completed\n {}".format(result))


# ====================
# Functions for decompression


def generate_tree_general(node_lst, root_index):
    """ Return the root of the Huffman tree corresponding
    to node_lst[root_index].
    The function assumes nothing about the order of the nodes in the list.
    @param list[ReadNode] node_lst: a list of ReadNode objects
    @param int root_index: index in the node list
    @rtype: HuffmanNode
    >>> lst = [ReadNode(0, 5, 0, 7), ReadNode(0, 10, 0, 12), \
    ReadNode(1, 1, 1, 0)]
    >>> generate_tree_general(lst, 2)
    HuffmanNode(None, HuffmanNode(None, HuffmanNode(10, None, None), \
    HuffmanNode(12, None, None)), \
    HuffmanNode(None, HuffmanNode(5, None, None), HuffmanNode(7, None, None)))
    """

    tree = HuffmanNode()
    if len(node_lst) == 1:
        tree.left = HuffmanNode(node_lst[0].l_data)
        tree.right = HuffmanNode(node_lst[0].r_data)
        return tree

    rn = node_lst[root_index]

    if rn.l_type == 1:
        if rn.l_data == 1:
            tree.right = generate_tree_general([node_lst[0]], root_index)
        else:
            tree.left = generate_tree_general([node_lst[1]], root_index)
    else:
        tree.left = HuffmanNode(rn.l_data)

    if rn.r_type == 1:
        if rn.r_data == 1:
            tree.right = generate_tree_general([node_lst[0]], root_index)
        else:
            tree.left = generate_tree_general([node_lst[1]], root_index)
    else:
        tree.right = HuffmanNode(rn.r_data)

    return tree


def generate_tree_postorder(node_lst, root_index):
    """Return the root of the Huffman tree corresponding
    to node_lst[root_index].
    The function assumes that the list represents a tree in postorder.
    @param list[ReadNode] node_lst: a list of ReadNode objects
    @param int root_index: index in the node list
    @rtype: HuffmanNode
    >>> lst = [ReadNode(0, 5, 0, 7), ReadNode(0, 10, 0, 12), \
    ReadNode(1, 0, 1, 0)]
    >>> generate_tree_postorder(lst, 2)
    HuffmanNode(None, HuffmanNode(None, HuffmanNode(5, None, None), \
    HuffmanNode(7, None, None)), \
    HuffmanNode(None, HuffmanNode(10, None, None), HuffmanNode(12, None, None)))
    """

    tree = HuffmanNode()
    if len(node_lst) == 1:
        tree.left = HuffmanNode(node_lst[0].l_data)
        tree.right = HuffmanNode(node_lst[0].r_data)
        return tree

    rn = node_lst[root_index]

    if rn.l_type == 1:
        if rn.l_data == 0:
            tree.right = generate_tree_general([node_lst[1]], root_index)
        else:
            tree.left = generate_tree_general([node_lst[0]], root_index)
    else:
        tree.left = HuffmanNode(rn.l_data)

    if rn.r_type == 1:
        if rn.r_data == 1:
            tree.right = generate_tree_general([node_lst[1]], root_index)
        else:
            tree.left = generate_tree_general([node_lst[0]], root_index)
    else:
        tree.right = HuffmanNode(rn.r_data)

    return tree


def generate_uncompressed(tree, text, size):
    """ Use Huffman tree to decompress size bytes from text.
    @param HuffmanNode tree: a HuffmanNode tree rooted at 'tree'
    @param bytes text: text to decompress
    @param int size: how many bytes to decompress from text.
    @rtype: bytes



    """

    # todo


def bytes_to_nodes(buf):
    """ Return a list of ReadNodes corresponding to the bytes in buf.
    @param bytes buf: a bytes object
    @rtype: list[ReadNode]
    >>> bytes_to_nodes(bytes([0, 1, 0, 2]))
    [ReadNode(0, 1, 0, 2)]
    """
    lst = []
    for i in range(0, len(buf), 4):
        l_type = buf[i]
        l_data = buf[i + 1]
        r_type = buf[i + 2]
        r_data = buf[i + 3]
        lst.append(ReadNode(l_type, l_data, r_type, r_data))
    return lst


def bytes_to_size(buf):
    """ Return the size corresponding to the
    given 4-byte little-endian representation.
    @param bytes buf: a bytes object
    @rtype: int
    >>> bytes_to_size(bytes([44, 1, 0, 0]))
    300
    """
    return int.from_bytes(buf, "little")


def uncompress(in_file, out_file):
    """ Uncompress contents of in_file and store results in out_file.
    @param str in_file: input file to uncompress
    @param str out_file: output file that will hold the uncompressed results
    @rtype: NoneType
    """
    with open(in_file, "rb") as f:
        num_nodes = f.read(1)[0]
        buf = f.read(num_nodes * 4)
        node_lst = bytes_to_nodes(buf)
        # use generate_tree_general or generate_tree_postorder here
        tree = generate_tree_general(node_lst, num_nodes - 1)
        size = bytes_to_size(f.read(4))
        with open(out_file, "wb") as g:
            text = f.read()
            g.write(generate_uncompressed(tree, text, size))


# ====================
# Other functions

def improve_tree(tree, freq_dict):
    """ Improve the tree as much as possible, without changing its shape,
    by swapping nodes. The improvements are with respect to freq_dict.
    @param HuffmanNode tree: Huffman tree rooted at 'tree'
    @param dict(int,int) freq_dict: frequency dictionary
    @rtype: NoneType
    >>> left = HuffmanNode(None, HuffmanNode(99), HuffmanNode(100))
    >>> right = HuffmanNode(None, HuffmanNode(101), \
    HuffmanNode(None, HuffmanNode(97), HuffmanNode(98)))
    >>> tree = HuffmanNode(None, left, right)
    >>> freq = {97: 26, 98: 23, 99: 20, 100: 16, 101: 15}
    >>> improve_tree(tree, freq)
    >>> avg_length(tree, freq)
    2.31
    """
    # todo


if __name__ == "__main__":
    import python_ta

    python_ta.check_all(config="huffman_pyta.txt")
    # TODO: Uncomment these when you have implemented all the functions
    import doctest

    doctest.testmod()

    import time

    d = {0: 600138, 1: 680, 2: 21121, 3: 5942, 4: 1955, 5: 30, 6: 221, 7: 3377, 11: 2, 16: 360, 17: 1179, 18: 1,
         19: 433, 20: 1, 21: 8, 23: 381, 24: 14, 32: 21939, 33: 2, 34: 60436, 35: 13604, 36: 1, 38: 104, 39: 5218,
         40: 6, 48: 5430, 49: 366, 50: 14448, 51: 53810, 55: 21381, 56: 98, 64: 1612, 65: 1, 66: 4, 68: 13799, 69: 41,
         70: 1686, 71: 548, 72: 4, 77: 1, 79: 1, 80: 12, 81: 7, 84: 19, 85: 36, 86: 1, 87: 43, 88: 3, 96: 364, 98: 139,
         100: 1589, 101: 1, 102: 20517, 103: 1297, 104: 33, 110: 765, 112: 3545, 113: 163, 114: 5557, 115: 21654,
         116: 482, 117: 42, 118: 1317, 119: 168432, 120: 5004, 126: 50, 127: 66, 128: 30, 130: 13, 131: 39, 132: 1,
         134: 12, 135: 5282, 136: 108417, 142: 28, 143: 2761, 184: 1, 192: 3, 196: 1, 230: 647, 231: 31, 232: 122,
         238: 43679, 239: 2, 247: 48, 248: 2788, 255: 22516}
    a = huffman_tree(d)
    print(a)
    '''
    mode = input("Press c to compress or u to uncompress: ")
    if mode == "c":
        fname = input("File to compress: ")
        start = time.time()
        compress(fname, fname + ".huf")
        print("compressed {} in {} seconds."
              .format(fname, time.time() - start))
    elif mode == "u":
        fname = input("File to uncompress: ")
        start = time.time()
        uncompress(fname, fname + ".orig")
        print("uncompressed {} in {} seconds."
              .format(fname, time.time() - start))'''
