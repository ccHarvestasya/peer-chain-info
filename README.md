# peer-chain-info

ピアノードのブロック高を取得する

# 準備

## SymbolSDK をインストール

```
pip install symbol-sdk-python
```

※本来は symbol-sdk-core-python だが、非推奨となっているため。

## CA プライベートキー生成

```
openssl genpkey -algorithm ed25519 -outform PEM -out ca.key.pem
```

## certtool をクローン

```
git clone https://github.com/symbol/symbol-node-configurator.git
```

### SymbolSDK 用に修正

`certtool.py`を編集

```diff
- from symbolchain.core.Network import NetworkLocator
- from symbolchain.core.PrivateKeyStorage import PrivateKeyStorage
- from symbolchain.core.symbol.KeyPair import KeyPair
- from symbolchain.core.symbol.Network import Network
+ from symbolchain.Network import NetworkLocator
+ from symbolchain.PrivateKeyStorage import PrivateKeyStorage
+ from symbolchain.symbol.KeyPair import KeyPair
+ from symbolchain.symbol.Network import Network
```

### Windows の場合

Windows の場合、パスに￥が含まれるため、￥をエスケープする。

```diff
def prepare_ca_config(ca_pem_path, ca_cn):
+    ca_pem_path_esc = str(ca_pem_path).replace("\\", "\\\\")
    with open('ca.cnf', 'wt', encoding='utf8') as output_file:
        output_file.write(f'''[ca]
default_ca = CA_default

[CA_default]
new_certs_dir = ./new_certs

database = index.txt
serial   = serial.dat
- private_key = {ca_pem_path}
+ private_key = {ca_pem_path_esc}
certificate = ca.crt.pem
policy = policy_catapult

```

## 証明書の生成

```
python symbol-node-configurator/certtool.py --working cert --name-ca "my cool CA" --name-node "my cool node name" --ca ca.key.pem
cat cert/node.crt.pem > cert/node.full.crt.pem
cat cert/ca.crt.pem >> cert/node.full.crt.pem
```

# 実行

```
python main.py dhealth03.harvestasya.com
```

## 通信ポート変更されている場合

第二引数にポート番号を指定

```
python main.py 03.symbol-node.com 7913
```

# 参考

- [Chatting with Peers for Fun and Profit - Symbol Blog](https://symbolblog.com/developer-guides/chatting-with-peers-for-fun-and-profit/)
