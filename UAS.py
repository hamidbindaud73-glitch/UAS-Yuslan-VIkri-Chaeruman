import streamlit as st
import heapq

class BSTNode:
    def __init__(self, key, name):
        self.key = key
        self.name = name
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None
    def insert(self, key, name):
        if not self.root:
            self.root = BSTNode(key, name)
        else:
            self._insert(self.root, key, name)
    def _insert(self, node, key, name):
        if key < node.key:
            if not node.left: node.left = BSTNode(key, name)
            else: self._insert(node.left, key, name)
        else:
            if not node.right: node.right = BSTNode(key, name)
            else: self._insert(node.right, key, name)
    def inorder(self):
        res = []
        self._inorder(self.root, res)
        return res
    def _inorder(self, node, res):
        if node:
            self._inorder(node.left, res)
            res.append(f"Zona {node.key}")
            self._inorder(node.right, res)

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
    def search_prefix(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return self._get_words(node, prefix)
    def _get_words(self, node, prefix):
        res = []
        if node.is_end: res.append(prefix)
        for char, next_node in node.children.items():
            res.extend(self._get_words(next_node, prefix + char))
        return res

class Graph:
    def __init__(self):
        self.adj = {}
        self.directed_adj = {} 
        
    def add_directed(self, u, v, w):
        if u not in self.adj: self.adj[u] = []
        self.adj[u].append((v, w))

    def add_dependency(self, u, v):
        if u not in self.directed_adj: self.directed_adj[u] = []
        if v not in self.directed_adj: self.directed_adj[v] = []
        self.directed_adj[u].append(v)

    def dijkstra(self, start, end):
        dist = {k: float('inf') for k in self.adj}
        dist[start] = 0
        pq = [(0, start)]
        prev = {}
        while pq:
            d, u = heapq.heappop(pq)
            if u == end: break
            for v, w in self.adj.get(u, []):
                if dist[u] + w < dist.get(v, float('inf')):
                    dist[v] = dist[u] + w
                    prev[v] = u
                    heapq.heappush(pq, (dist[v], v))
        path = []
        curr = end
        while curr in prev:
            path.insert(0, curr)
            curr = prev[curr]
        if path: path.insert(0, start)
        return path, dist.get(end, float('inf'))

    def topo_sort(self):
        in_degree = {k: 0 for k in self.directed_adj}
        for u in self.directed_adj:
            for v in self.directed_adj[u]:
                in_degree[v] = in_degree.get(v, 0) + 1
        queue = [k for k in in_degree if in_degree[k] == 0]
        order = []
        while queue:
            u = queue.pop(0)
            order.append(u)
            for v in self.directed_adj.get(u, []):
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
        if len(order) != len(self.directed_adj):
            return None 
        return order

# --- INISIALISASI STATE (BACKEND LOGIC) ---
if 'queue' not in st.session_state: st.session_state.queue = []
if 'inventory' not in st.session_state: st.session_state.inventory = {}
if 'stack' not in st.session_state: st.session_state.stack = []
if 'bst' not in st.session_state: st.session_state.bst = BST()
if 'trie' not in st.session_state: st.session_state.trie = Trie()
if 'graph' not in st.session_state: st.session_state.graph = Graph()

# --- ANTARMUKA PENGGUNA (FRONTEND) ---
st.title('Suite Logistik Terintegrasi v2.0')

menu = st.sidebar.selectbox("Menu Utama", [
    "Operasional Gudang",
    "Manajemen Zona Rak",
    "Fitur Pencarian",
    "Rute & Prosedur",
    "Uji Sistem"
])

if menu == "Operasional Gudang":
    st.header("Operasional Gudang")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Gerbang Antrean (Queue)")
        truk = st.text_input("Nama Truk")
        barang = st.text_input("Nama Barang bawaan")
        jumlah = st.number_input("Jumlah", min_value=1, step=1)
        
        if st.button("ANTRE"):
            st.session_state.queue.append({'truk': truk, 'barang': barang, 'jumlah': jumlah})
            st.success(f"{truk} masuk antrean.")
            
        if st.button("PROSES"):
            data = st.session_state.queue.pop(0) 
            st.session_state.inventory[data['barang']] = {'jumlah': data['jumlah'], 'zona': None}
            st.session_state.trie.insert(data['barang'])
            st.session_state.stack.append(('tambah', data['barang']))
            st.success(f"{data['truk']} diproses. {data['barang']} otomatis masuk sistem.")

    with col2:
        st.subheader("Manajemen Stok (Hash Map)")
        brg_tambah = st.text_input("Nama Barang Baru")
        jml_tambah = st.number_input("Jumlah Stok", min_value=1, step=1)
        zona_id = st.number_input("ID Zona", min_value=1, step=1)
        
        if st.button("TAMBAH"):
            st.session_state.inventory[brg_tambah] = {'jumlah': jml_tambah, 'zona': zona_id}
            st.session_state.trie.insert(brg_tambah)
            st.session_state.stack.append(('tambah', brg_tambah))
            st.success(f"{brg_tambah} ditambahkan ke zona {zona_id}.")

        if st.button("BATAL"):
            aksi, nama_brg = st.session_state.stack.pop()
            del st.session_state.inventory[nama_brg]
            st.success("Aksi terakhir dibatalkan.")

elif menu == "Manajemen Zona Rak":
    st.header("Manajemen Zona Rak (BST)")
    z_id = st.number_input("ID Zona Baru", step=1)
    z_nama = st.text_input("Nama Zona")
    
    if st.button("TAMBAH_ZONA"):
        st.session_state.bst.insert(int(z_id), z_nama)
        st.success(f"Zona {z_id} ({z_nama}) ditambahkan ke BST.")
        
    if st.button("CETAK_ZONA"):
        urutan = st.session_state.bst.inorder()
        st.write(" -> ".join(urutan))

elif menu == "Fitur Pencarian":
    st.header("Pencarian (Trie)")
    prefix = st.text_input("Ketik awalan nama barang (Autocomplete):")
    if prefix:
        rekomendasi = st.session_state.trie.search_prefix(prefix)
        st.write("Rekomendasi:", rekomendasi)

    cari = st.text_input("Cari Barang Lengkap:")
    if st.button("CARI"):
        data = st.session_state.inventory[cari] 
        st.write(f"Ditemukan: {cari}, Jumlah: {data['jumlah']}, Zona: {data['zona']}")

elif menu == "Rute & Prosedur":
    st.header("Rute & Prosedur (Graph)")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Rute Distribusi")
        asal = st.text_input("Titik Asal")
        tujuan = st.text_input("Titik Tujuan")
        jarak = st.number_input("Jarak (Km)", min_value=1)
        
        if st.button("TAMBAH_RUTE"):
            st.session_state.graph.add_directed(asal, tujuan, jarak)
            st.success("Rute ditambahkan.")
            
        if st.button("RUTE_TERPENDEK"):
            path, dist = st.session_state.graph.dijkstra(asal, tujuan)
            st.write(f"Rute: {' -> '.join(path)}")
            st.write(f"Total Jarak: {dist} Km")

    with col2:
        st.subheader("Aturan Prosedur")
        proses_a = st.text_input("Proses A (Selesai sebelum B)")
        proses_b = st.text_input("Proses B")
        
        if st.button("TAMBAH_ATURAN"):
            st.session_state.graph.add_dependency(proses_a, proses_b)
            st.success("Aturan kerja ditambahkan.")
            
        if st.button("URUTAN_KERJA"):
            order = st.session_state.graph.topo_sort()
            if order is None:
                st.error("Error: Jadwal macet! Terjadi aturan yang saling mengunci/berputar pada sistem!")
            else:
                st.write(" -> ".join(order))

elif menu == "Uji Sistem":
    st.header("Uji Logika Mandiri")
    if st.button("JALANKAN_UJI"):
        test_bst = BST()
        for x in [50, 30, 70]: 
            test_bst.insert(x, f"Z{x}")
        if test_bst.inorder() == ['Zona 30', 'Zona 50', 'Zona 70']:
            st.success("UJI 1 (Validasi Urutan Pohon BST) : SUKSES")

        test_trie = Trie()
        test_trie.insert("BERAS")
        if test_trie.search_prefix("XYZ") == []:
            st.success("UJI 2 (Batas Kata Kosong pada Trie): SUKSES")

        test_graph = Graph()
        test_graph.add_dependency("A", "B")
        test_graph.add_dependency("B", "A")
        if test_graph.topo_sort() is None:
            st.success("UJI 3 (Deteksi Macet Alur Graf) : SUKSES")
