[en](./ReadMe.md)

# TexTree

　ツリー形式のテキストで指定した通りにノードを作成する。

# 特徴

* python2,3に対応
* ノードに独自データを付与できる
* テキストとノードオブジェクトを相互変換できる

# 開発環境

* <time datetime="2019-12-26T10:00:00+0900">2019-12-26</time>
* [Raspbierry Pi](https://ja.wikipedia.org/wiki/Raspberry_Pi) 4 Model B Rev 1.2
* [Raspbian](https://ja.wikipedia.org/wiki/Raspbian) buster 10.0 2019-09-26 <small>[setup](http://ytyaru.hatenablog.com/entry/2019/12/25/222222)</small>
* bash 5.0.3(1)-release
* Python 2.7.16
* Python 3.7.3

# インストール

```sh
pip install textree
```

# 使い方

## 基礎

　テキストからノードオブジェクトへ変換する。

```python
import textree
tree_text = """
A
	A1
		A11
			A111
			A112
	A2
B
"""
tree = TexTree()
root = tree.to_node(tree_text)
print(root, root.Name)
for node in tree.Nodes:
    print(node.Line)
print(tree.to_text())
```

## リファレンス

　テキストとオブジェクトを相互変換する。

```python
root = tree.to_node(tree_text)
       tree.to_text()
```

　参照と代入。

```python
node.Name
node.Parent
node.Children
```
```python
node.Name = 'NewName'
node.Parent = Node('Parent')
node.Children.append(Node('Child'))
```

　移動。

```python
node.to_first()
node.to_last()
node.to_next()
node.to_prev()
```

　取得。

```python
Node.Path.select(root, 'A/A1/A11')
Node.Path.select(A, 'A1/A11')
```

　挿入・削除。

```python
node.insert_first(Node('new'))
node.insert_last(Node('new'))
node.insert_next(Node('new'))
node.insert_prev(Node('new'))
```
```python
node.delete()
```

　更新。

```python
node = Node.Path.select(root, 'A/A1/A11')
node.Name = 'UpdateName'
```

　他にも多数ある。詳細は[コード](./src/py3/textree.py)または[API一覧](./doc/memo/apis_py3.txt)を参照すること。

## 属性

　同一行に属性を付与できる。

```python
import textree
tree_text = """
A	attrA
	A1	attrA1
		A11	attrA11
			A111	attrA111
			A112	attrA112
	A2	attrA2
B	attrB
"""
tree = TexTree()
root = tree.to_node(tree_text)
print(root, root.Name)
for node in tree.Nodes:
    print(node.Name, node,Attr)
```

### RootNode

　RootNodeに属性を付与できる。

```python
import textree
tree_text = """
<ROOT>	root_attr
A	attrA
	A1	attrA1
		A11	attrA11
			A111	attrA111
			A112	attrA112
	A2	attrA2
B	attrB
"""
tree = TexTree()
root = tree.to_node(tree_text)
print(root, root.Name, root.Attr)
for node in tree.Nodes:
    print(node.Name, node,Attr)
```

### 属性のデシリアライズ

　ユーザは自由に属性を解析するコードを埋め込める。もちろんテキストへシリアライズするコードも書ける。

　以下のコードは、ノードに`my_name`を与える。

```python
class MyNodeDeserializer(NodeDeserializer):
    def deserialize(self, ana, parent, parents=Node):
        node = Node(ana.Line, parent=parent)
        node.my_name = 'My name is ' + node.Name
        return node
```
```python
tree = TexTree(node_deserializer=MyNodeDeserializer())
root = tree.to_node(tree_text)
for node in tree.Nodes:
    print(node.my_name)
```

```python
class MyNodeAttributeSerializer(NodeAttributeSerializer):
    def serialize(self, attr): return 'my_name=' + attr
```
```python
tree = TexTree(node_deserializer=MyNodeDeserializer(), node_serializer=NodeSerializer(MyNodeAttributeSerializer()))
root = tree.to_node(tree_text)
for node in tree.Nodes:
    print(node.my_name)
print(tree.to_text())
```

# 注意

* アルファ版である。インストール確認中

# 著者

　ytyaru

* [![github](http://www.google.com/s2/favicons?domain=github.com)](https://github.com/ytyaru "github")
* [![hatena](http://www.google.com/s2/favicons?domain=www.hatena.ne.jp)](http://ytyaru.hatenablog.com/ytyaru "hatena")
* [![mastodon](http://www.google.com/s2/favicons?domain=mstdn.jp)](https://mstdn.jp/web/accounts/233143 "mastdon")

# ライセンス

　このソフトウェアは[AGPLv3](https://www.gnu.org/licenses/agpl-3.0.ja.html)である。（GNU Affero General Public License v3）`agpl-3.0`

[![agpl-3.0](./doc/res/AGPLv3.svg "agpl-3.0")](https://www.gnu.org/licenses/agpl-3.0.ja.html)

