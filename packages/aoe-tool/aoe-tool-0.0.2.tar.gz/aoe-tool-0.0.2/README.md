# 安装依赖环境
`pip3 install pycrypto aoe-tool`
# 使用说明
### Samples:
1. encrypt SRC_FILE to ENCODED_FILE
`  atenc -e -f SRC_FILE -t ENCODED_FILE`
2. decrypt ENCODED_FILE to SRC_FILE
`  atenc -d -f ENCODED_FILE -t SRC_FILE`
### Options:
```
  -h, --help, show help document.
  -e, --encrypt, encrypt file mode.
  -d, --decrypt, decrypt file mode.
  -f <path>, --from <path>, specify the file path to encrypt/decrypt.
  -t <path>, --to <path>, specify the file path after encrypt/decrypt.
```
